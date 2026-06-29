# Phase 3 Payment Records API Audit — Gap Inventory & Backlog

Author: open
Date: 2026-06-30
Branch: `agent/open-phase3-payment-api-audit-01`
Baseline: `codex-phase2-mainline-01` (HEAD, commit `379f58a`)
Tests Baseline: 51 passed, 15 skipped

---

## 1. 盤點範圍

針對 `app/modules/payments/api_routes.py` 內已上線的 `/api/payment-records` 三個端點做定點缺口分析：

| Method | Path | 現狀 |
|--------|------|------|
| `GET` | `/api/payment-records/` | ✅ list — 支援 `record_status`, `contract_id`, `monthly_bill_id`, `limit` |
| `GET` | `/api/payment-records/<payment_id>` | ✅ detail |
| `POST` | `/api/payment-records/` | ✅ create — 接受完整 PaymentRecord 欄位 |

資料來源：
- `api_routes.py:10-106` — 路由實作
- `payment_repository.py:5-34` — repository 查詢層
- `payment_service.py:18-99` — 服務層 + 狀態機
- `test_payments_api_boundary.py:1-70` — 現有邊界測試
- `core/errors/handlers.py:6-49` — 全域錯誤處理模式
- `data_contracts/payments-contract.md:1-71` — 資料契約

---

## 2. 現有能力盤點

### 2.1 List 端點實際能力

```
GET /api/payment-records/?record_status=pending&contract_id=5&monthly_bill_id=12&limit=50
```

- 篩選欄位：`record_status` (String), `contract_id` (int), `monthly_bill_id` (int)
- 分頁：僅 `limit`（1–200, default 50），**無 offset / cursor**
- 排序：固定 `created_at DESC`，**不可自訂**
- 回傳格式：`{ items: [...], count: int, limit: int }`
- Auth：`@login_required`

### 2.2 Detail 端點實際能力

```
GET /api/payment-records/<payment_id>
```

- 回傳完整序列化 PaymentRecord（19 欄位 + `links.self` HATEOAS）
- 404 由 repository `session_get_or_404` 自動拋出
- Auth：`@login_required`

### 2.3 Create 端點實際能力

```
POST /api/payment-records/
Body: { contract_id, monthly_bill_id, amount, bank_name, ... }
```

- 接受全部 15 個 payload 欄位
- 內部呼叫 `PaymentService.create_payment_record()`，含：
  - Amount 正規化（Decimal 2 位）與負值驗證（→ 422 `DomainValidationError`）
  - Transaction ID 唯一性檢查（重複 → 409 `ConflictError`）
  - MonthlyBill 存在性驗證與 Contract ID 自動補齊
- 回傳 201 + 完整序列化 PaymentRecord
- **無 request body schema 驗證** — 全部 optional，錯欄會寫入 None
- Auth：`@login_required`

---

## 3. Gap 矩陣

### 3.1 缺少的 Query / Filter 參數（List 端點）

| # | 參數 | 現狀 | Phase 3 建議 | 優先序 |
|---|------|------|-------------|--------|
| F1 | `payer_name` | ❌ 無 | 模糊比對或精確篩選 | **P1** |
| F2 | `transaction_date_from` / `transaction_date_to` | ❌ 無 | 日期區間篩選 | **P1** |
| F3 | `amount_min` / `amount_max` | ❌ 無 | 金額範圍篩選 | P2 |
| F4 | `bank_name` | ❌ 無 | 精確或模糊篩選 | P2 |
| F5 | `status_text` | ❌ 無 | 原始狀態文字篩選 | P2 |
| F6 | `offset` (分頁位移) | ❌ 無 | 跳過前 N 筆 | **P1** |
| F7 | `sort_by` / `sort_order` | ❌ 無 | `created_at`, `amount`, `transaction_date` | P2 |
| F8 | `q` 全文檢索 | ❌ 無 | 跨 `transaction_id` / `payer_name` / `notes` 搜尋 | P2 |
| F9 | `created_at_from` / `created_at_to` | ❌ 無 | 建立時間區間 | P2 |

