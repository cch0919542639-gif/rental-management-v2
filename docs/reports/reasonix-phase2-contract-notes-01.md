# Phase 2 Contract & Risk Notes — Decision Guide for Codex

Date: 2026-06-28  
Author: reasonix  
Branch: `agent/reasonix-phase2-contract-notes-01`  
Purpose: 提供 Codex 可直接施工的 Phase 2 契約邊界與風險說明  
Baseline: `main` (origin, commit `6456069`)

---

## Executive Summary

Phase 2 最大工作量集中在 **billing create/generate/batch** 流程補完（P0 缺口）與 **maintenance schema 設計**（需先有 ADR）。`reports` / `payments` / `electricity` / `water` 在 Phase 2 的變更邊界已收斂，多數為欄位補強與 UI 層改動，高風險變更（改狀態機、改 schema）已被排除。

---

## 1. Billing Create / Generate / Batch — Contract Boundaries

### 1.1 Current State

`billing/` 模組只有一個 `billing_list()` route — **完全唯讀**。`MonthlyBill` model 已完整定義（含所有 charge 欄位、`UniqueConstraint`、`calculate_total` static method），但無任何 route 或 service 能建立/編輯/批次產生月帳單。

### 1.2 Frozen Contract (不可違反)

| Rule | Source | Rationale |
|------|--------|-----------|
| `MonthlyBill.year_month` = DB `YYYYMM` (String(6)) | Architecture Decision | 與實際資料一致，ORM 已修正 |
| `year_month` 轉換只能用 `core/year_month.py` helper | Architecture Decision | 禁止 route/service 各自 `replace('-', '')` |
| `contract_id + year_month` UNIQUE | Data Contract | 避免重複帳單 |
| `Room.status` 僅 `vacant`/`occupied` | Architecture Decision | 不因 billing 狀態改變 Room.status |
| `PaymentRecord` 為唯一付款實體 | Architecture Decision | billing 不可自創付款流程 |

### 1.3 Decision Notes for Codex

#### D1 — MonthlyBill Generation Logic

**問題**: 目前無 route/service 可建立 `MonthlyBill` row。

**建議作法**:

```
新增: app/services/billing_generate_service.py
  方法: generate_for_contract(contract_id, year_month) → MonthlyBill
  方法: generate_for_month(year_month) → list[MonthlyBill]  (batch)

合約規則:
  - 只對 status='active' 的 contract 建立帳單
  - 跳過已存在 (contract_id, year_month) 的組合（UniqueConstraint 保證）
  - year_month 需先用 to_db_year_month() 正規化
  - 新 bill 預設值: rent = contract.rent, paid = False, total = rent
  - 其他欄位 (electricity_*, water_*, public_electricity, other_charges) 預設 0
```

**風險**: LOW — 這是純新增 service，不更改既有 model/route。

#### D2 — Billing Create Route (單筆建立)

**建議作法**:

```
新增: app/modules/billing/routes.py
  - GET/POST /billing/create → 單筆月帳單建立表單
  - 表單欄位: contract_id selector, year_month, rent (預填 contract.rent)

禁止事項:
  - 不可讓 user 直接改 electricity_amount / water_amount（由 electricity/water post flow 寫入）
  - 不可改 paid flag（由 payment reconciliation 控制）
  - 不可改 total（由 BillingService.calculate_total() 自動計算）
```

**風險**: LOW — 新增 route 不影響現有 flow。

#### D3 — Billing Edit Route

**建議作法**:

```
新增: GET/POST /billing/<int:bill_id>/edit
  可編輯欄位: rent, other_charges, other_desc, notes
  不可編輯欄位: contract_id, year_month, paid, total, electricity_*, water_*, public_electricity

驗證規則:
  - 變更 rent 或 other_charges 後自動 recalculate total
```

**風險**: LOW — 自含的 CRUD 操作。

#### D4 — Batch Entry (批次建立/編輯)

**建議作法**:

```
新增: GET/POST /billing/batch
  - 選取 year_month
  - 顯示所有 active contract 的清單，每個可勾選
  - 一次送出建立多筆 MonthlyBill

禁止事項:
  - 不可批次刪除帳單（soft-delete 或 archive 需先有 ADR）
  - 不可批次改 paid 狀態（由 payment reconciliation 控制）
```

**風險**: MEDIUM — batch 操作需注意 transaction 邊界：全部成功或全部 rollback。

#### D5 — Per-Contract Bill Listing

