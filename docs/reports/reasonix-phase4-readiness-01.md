# Phase 4 — Pre-Launch Readiness Guard Note

Date: 2026-06-30  
Author: reasonix  
Branch: `agent/reasonix-phase4-readiness-01`  
Baseline: `codex-phase2-mainline-01` (current HEAD)  
Purpose: 盤點系統距離「初步上線」的必要缺口，分類 risk 邊界，凍結 Phase 4 上線前規則  

---

## Executive Summary

Phase 1–3 已完成契約凍結、核心 CRUD、maintenance schema、billing 流程、payment API、electricity/water 計算、reports、以及三條 integration（LINE/OCR/Sheets）的 skeleton 與 contract。然而**系統尚未準備好上線（production-ready）**。

本報告盤點 22 項缺口，分類為：

| Category | Count | Blocker? |
|----------|-------|----------|
| ✅ Direct items（可直接做） | 12 | 4 項為 blocker |
| ⚠️ ADR items（需先有 ADR） | 6 | 0 項為 blocker |
| ❌ Forbidden items（無論如何不可做） | 3 | — |
| **Total** | **22** | **4 blockers** |

### Blocker Summary（上線前必解）

| ID | Area | Why Blocker | Fix Type |
|----|------|-------------|----------|
| B1 | Auth — `role_required` 未套用任何 route | 無權限控管，landlord/viewer 可存取全部功能 | Direct |
| B2 | Config — `SECRET_KEY` production validation 會拋 error | Production 啟動會直接 crash | Direct |
| B3 | Migration — 無 Alembic/Flask-Migrate | 無法管理 schema 版本，production 無法安全更版 | ADR |
| B4 | Database — SQLite 非 production-safe | 無 concurrent write 保護、無 backup 策略、無 connection pool | ADR |

### Implementation Order Recommendation

```
Phase 4A (blockers) → B1, B2
Phase 4B (infra)    → B3, B4 + D1-D4 (config/monitoring)
Phase 4C (edge)     → D5-D12 + ADR items
Phase 4D (freeze)   → 確認無 regression，上線
```

---

## 1. Auth / Roles / Permissions

### 1.1 Current State

- `User.role` 支援 3 個角色：`admin` / `landlord` / `viewer`（預設 `viewer`）
- `role_required(*roles)` decorator 已在 `app/core/security/auth.py` 定義
- `admin_required` 是 `role_required("admin")` 的別名

**但：沒有任何 route 使用這些 decorator。**

所有 Blueprint 的 route 僅使用 `@login_required`（部分甚至無 auth check）。`role=viewer` 或 `role=landlord` 的使用者可存取 admin-only 功能（billing create/edit, electricity create, water post 等）。

### 1.2 Task Classification

#### ✅ Direct Items

| ID | Task | Rationale | Blocker? |
|----|------|-----------|----------|
| **B1** | **為每個 Blueprint 的寫入/管理 route 加上 `@admin_required`** | 上線前最小必要 security 修正 | 🔴 **YES** |
| D1 | 為 landlord 可見 route 加上 `@role_required("admin", "landlord")` 並依 `landlord_id` 過濾 | 跨房東資料不可見 | No |
| D2 | 確認 `viewer` 角色只能讀取 dashboard/reports 唯讀頁面 | 符合 auth-and-roles.md contract | No |

#### ⚠️ ADR Items

| ID | Task | Why ADR | Blocker? |
|----|------|---------|----------|
| A1 | 設計「landlord 只看自己資料」的完整過濾策略（repository 層 scope filter） | 需決定房東 scope 的查詢策略與測試覆蓋 | No |

#### ❌ Forbidden Items

| ID | Practice | Why |
|----|----------|-----|
| F1 | 在 production 使用 `viewer` 預設角色且不限制寫入權限 | 無異於開放匿名寫入 |

### 1.3 Route-Level Role Audit

| Module | Routes | Current Protection | Needed |
|--------|--------|-------------------|--------|
| `auth` | login, logout | None (login is public) | OK (public) |
| `dashboard` | dashboard_home | `@login_required` | `@admin_required` |
| `landlords` | list, create, edit, delete | `@login_required` | `@admin_required` |
| `properties` | list, create, edit, delete | `@login_required` | `@admin_required` |
| `rooms` | list, create, edit, delete | `@login_required` | `@admin_required` |
| `tenants` | list, create, edit, delete | `@login_required` | `@admin_required` |
| `contracts` | list, create, edit, terminate | `@login_required` | `@admin_required` |
| `billing` | create, edit, batch | `@login_required` | `@admin_required` |
| `electricity` | create reading/bill, calculate, post | `@login_required` | `@admin_required` |
| `water` | create, post, calculate | `@login_required` | `@admin_required` |
| `payments` | create, verify, reject, link | `@login_required` | `@admin_required` |
| `reports` | view, export | `@login_required` | OK (admin+landlord+viewer) |
| `maintenance` | create, assign, resolve, close | `@login_required` | `@admin_required` |

