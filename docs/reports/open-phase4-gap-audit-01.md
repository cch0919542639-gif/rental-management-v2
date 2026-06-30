# Phase 4 可上線缺口盤點 — open 視角

**報告日期**: 2026-06-30  
**基準線**: `codex-phase2-mainline-01`  
**目標 repo**: `D:\CodexRuntime\rental\rebuild`  
**作者**: open（Codex Phase 4 gap audit）  

---

## 前言

本報告是 Phase 4 缺口盤點的 **open 視角**，重點放在：
- **操作流程缺口**（route 未完成、流程會卡住的地方）
- **設定/維運缺口**（production deployment 會撞到的牆）
- **測試缺口**（整合測試覆蓋不足之處）

與 `reasonix-phase4-readiness-01.md` 的互補定位：
| 項目 | reasonix 報告 | 本報告 (open) |
|------|--------------|--------------|
| 焦點 | 架構決策 / ADR / 安全規則 | Route 完成度 / 部署流程 / 測試涵蓋 |
| Blocker 判斷 | 4 項（B1–B4） | 在本報告 P0 中一併參考 reasonix B1–B4 |
| 交付對象 | reasonix（架構守門） | Codex（實際施工排序） |

> ⚠️ **本報告不重複 reasonix B1–B4**（auth role / SECRET_KEY / Alembic / SQLite→RDBMS）。預設這些已被 reasonix 鎖定為 P0，Codex 施工時應一併納入。

---

## 統計總表

| 優先級 | 數量 | 標籤 |
|--------|:----:|------|
| **P0 (Blocker)** | 6 | 🔴 production 無法上線或啟動後會 crash |
| **P1 (建議做)** | 9 | 🟡 production 可以跑但會卡流程或維運困難 |
| **P2 (可延後)** | 7 | 🟢 polish / post-launch |
| **總計** | **22** | |

---

## P0 — Blocker（不上線不行）

| ID | 缺口 | 類別 | 位置 | 症狀 | 修復方向 |
|----|------|------|------|------|---------|
| **B1** | **@login_required.user_loader 未註冊** | 流程 | `core/db/extensions.py:41` | Flask-Login 無法從 session 恢復 User，受保護 route 會 raise Exception | 在 `init_extensions()` 內或 factory 加上 `@login_manager.user_loader` callback |
| **B2** | **app.models 未完整建構（factory 中 side-effect import）** | 流程 | `core/app_factory/factory.py:38` | `import app.models` 會執行 models `__init__`；若任一 model 有未滿足的 import 則 crash | 確認 models `__init__.py` 能安全 import 所有 model class |
| **B3** | **SECRET_KEY 預設值 production 會 crash** | 設定 | `core/config/validation.py:13` | `validate_runtime_config()` 在 production 偵測 `change-me-in-production` 會 raise RuntimeError | ⚠️ 此為 reasonix B2，列出供 Codex pipeline 參考 |
| **B4** | **無 Alembic / Flask-Migrate** | 維運 | `app/migrations/`（空目錄） | 無法管理 schema 版本，production 無法安全更版 | ⚠️ 此為 reasonix B3，需先 ADR |
| **B5** | **無 production WSGI server** | 維運 | `requirements-dev.txt` | Flask dev server 不適合 production（single-thread, no graceful reload） | 加入 waitress/gunicorn、修改 `wsgi.py` 啟動方式 |
| **B6** | **無 production DB driver 與 backup 策略** | 維運 | `requirements-dev.txt` + `core/config/settings.py:18` | 預設 SQLite 無 concurrent write 保護；無 backup script → 資料損毀無法復原 | 決定 production DB（參閱 reasonix B4 ADR），加入 driver 與 backup script |

---

## P1 — 建議做（production 會卡流程）

### 🟡 P1-A: Route / Flow 缺口