**建議作法**:

```
新增: GET /contracts/<int:contract_id>/bills
  - 列出該 contract 的所有 MonthlyBill（BillingRepository.list_for_contract 已存在）
```

**風險**: LOW — repository 已存在，只需 route + template。

### 1.4 Key Constraints Summary (Billing)

| Constraint | Enforcement |
|------------|-------------|
| Unique (contract_id, year_month) | DB UniqueConstraint + Service 層先檢查 |
| year_month format | 一律經 `to_db_year_month()` |
| total 由 service 自動計算 | 禁止 route 直接寫 `bill.total = x` |
| paid 由 payment reconciliation 控制 | 禁止 route 直接 flip paid |
| electricity/water 由各自模組寫入 | 禁止 billing route 改 electricity_*/water_* |

---

## 2. Maintenance — Schema Decision Requirements

### 2.1 Current State

`maintenance/` 只有一個 `GET /` route，回傳唯讀的 `room_snapshot()`（從 Room table 直接讀取）。**無 model、無 schema、無狀態機**。

### 2.2 Minimum Decisions Needed Before Creating Schema

Codex 需先回答以下問題才能建立 `maintenance` 正式 schema：

#### M1 — 狀態機（Required Before Coding）

```
建議狀態集合:
  reported → assigned → in_progress → resolved
                                    → closed
  reported → cancelled

禁止:
  - 不可與 Room.status 混用（Room.status 只能 vacant/occupied）
  - 不可與 Contract.status 混用
```

**決策**: 請 Codex 確認這組狀態機是否涵蓋業務需求。

#### M2 — 關聯方式（Required Before Coding）

```
選項 A: 獨立 maintenance 表 + room_id FK
  優點: schema 乾淨，不污染 Room table
  缺點: 查詢需 JOIN
  建議: ✅ 選此方案

選項 B: 在 Room table 加 maintenance_flag / maintenance_status
  優點: 查詢簡單
  缺點: Room table 語義被污染，違反 Phase 0 隔離原則
  建議: ❌ 不採用
```

#### M3 — 最低必要欄位

```
id (PK, auto)
room_id (FK → rooms.id, NOT NULL)
status (String(20), NOT NULL, default='reported')
description (Text)
reported_by (String(100))        — 通報人
reported_at (DateTime, default=now)
assigned_to (String(100))         — 指派給誰
resolved_at (DateTime, nullable)
cost (Numeric(10,2), nullable)    — 維修費用
notes (Text)
created_at, updated_at (TimestampMixin)
```

#### M4 — 不在此輪做的項目

```
- maintenance attachment / image upload（Phase 3+）
- recurring maintenance schedule（Phase 3+）
- LINE notification for maintenance（Phase 3+）
```

### 2.3 Risk If Delayed

| Risk | Impact | Mitigation |
|------|--------|------------|
| Codex 開始施工但無決策 | 可能寫出需重工的 schema | 先做成 M1-M3 決定再 coding |
| 違反 Room.status 隔離原則 | 回到舊系統的耦合問題 | 決策中明確禁止選項 B |

---

## 3. Reports — Phase 2 Change Boundaries

### 3.1 Current Compliance

Phase 1 review 02 已確認 reports 模組通過合規檢查：
- ✅ 無虛擬 tenant 關鍵字比對（**關鍵修正已到位**）
- ✅ 使用 `YearMonthHelper`
- ✅ 使用 `Room.status` + `Contract.status`

### 3.2 Low-Risk Changes (可直接施工)

| Change | File | Risk | Note |
|--------|------|------|------|
| 月報表增加「已收 vs 未收」金額欄 | `ReportRepository`, `ReportService` | LOW | 純新增欄位 |
| 年報表增加每月已收比例 | `ReportRepository`, `ReportService` | LOW | 純計算欄位 |
| 增加 vacancy rate 統計 | `ReportRepository` | LOW | 新查詢，不影響既有 |
| landlord-summary 可選月份範圍 | `routes.py` + template | LOW | UI filter |
| 增加 CSV/Excel 匯出 | `ReportService` | LOW | 新增方法 |

### 3.3 High-Risk Changes (禁止)

| Change | Reason |
|--------|--------|
| 改回 `tenant.name` 關鍵字比對 | 違反 Phase 0 契約 |
| 改 `MonthlyBill.paid` 計算邏輯 | 應由 payment reconciliation 驅動 |
| 移除 `year_month` helper | 契約強制使用 |
| 讓 report route 直接寫 DB | 違反 route→service→repository 邊界 |