### 3.2 缺少的 API Operation

| # | Operation | 現狀 | 說明 | 優先序 |
|---|-----------|------|------|--------|
| O1 | `PATCH /api/payment-records/<id>` | ❌ 無 | 更新付款記錄（修正 OCR 辨識錯誤或人工校正） | **P0** |
| O2 | `DELETE /api/payment-records/<id>` | ❌ 無 | 刪除無效付款記錄（限 `pending` 狀態） | P2 |
| O3 | `POST .../<id>/verify` | ❌ 僅 UI route | API 端點驗證記錄 | **P1** |
| O4 | `POST .../<id>/reject` | ❌ 僅 UI route | API 端點駁回記錄 | **P1** |
| O5 | `POST .../<id>/link` | ❌ 僅 UI route | API 端點連結帳單 | **P1** |
| O6 | `GET /api/payment-records/stats` | ❌ 無 | 摘要統計（pending 筆數、本月總額等） | P2 |

### 3.3 Error Response 格式缺口

| # | 問題 | 現狀 | 建議 | 優先序 |
|---|------|------|------|--------|
| E1 | 無標準 error schema 文件 | handler 回傳 `{ error, message }`，但無全局規範 | 補 API 錯誤格式文件 | **P1** |
| E2 | 422 無 field-level errors | `DomainValidationError` 只給單一 message | `{ error, message, fields: { amount: "不可為負值" } }` | **P1** |
| E3 | 無 request body schema 驗證 | 錯欄或漏欄直接寫 None，無 400 回應 | 引入 Marshmallow / 自訂 `validate_payload()` | **P0** |
| E4 | 驗證錯誤非中文 | `ConflictError("transaction_id 已存在")` 已是中文 ✅ | 持續保持 | — |
| E5 | 缺少 `X-Request-Id` trace 支援 | 錯誤無可追蹤 ID | 選項：middleware 插入 trace_id | P2 |

### 3.4 Route / Doc Gaps

| # | 問題 | 發現位置 | 優先序 |
|---|------|---------|--------|
| D1 | 無 API documentation 文件 | `docs/` 下無 payment API 專屬文件 | **P1** |
| D2 | `data_contracts/payments-contract.md` 未記載 API contract | 僅含 model schema 與狀態機 | **P1** |
| D3 | 無 OpenAPI / Swagger 規格 | 全域無 spec | P2 |
| D4 | Integration test 僅 2 個案例 | `test_payments_api_boundary.py` — create+list+detail + duplicate | **P0**（需補 error cases） |

---

## 4. 測試覆蓋評估

| 測試檔 | 案例數 | 覆蓋範圍 | 缺口 |
|--------|--------|---------|------|
| `test_payments_api_boundary.py` | 2 | 快樂路徑 + duplicate transaction_id | ❌ 無 422 validation、無 404、無 list empty、無 filter edge |
| `test_payments_reject_and_status.py` | 2 (2 skip) | UI reject flow | ❌ 2 個 skip placeholder（duplicate + reconciliation） |

**需補的 API test cases：**

| # | 案例 | 預期 | 優先序 |
|---|------|------|--------|
| T1 | POST 負值 amount → 422 | `{ error: "validation_error", message: "..." }` | P0 |
| T2 | POST 空 body → 201（全部 optional） | 建立成功，欄位為 None | P1 |
| T3 | GET /api/payment-records/?limit=0 → limit=1 | 自動 clamp 到 1 | P1 |
| T4 | GET /api/payment-records/?limit=999 → limit=200 | 自動 clamp 到 200 | P1 |
| T5 | GET /api/payment-records/999999 → 404 | `{ error: "not_found" }` | P0 |
| T6 | GET /api/payment-records/ 無資料 → 200 empty list | `{ items: [], count: 0 }` | P1 |

---

## 5. P0 / P1 / P2 優先 Backlog for Codex

### P0 — Blocking（Phase 3 務必補）