### 1.4 Risk Notes

- **R-A1**: `role=viewer` 在 production 不得看到 landlord 報表中的金額明細。需確認 template 層也有 role-based rendering。
- **R-A2**: `landlord_id` FK in User model 已存在，但 landlord scope 過濾還未在任何 repository 層實作。若先套 role decorator 但無 scope filter，landlord 可看到不屬於自己的資料（僅無法寫入）。

---

## 2. Payment / OCR / LINE / Export — Risk Boundaries

### 2.1 Current State

| Integration | Implementation | Status |
|-------------|---------------|--------|
| **LINE webhook** | Signature verified, events parsed + summarized, returns 200 | ✅ Route works, but **events are not stored** — no downstream processing |
| **OCR adapter** | `NoopOCRClient` (not configured) and `TextFileOCRClient` (dev-only) | ❌ No real OCR provider implemented |
| **Sheets export** | CSV + XLSX export via `CSVSheetsClient` / `XLSXSheetsClient` | ✅ Export works without external API |
| **Sheets import** | `import_sheet` defined in Protocol but **not implemented** | ❌ Requires Google Sheets API ADR |
| **Payment OCR flow** | `PaymentOCRService` exists but not wired to any route or event | ❌ Dead code path |

### 2.2 Task Classification

#### ✅ Direct Items

| ID | Task | Rationale | Blocker? |
|----|------|-----------|----------|
| D3 | LINE webhook: 將 accepted events 記錄到 log file 或 db audit log（不實作業務邏輯） | 避免事件被靜默丟棄，符合「events accepted but not lost」原則 | No |
| D4 | OCR: 整合至少一個 real OCR provider（Gemini Vision 或 Tesseract local） | OCRClientProtocol 已定義，僅需實作 concrete class | No |
| D5 | Payment: 確認 `PaymentOCRService` 是否預期被呼叫，否則標記為 deprecated | 避免 production 中 dead code 的混淆 | No |
| D6 | 為 LINE / OCR / Sheets 加上未設定時的 graceful startup check（只 log warning，不 crash） | 符合 Phase 3 contract「graceful degradation」 | No |

#### ⚠️ ADR Items

| ID | Task | Why ADR | Blocker? |
|----|------|---------|----------|
| A2 | LINE webhook 連接 payment 通知流程 | 會觸及 PaymentRecord 狀態機與 service boundary | No |
| A3 | OCR 辨識結果的 human review workflow | 新增 UI 流程，影響 record_status 狀態機 | No |
| A4 | Google Sheets API OAuth / service account 設置與 import 流程 | 外部 API 授權與安全審查 | No |

#### ❌ Forbidden Items

| ID | Practice | Why |
|----|----------|-----|
| F2 | LINE webhook 直接寫入 DB（PaymentRecord 或其他 model） | 違反 integrations-contract 「webhook 不直接寫核心業務邏輯」 |
| F3 | Production 中使用 `TextFileOCRClient`（從文字檔模擬 OCR） | Dev-only，production 會讀到不存在或不相關的檔案 |

### 2.3 Risk Notes

- **R-P1**: LINE webhook 目前回傳 200 但 events 未被 storage 接收。若 LINE 認為事件已送達（200），但系統未處理，事件永久遺失。R-D3 可緩解（至少 log）。
- **R-P2**: `PaymentOCRService` imports `PaymentService` 但未在任何 route/event handler 中被呼叫，屬於無作用的 code path。可能誤導 developer 認為 OCR 已整合。
- **R-P3**: Sheets import 完全未實作。若上線後需求突然出現，可能繞過 ADR 直接硬寫。

---

## 3. Migration / Repair — Production Forbidden Zone

### 3.1 Current State

| Script | Path | Writes? | Production Safe? |
|--------|------|---------|------------------|
| `maintenance_legacy_scan.py` | `scripts/migration/` | Read-only (scan only) | ✅ Safe |
| `migration_index.py` | `scripts/migration/` | Template write | ⚠️ Has write template |
| `_template_write_migration.py` | `scripts/migration/` | Template only | ⚠️ Template, not production code |
| `contract_expiry_repair.py` | `scripts/repair/` | Writes to DB | ❌ NOT safe for production |
| `room_status_audit.py` | `scripts/repair/` | Read-only (audit report) | ✅ Safe |
| `user_table_audit.py` | `scripts/repair/` | Read-only (audit report) | ✅ Safe |
| `year_month_audit.py` | `scripts/repair/` | Read-only (audit report) | ✅ Safe |

### 3.2 Task Classification

#### ✅ Direct Items

