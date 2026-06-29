# Phase 3 Kickoff Gap Check — Payment API / Migration Write Path

Author: open
Date: 2026-06-29
Baseline: `codex-phase2-mainline-01` (HEAD)
Tests: `46 passed, 15 skipped`

---

## 1. Executive Summary

以 Phase 2 完成、`water preview` 落地後的 `codex-phase2-mainline-01` 為基準，盤點 Phase 3 兩個重點領域的前置準備狀態。

**結論：service/repo 層已就緒，缺薄 route 層包裝與 migration write convention。無 blocking gap，無需 incident。**

---

## 2. Water Preview — 確認已完成

| 項目 | 狀態 |
|------|------|
| Route | ✅ `GET,POST /water/<id>/preview` |
| Service | ✅ `WaterService.preview_post_to_monthly_bill()` |
| Template | ✅ `water/preview.html` |
| Integration test | ✅ `test_water_preview.py` |
| 測試結果 | ✅ `46 passed, 15 skipped`（自 closeout 增加 2 passed） |

**water preview 不再是缺口。** Phase 3 無需再處理。

---

## 3. Payment Records API Boundary

### 3.1 現有層級

| 層級 | 檔案 | 狀態 | 說明 |
|------|------|------|------|
| Model | `app/models/billing.py` → `PaymentRecord` | ✅ | Phase 0 已凍結 |
| Repository | `app/repositories/payment_repository.py` | ✅ | `list_all` / `list_recent` / `get_or_404` / `get_by_transaction_id` |
| Service | `app/services/payment_service.py` | ✅ | `create` / `verify` / `reject` / `link` + 狀態機 + reconciliation |
| Reconciliation | `app/services/payment_reconciliation_service.py` | ✅ | `is_bill_paid` 邏輯 |
| UI routes | `app/modules/payments/routes.py` | ✅ | 5 routes：list / create / verify / reject / link |
| API route | `GET,POST /api/payment-records` | ❌ **不存在** | 唯一缺口 |

### 3.2 缺口評估

| 項目 | 細節 |
|------|------|
| 所需實作 | 新增 1 個 blueprint (`api_payments_bp` 或擴展現有) + 2 個 handler (list + create) |
| Service/repo 是否可用 | ✅ 完全就緒 — `PaymentService.create_payment_record()` + `PaymentRepository.list_all()` |
| JSON serialization | 需確認 `PaymentRecord` → dict 轉換（可加 `to_dict()` method 或獨立 serializer） |
| Auth | ✅ `@login_required` 比照 UI route |
| 測試 | 需新增 `test_api_payment_records.py` |
| 工作量 | < 1 小時（薄 JSON wrapper + test） |

### 3.3 結論

> **Phase 3 可直接實作。** Service/repo 層已完整，無需改動 model/contract。只需 1 個 route file + 1 個 test file。

---

## 4. Migration Write Path

### 4.1 現有 Migration / Repair 腳本

| 腳本 | 類型 | 安全性 | 說明 |
|------|------|--------|------|
| `scripts/migration/migration_index.py` | index | ✅ safe | 唯讀入口索引 |
| `scripts/migration/maintenance_legacy_scan.py` | scan | ✅ safe | 掃描虛擬 tenant 與 room status |
| `scripts/repair/year_month_audit.py` | audit | ✅ safe | 檢查 year_month 格式 |
| `scripts/repair/room_status_audit.py` | audit | ✅ safe | 檢查 room status 一致性 |
| `scripts/repair/user_table_audit.py` | audit | ✅ safe | 檢查 user table |
| `scripts/repair/contract_expiry_repair.py` | audit + write | ⚠️ **含 write** | 到期合約自動 terminate（唯讀模式可執行，write 模式需 --apply） |

### 4.2 缺口評估

| 項目 | 細節 |
|------|------|
| `migration_index.py` 分類 | ✅ 已有 type/safety 標示 |
| Write migration convention | ❌ **尚未文件化** — 無正式規範說明何時可用 write mode、誰可授權執行 |
| Write script scaffold | ❌ 無正式 write migration scaffold（如 `YYYYMMDD_description.py` 範本） |
| Runbook 記載 | ❌ `docs/operations/dev-runbook.md` 未提及 migration write 流程 |
| `contract_expiry_repair.py` 的 write mode | ⚠️ 已實作但無額外防護（無第二人確認機制） |

### 4.3 建議 Phase 3 前置

| 優先序 | 項目 | 說明 |
|--------|------|------|
| P1 | 建立 write migration convention | docs 規範：命名規則、審查流程、--apply 安全機制 |
| P2 | 建立 write scaffold 範本 | 如 `scripts/migration/_template.py` 含註解佔位 |
| P3 | 更新 dev-runbook | 追加 migration write 操作章節 |
| P4 | `contract_expiry_repair.py` 加固 | 追加 `--confirm` 二次確認 |

### 4.4 結論

> **Write migration 尚未正式啟動，但已有 read-only 基礎。** Phase 3 應先補 convention 與 scaffold，再開始撰寫實際 write script。

---

## 5. 綜合缺口矩陣

| 領域 | 項目 | Phase 3 優先序 | 依賴 | 預估工時 |
|------|------|---------------|------|---------|
| Payment API | `GET,POST /api/payment-records` | **P0** | 無（service/repo 就緒） | < 1 hr |
| Payment API | API test coverage | P0 | route 完成後 | < 30 min |
| Migration | Write convention docs | **P1** | 無 | 1 hr |
| Migration | Write scaffold 範本 | P2 | convention 完成 | 30 min |
| Migration | dev-runbook 更新 | P3 | convention 完成 | 30 min |
| Migration | `contract_expiry_repair.py` 加固 | P4 | convention 完成 | 30 min |

---

## 6. 高風險邊界確認

逐項檢查 `docs/reports/reasonix-phase2-contract-notes-01.md` 與 `reasonix-maintenance-followup-04.md` 中與 payment API / migration 相關的合規要求：

| 契約規則 | 影響 | 現狀 |
|---------|------|------|
| `PaymentRecord` 為唯一付款實體 | Payment API 不可自創新付款 model | ✅ API 僅操作 `PaymentRecord`，不新增 model |
| `Room.status` 僅 vacant/occupied | migration write 不可改 Room.status 定義 | ✅ `contract_expiry_repair.py` 僅改 `Contract.status` |
| `year_month` 格式須用 core helper | migration write 須使用 `year_month_helper` | ✅ `year_month_audit.py` 已檢查 |

**無高風險邊界不明之處。** 以上 Phase 3 項目均可安全開發。

---

## 7. 結論

- ✅ Water preview 已完成，Phase 3 無需再處理
- ✅ Payment API 的 service/repo 層已就緒，只缺薄 route 層
- ⚠️ Migration write path 尚未正式啟動，但已有 read-only 基礎
- ❌ 無 blocking gap
- ❌ 無需 incident

---

*End of report — no models touched, no data contracts modified, no core code rewritten.*