### 3.4 Phase 2 Suggested Order

1. 月報表補「已收/未收」欄位（低風險、高價值）
2. CSV 匯出（低風險、UX 改善）
3. Vacancy rate 統計（低風險、房東常用）

---

## 4. Payments — Phase 2 Change Boundaries

### 4.1 Current Compliance

Phase 1 review 02 已確認 payments 模組通過：
- ✅ `PaymentRecord` 狀態機完整
- ✅ 無 `Payment` 死碼
- ✅ reconciliation 乾淨

### 4.2 Low-Risk Changes

| Change | File | Risk | Note |
|--------|------|------|------|
| payments list 增加對帳欄位（bank/account/date） | template | LOW | 僅 UI 層 |
| 增加 payment delete（soft-delete or admin only） | `routes.py`, `service` | LOW | 需先確認 soft-delete policy |
| 增加 OCR 欄位顯示在 detail page | template | LOW | Phase 2 OCR 尚未上線，但欄位已存在 |
| payments list 支援月份 filter | `routes.py`, repository | LOW | 新增查詢條件 |
| payment link 時顯示已連結帳單 detail | template | LOW | UX 改善 |

### 4.3 High-Risk Changes (禁止)

| Change | Reason |
|--------|--------|
| 改 `record_status` 狀態機（pending→verified→linked→rejected） | 違反已凍結契約 |
| 移除 `transaction_id` uniqueness | 對帳完整性需要 |
| 讓 route 直接改 `monthly_bill.paid` | 違反 route→service 邊界 |
| 新增付款實體取代 `PaymentRecord` | 違反架構決策 |

### 4.4 OCR Integration Note

`PaymentRecord` schema 已有 OCR 欄位（`raw_ocr_text`, `raw_llm_response`, `image_path`, `ocr_engine`），但 `app/integrations/` 目錄目前是空的。Phase 2 若需 OCR 整合：
- 新增 `integrations/ocr_service.py`（呼叫外部 OCR API）
- 新增 `modules/payments/ocr_routes.py` 或擴展現有 route
- **不可** 改動 `PaymentRecord` schema（欄位已夠用）

---

## 5. Electricity — Phase 2 Change Boundaries

### 5.1 Current Compliance

Phase 1 review 02 已確認 electricity 模組通過：
- ✅ 無 hard-coded `meter_id=1`
- ✅ `year_month` = String(6) + helper
- ✅ Route→Service→Repository 模式

### 5.2 Low-Risk Changes

| Change | File | Risk | Note |
|--------|------|------|------|
| Property-specific bill filter | `routes.py`, `ElectricityBillRepository` | LOW | 新增查詢方法 |
| Quick reading 功能 | `routes.py`, `ElectricityService` | LOW | 新增 route |
| Reading log (歷史查詢) | `routes.py`, `ElectricityReadingRepository` | LOW | 新增 route |
| Meter 刪除（admin only） | `routes.py`, `ElectricityService` | LOW | 需確認 soft-delete |
| 電費單 edit route | `routes.py`, form | LOW | 補 CRUD 完整性 |

### 5.3 High-Risk Changes (禁止)

| Change | Reason |
|--------|--------|
| 在 route 內寫計算公式 | 違反 route→service 邊界（舊系統問題已修復） |
| 硬編碼 `meter_id=1` | 回歸舊系統 bug |
| 改 `ElectricityBill` schema 的 `year_month` 格式 | 違反契約 |
| 讓 electricity post flow 直接寫 `monthly_bill.total` | 應由 `BillingService.calculate_total()` 處理 |

### 5.4 Phase 2 Suggested Order

1. Property-specific bill filter（低風險、依 open gap audit）
2. Electricity bill edit route（CRUD 完整性）
3. Quick reading 功能（操作效率）

---

## 6. Water — Phase 2 Change Boundaries

### 6.1 Current Compliance

Phase 1 review 02 已確認：
- ✅ Shared / independent 分配邏輯正確
- ✅ 無舊 `water_bill.py` reverse import

### 6.2 Low-Risk Changes

| Change | File | Risk | Note |
|--------|------|------|------|
| Water bill delete route | `routes.py`, `WaterService` | LOW | 補 CRUD |
| Water bill detail page | `routes.py`, template | LOW | 目前只有 list |
| Property-specific water bill filter | `WaterBillRepository` | LOW | 新增查詢 |
| Water bill preview route | `routes.py`, `WaterService` | LOW | UX 改善 |