| ID | Task | Rationale | Blocker? |
|----|------|-----------|----------|
| D7 | 在所有 migration/repair script 的 header 加上「⚠️ PRODUCTION READ-ONLY LOCK — add --apply flag to write」註釋 | 防止誤執行寫入腳本 | No |
| D8 | `contract_expiry_repair.py` 必須加上乾執行（dry-run）模式與明確的 --apply flag | 避免 production DB 被未經確認的 repair 修改 | No |
| D9 | 將 `_template_write_migration.py` rename 為 `_write_template.py`（移除可能觸發 production 自動執行的命名誤解） | 命名混淆 | No |
| D10 | 建立 production migration SOP 文件（`docs/operations/migration-sop.md`） | 定義 migration 前/中/後步驟 | No |

#### ⚠️ ADR Items

| ID | Task | Why ADR | Blocker? |
|----|------|---------|----------|
| **B3** | **導入 Alembic / Flask-Migrate 作為正式 schema migration 工具** | 架構決策：需決定 migration 策略、版本控制、rollback 流程 | 🔴 **YES** |
| A5 | 為 migration/repair scripts 建立「production 執行許可」checklist | 非技術性流程決策 | No |

#### ❌ Forbidden Items

| ID | Practice | Why |
|----|----------|-----|
| — | (None beyond what Phases 1-3 already defined) | — |

### 3.3 Risk Notes

- **R-M1**: `contract_expiry_repair.py` 目前無 dry-run 模式，若在 production 環境被錯誤執行，contract 的 `status` 可能被大量誤改。D8 為必要防護。
- **R-M2**: 無 Alembic 意味著 schema 變更必須手動執行 SQL，production 上線後不可接受。B3 是 blocker。
- **R-M3**: `migration_index.py` 和 `_template_write_migration.py` 有 write template code，若被誤觸可能產生不完整的 migration 記錄。

---

## 4. Secrets / Config Management

### 4.1 Current State

| Aspect | Current | Severity |
|--------|---------|----------|
| `SECRET_KEY` | Default `"change-me-in-production"` — production validation WILL reject | 🔴 BLOCKER |
| LINE/OCR secrets | Read from env vars — good | ✅ Correct |
| SQLite in production | Warned in `validation.py` (`"SQLite is still in use"`) but NOT blocked | 🟡 WARNING |
| `SESSION_COOKIE_SECURE` | `True` in ProductionConfig | ✅ Correct |
| `PREFERRED_URL_SCHEME` | `"https"` in ProductionConfig | ✅ Correct |
| HTTPS termination | Not configured or documented | 🟡 MISSING |
| Env var documentation | No `.env.example` or required-vars list | 🟡 MISSING |

### 4.2 Task Classification

#### ✅ Direct Items

| ID | Task | Rationale | Blocker? |
|----|------|-----------|----------|
| **B2** | **Production 部署前必須設定唯一的 `SECRET_KEY` 環境變數** | Validation 會阻止 production 啟動 — 這是必要阻擋 | 🔴 **YES** |
| D11 | 建立 `.env.example` 列出所有必要的 env var 與說明 | 方便部署人員設定環境 | No |
| D12 | 在 startup log 中記錄 config validation 結果（非 blocking 的 warning） | 方便運維人員確認設定 | No |

#### ⚠️ ADR Items

| ID | Task | Why ADR | Blocker? |
|----|------|---------|----------|
| **B4** | **Migration from SQLite to PostgreSQL / MySQL 的 ADR** | 架構決策：SQLite 不支援 concurrent write，production 需正式 RDBMS | 🔴 **YES** |
| A6 | HTTPS termination 策略（reverse proxy vs Flask built-in） | 架構與部署決策 | No |

#### ❌ Forbidden Items

| ID | Practice | Why |
|----|----------|-----|
| — | (None beyond Phase 0 frozen "secrets only from env") | — |

### 4.3 Risk Notes

- **R-C1**: `validation.py` 在 production 發現 `SECRET_KEY` 為預設值時會 raise `RuntimeError`。這不是 bug，是有意的防護 — 但 deploy 時必須記得設定。
- **R-C2**: SQLite production 的 backup 策略為空白。若 `runtime.db` 損毀，所有資料遺失。B4 需要 ADR 決定 production DB。
- **R-C3**: `.env.example` 不存在意味著新開發者/運維人員無法一望可知哪些 env var 是必要的。

---

## 5. Cross-Cutting Readiness Gaps

### 5.1 Infrastructure Gaps

| Gap | Severity | Notes |
|-----|----------|-------|
| No Alembic / Flask-Migrate | 🔴 BLOCKER | Schema versioning required for production |
| No Docker / deployment config | 🟡 WARNING | Not blocking for initial launch if deployed manually |
| No CI/CD pipeline | 🟡 WARNING | Manual deploy acceptable for v1 |
| No monitoring / alerting | 🟡 WARNING | Flask default logging only |
| No health check endpoint | 🟢 INFO | Easy to add |
| No backup script for runtime.db | 🔴 BLOCKER | Data loss risk without backup |
| No `.env.example` | 🟢 INFO | Operational convenience |