| ID | 項目 | 檔案 | 依賴 | 預估 |
|----|------|------|------|------|
| P0-1 | **Request body schema validation** — Create 端點補 payload 欄位型別檢查（缺欄不直接寫 None） | `api_routes.py` | 無 | 1 hr |
| P0-2 | **PATCH endpoint** — 允許 API 更新 PaymentRecord 欄位（必要時支援部分更新） | `api_routes.py` + `payment_service.py` | 無 | 1 hr |
| P0-3 | **補 error test cases** — 422 (負值), 404 (不存在的 ID), 409 (重複) | `test_payments_api_boundary.py` | 無 | 30 min |

### P1 — Important（Phase 3 應補）

| ID | 項目 | 檔案 | 依賴 | 預估 |
|----|------|------|------|------|
| P1-1 | **List 補 `payer_name` filter** | `api_routes.py` + `payment_repository.py` | 無 | 30 min |
| P1-2 | **List 補 `transaction_date_from` / `transaction_date_to`** | `api_routes.py` + `payment_repository.py` | 無 | 30 min |
| P1-3 | **List 補 offset 分頁** | `api_routes.py` + `payment_repository.py` | 無 | 30 min |
| P1-4 | **Field-level 422 錯誤細節** — `{ error, message, fields: { ... } }` | `core/errors/exceptions.py` + `handlers.py` | 無 | 1 hr |
| P1-5 | **verify / reject / link API 端點** — 包裝現有 `PaymentService` | `api_routes.py` | P0-2 完成後 | 1 hr |
| P1-6 | **API documentation** — 補 `docs/api/payment-records-api.md` 或寫入現有 contract | `data_contracts/payments-contract.md` | 無 | 1 hr |
| P1-7 | **補一般 test cases** — 空 list、limit clamp、空 body create | `test_payments_api_boundary.py` | 無 | 30 min |

### P2 — Nice to Have（Phase 3+/defer）

| ID | 項目 | 說明 | 預估 |
|----|------|------|------|
| P2-1 | List 補 `amount_min` / `amount_max` | 金額範圍 | 30 min |
| P2-2 | List 補 `bank_name`, `status_text`, `q` | 篩選擴充 | 1 hr |
| P2-3 | List 補 `sort_by` / `sort_order` | 排序選項 | 30 min |
| P2-4 | List 補 `created_at_from` / `created_at_to` | 時間區間 | 30 min |
| P2-5 | DELETE endpoint（僅限 pending） | 刪除 | 30 min |
| P2-6 | Stats endpoint | 摘要統計 | 30 min |
| P2-7 | OpenAPI / Swagger spec | 全域規格 | 2 hr |
| P2-8 | `X-Request-Id` trace 支援 | 可追蹤性 | 1 hr |

---

## 6. 風險邊界

| 檢查項 | 狀態 | 說明 |
|--------|------|------|
| 是否改到 `app/models` | ❌ 無需改動 | 本次 audit 不建議改 model |
| 是否建立第二套 payment flow | ❌ 無需 | 所有建議均使用現有 `PaymentRecord` + `PaymentService` |
| 是否擴大到 OCR/LINE 實作 | ❌ 無需 | audit 僅限 API 邊界 |
| 是否有 Blocking Gap | ❌ **無** | 所有缺口均可增量補完，無依賴死結 |
| 是否需 incident | ❌ 無需 | 現有功能正常，非 blocking issue |

---

## 7. 結論

- ✅ `/api/payment-records` 三個端點已正常運作，無 blocking defect
- ⚠️ **核心缺口 5 項**：request body schema、PATCH、verify/reject/link API、filter 不足、test coverage 偏低
- 📋 **P0 有 3 項**（總預估 ~2.5 hr）、**P1 有 7 項**（~5.5 hr）、**P2 有 8 項**（~6.5 hr）
- 🔧 全部建議改動均可在 `api_routes.py` / `payment_repository.py` / `core/errors/` 範圍內完成，不影響 model 與資料契約

---

*End of report — no models changed, no data contracts modified, no second payment flow created.*