### 6.3 High-Risk Changes (禁止)

| Change | Reason |
|--------|--------|
| 改 shared allocation 公式邏輯 | 需先有 ADR 確認分攤規則 |
| 讓 water route 直接寫 `monthly_bill.water_amount` | 違反 route→service 邊界 |
| 移除 `property_id` 關聯 | 水費單需綁定 property |
| 改 `WaterBill` schema 核心欄位 | 未凍結但不宜無 ADR 改動 |

---

## 7. Cross-Cutting Phase 2 Boundary Rules

### 7.1 可直接做（不需 reasonix 覆核）

- 新增 route（不更改 model / service 核心邏輯）
- 新增 template（純 UI）
- 新增查詢方法到 repository（不更改既有方法簽名）
- 新增 service 方法（不更改既有方法簽名）
- 新增 tests
- 補 CRUD 遺漏（delete、edit）

### 7.2 需先有 ADR 才能做

- 新增資料表 / model
- 改既有 model 的 constraint / FK / unique
- 改狀態機定義（`record_status`, `Contract.status`, `Room.status`）
- 改計費公式（water allocation, electricity calculation）
- 新增整合對接（LINE, OCR, Sheets）

### 7.3 無論如何不可做

- 改 `year_month` 格式
- 新增虛擬 tenant 或 tenant.name 關鍵字邏輯
- 在 `Room.status` 增加非 `vacant`/`occupied` 的值
- 新增第二套付款流程
- 讓 module 直接 import 另一個 module 的 route / service

---

## 8. Phase 2 Priority Recommendation

| Priority | Work Item | Depends On | Risk | Estimated Effort |
|----------|-----------|------------|------|------------------|
| P0 | Billing generate/create/batch flow | None | MEDIUM | 3-5 routes + 1 service |
| P0 | Maintenance schema ADR + model | M1-M3 decisions | MEDIUM | 1 ADR + 1 model |
| P1 | Billing edit route | Billing create done | LOW | 1 route |
| P1 | Reports: 已收/未收欄位 + CSV export | None | LOW | 2-3 methods |
| P2 | Payments: filter + detail UI | None | LOW | templates only |
| P2 | Electricity: property filter + edit | None | LOW | 2 routes |
| P2 | Water: delete + detail | None | LOW | 2 routes |
| P3 | Integrations (OCR, LINE, Sheets) | Core billing stable | MEDIUM | New module |

---

## 9. Risk Register (Phase 2)

| ID | Area | Risk | Severity | Mitigation |
|----|------|------|----------|------------|
| R01 | billing | Batch generate 若無 transaction 保護可能部分寫入 | MEDIUM | 使用 `db.session` transaction，失敗全數 rollback |
| R02 | maintenance | 延遲 ADR → Codex 自行猜 schema → 後續需重工 | MEDIUM | 先決定 M1-M3 再 coding |
| R03 | electricity/water | Post-to-monthly flow 若 billing generate 尚未實作，post 可能失敗 | MEDIUM | 先完成 billing create/generate 再處理 post flow 測試 |
| R04 | cross-module | Codex 在新增 route 時可能跳過 service 層直接操作 model | LOW | review gate 檢查 |
| R05 | reports | 增加欄位時可能誤用 `year_month` 格式 | LOW | review gate 檢查 |
| R06 | payments | OCR 整合可能改動 `PaymentRecord` schema（但欄位已夠用） | LOW | review gate 確認 |

---

## 10. Decision Log

| Decision | Rationale |
|----------|-----------|
| Billing generate 應為獨立 service (`BillingGenerateService`) | 與現有 `BillingService.calculate_total()` 職責分離 |
| Maintenance schema 選獨立表 + room_id FK | 不污染 Room table，符合 Phase 0 隔離原則 |
| Reports 不在此輪加新 aggregation model | 現有 query-based 報表已夠用 |
| Payments OCR 欄位不改，等 integrations 模組實作 | 欄位設計已涵蓋 OCR 需求 |
| Electricity/water 不在此輪改計算公式 | 公式尚未凍結，需等 Phase 2 後期收集實際需求 |

---

## Deliverables

- ✅ `docs/reports/reasonix-phase2-contract-notes-01.md` (this file)
- ⬜ `coordination/progress/reasonix.md` (updated)
- ⬜ `coordination/completed/reasonix.md` (updated)