| ID | 缺口 | 位置 | 細節 | 建議 |
|----|------|------|------|------|
| **P1-01** | **Dashboard 極薄，無可用資訊** | `modules/dashboard/routes.py` | `DashboardService.get_summary()` 是 repository 的薄包裝，無圖表、無趨勢、無即時統計 | 補 dashboard 實用資訊（房間數、欠繳數、近期到期合約），非 blocking 但 production 管理員需要 |
| **P1-02** | **無 pagination — 大量資料會爆** | 所有 list route | 13 個 module 中僅 payments API 有 limit/offset。billing、electricity、water 等 list 全部全量回傳 | 為所有 list endpoint 加上分頁（page/page_size 或 cursor），否則百筆資料後網頁失能 |
| **P1-03** | **8 個 module 無 delete endpoint** | modules/* | billing、contracts、electricity、maintenance、payments、properties、rooms、water 無 delete route。僅 landlords / tenants 有 delete | 加入 soft-delete 或「僅限未使用時可刪」的 delete route（需先確認資料關聯） |
| **P1-04** | **無 detail view — 編輯後無法確認** | 11/13 modules | 僅 electricity bill detail、payments API detail 有獨立檢視頁。其餘 module 編輯後只能回到 list，無法確認變更 | 依 module 優先序補 detail page（contract / billing / property 優先） |
| **P1-05** | **LINE webhook events 永遠遺失** | `integrations/line_webhook.py:94` | Webhook 回 200 但不儲存 events。LINE 認為已送達，但 event 被靜默丟棄 | 至少寫 log file 或 DB audit log（reasonix D3） |
| **P1-06** | **MaintenanceFilterForm 關閉 CSRF** | `modules/maintenance/forms.py` | `meta={"csrf": False}` — 雖為 GET filter 表單，但缺少文件說明為何可接受 | 加上註釋說明「GET-only filter form，CSRF 不適用」或僅限 admin 使用時重新啟用 |

### 🟡 P1-B: 測試與維運缺口

| ID | 缺口 | 位置 | 細節 | 建議 |
|----|------|------|------|------|
| **P1-07** | **零 unit test** | `tests/unit/`（空目錄） | 核心計算邏輯（billing total、water allocation、electricity calc）無隔離測試 | 為 `MonthlyBill.total`、`WaterBill.shared_by_stay_days`、`ElectricityBill` status 撰寫 unit test |
| **P1-08** | **15 個 integration test 被 skip** | `tests/integration/test_*.py` | 標註 skip 的測試涵蓋 billing conflict、electricity status transition、water multi-contract、payment reconciliation 等邊界案例 | 逐項確認 skip reason，補齊跳過的測試 |
| **P1-09** | **無 CI/CD 管線** | 根目錄 | 無 `.github/workflows/`、無 pre-commit hook、無自動化測試執行 | 建立基本 CI（push 時跑 pytest + 檢查 seed script） |

---

## P2 — 可延後（上線後 polish）

| ID | 缺口 | 位置 | 細節 | 建議 |
|----|------|------|------|------|
| **P2-01** | **Tenant / Landlord / Room 無 detail view** | modules/* | 僅有 list + create + edit，無法從 list 點入看單筆詳情 | 上線後補 |
| **P2-02** | **Reports 無 maintenance export** | `modules/reports/routes.py` | maintenance report 有 HTML 但無 CSV/XLSX export endpoint | 上線後補 |
| **P2-03** | **Reports format 參數無驗證** | `modules/reports/routes.py` | `?format=csv` 無白名單驗證，任意字串直接傳入 create_sheets_client | 加 allowed_formats 驗證 |
| **P2-04** | **Error handler 無 403/401/405** | `core/errors/handlers.py` | 只註冊 404 和 500。403/401 和 405 fallback 到 Flask 預設，API 請求無法得到 JSON | 補 API 友善的 403/405 handler |
| **P2-05** | **無 `.env.example`** | 根目錄 | 新開發者無法一望可知必要 env var | 建立 `.env.example` |
| **P2-06** | **error HTML template 非 API 時 render 路徑依賴** | `core/errors/handlers.py` | `render_template("errors/app_error.html")` — 若 template 路徑不對會 double fault | 已存在於 `templates/errors/`，但需確認所有 deploy 環境 path 一致 |
| **P2-07** | **無 Dockerfile** | 根目錄 | 無 container 化部署選項 | 上線後建立 |

---

## 給 Codex 的實作順序建議

```
Phase 4A — Blocker 清除（先確認 reasonix B1–B4 已完成）
  0. [reasonix B1] `@admin_required` 套用到所有寫入 route
  1. [reasonix B2] Production 設 `SECRET_KEY`
  2. [B1] `@login_manager.user_loader` callback 註冊
  3. [B2] models `__init__` 確認可安全 import
  4. [B5] 加入 waitress/gunicorn，修改 wsgi.py
  5. [B6] Production DB driver + backup script

Phase 4B — 操作流程補強
  6. [P1-01] Dashboard 補實用統計
  7. [P1-02] 關鍵 list route 加入分頁（billing / electricity / water 優先）
  8. [P1-03] 補 delete endpoint（先做 contract / billing / electricity）
  9. [P1-04] 補 detail view（contract / billing / property 優先）
  10. [P1-06] CSRF 說明或修正

Phase 4C — 測試與維運
  11. [P1-07] 核心計算 logic unit test
  12. [P1-08] 15 個 skipped test 逐項補齊
  13. [P1-09] 建立 CI 管線
  14. [P1-05] LINE webhook event 至少 log 儲存

Phase 4D — Polish
  15. [P2-01~P2-07] 各可延後項目
```

---

## 與 reasonix phase4-readiness-01 的合併對照

| 項目 | reasonix ID | open ID | 是否重疊 |
|------|------------|---------|---------|
| Auth role 未套用 | B1 | 引用 B1（不重複） | ⚠️ reference only |
| SECRET_KEY production 會 crash | B2 | B3 (reference) | ⚠️ reference only |
| Alembic / Flask-Migrate | B3 | B4 (reference) | ⚠️ reference only |
| SQLite→RDBMS | B4 | B6 (partial) | ⚠️ reference only |
| user_loader callback 未註冊 | — | **B1 (new)** | ✅ open 發現 |
| models import 風險 | — | **B2 (new)** | ✅ open 發現 |
| 無 production WSGI server | — | **B5 (new)** | ✅ open 發現 |
| Dashboard 過薄 | D1, D2 | **P1-01** | 部分重疊但不同層級 |
| LINE webhook event 遺失 | D3 | **P1-05** | ✅ 相同 |
| Pagination / Delete / Detail | — | **P1-02~04** | ✅ open 發現 |
| 零 unit test | 5.2 | **P1-07** | ✅ 相同但 open 更具體定位 |
| 15 skipped tests | — | **P1-08** | ✅ open 發現 |
| 無 CI/CD | 5.1 | **P1-09** | ✅ 相同 |

總計 open 獨自發現 **5 項新缺口**（B1、B2、B5、P1-02~04），不在 reasonix 報告中。

---

*End of open Phase 4 gap audit*