### 5.2 Test Coverage Gaps

| Gap | Severity | Notes |
|-----|----------|-------|
| Integration tests exist but coverage unknown | 🟡 WARNING | Run `pytest --cov` to measure |
| No E2E tests for full user flows | 🟡 WARNING | Manual testing sufficient for v1 |
| No load / stress tests | 🟢 INFO | Deferred to post-launch |

### 5.3 Documentation Gaps

| Gap | Severity | Notes |
|-----|----------|-------|
| No operations runbook | 🟡 WARNING | Start with `docs/operations/` |
| No deployment guide | 🟡 WARNING | Start with `docs/operations/deployment.md` |
| No disaster recovery plan | 🔴 BLOCKER | Must document backup + restore before launch |

---

## 6. Summary Table

| ID | Area | Item | Classification | Blocker? | Suggested Phase 4 Order |
|----|------|------|---------------|----------|------------------------|
| **B1** | Auth | Route-level `@admin_required` everywhere | ✅ Direct | 🔴 YES | 1 |
| **B2** | Config | Set unique `SECRET_KEY` in production env | ✅ Direct | 🔴 YES | 2 |
| **B3** | Migration | Alembic / Flask-Migrate setup | ⚠️ ADR | 🔴 YES | 3 |
| **B4** | Database | SQLite → PostgreSQL/MySQL | ⚠️ ADR | 🔴 YES | 4 |
| D1 | Auth | Landlord scope filtering | ✅ Direct | No | 5 |
| D2 | Auth | Viewer read-only routes | ✅ Direct | No | 6 |
| D3 | LINE | Log accepted events | ✅ Direct | No | 7 |
| D4 | OCR | Implement real OCR provider | ✅ Direct | No | 8 |
| D5 | Payment | Deprecate unused `PaymentOCRService` | ✅ Direct | No | 9 |
| D6 | Integrations | Graceful startup checks | ✅ Direct | No | 10 |
| D7 | Migration | READ-ONLY header on scripts | ✅ Direct | No | 11 |
| D8 | Migration | Dry-run mode for repair scripts | ✅ Direct | No | 12 |
| D9 | Migration | Rename misleading script names | ✅ Direct | No | 13 |
| D10 | Migration | Write migration SOP doc | ✅ Direct | No | 14 |
| D11 | Config | `.env.example` file | ✅ Direct | No | 15 |
| D12 | Config | Startup config validation log | ✅ Direct | No | 16 |
| A1 | Auth | Landlord data scope filter ADR | ⚠️ ADR | No | 17 |
| A2 | LINE | Payment notification connection | ⚠️ ADR | No | 18 |
| A3 | OCR | Human review workflow | ⚠️ ADR | No | 19 |
| A4 | Sheets | Google Sheets API OAuth + import | ⚠️ ADR | No | 20 |
| A5 | Migration | Production execution checklist | ⚠️ ADR | No | 21 |
| A6 | Config | HTTPS termination strategy | ⚠️ ADR | No | 22 |
| F1 | Auth | Default viewer with no restrictions | ❌ Forbidden | — | — |
| F2 | LINE | Direct DB write from webhook | ❌ Forbidden | — | — |
| F3 | OCR | Production use of TextFileOCRClient | ❌ Forbidden | — | — |

### Count Summary

| Classification | Count |
|---------------|-------|
| ✅ Direct items | 12 |
| ⚠️ ADR items | 6 |
| ❌ Forbidden items | 3 |
| 🔴 Blockers | 4 |
| **Total gaps** | **22** |

---

## 7. Decision Log

| Decision | Rationale |
|----------|-----------|
| Auth role enforcement is #1 blocker | Without it, any authenticated user can modify any data — zero production security |
| `SECRET_KEY` validation protects against production misconfig | The `change-me-in-production` default must never reach production |
| Alembic ADR needed before any schema change in production | Manual schema migration is unacceptable for production systems |
| SQLite→RDBMS ADR deferred to Phase 4B (not Phase 4A) | System could theoretically launch on SQLite with backup strategy, but high risk |
| `contract_expiry_repair.py` must add dry-run before it can be considered production-ready | A repair script that writes without preview is dangerous |
| `PaymentOCRService` should be deprecated if not wired | Dead code path confuses developers and wastes maintenance effort |

---

## Deliverables

- ✅ `docs/reports/reasonix-phase4-readiness-01.md` (this file)
- ⬜ `coordination/progress/reasonix.md` (updated)
- ⬜ `coordination/completed/reasonix.md` (updated)

---

*End of Phase 4 Readiness Guard Note*
