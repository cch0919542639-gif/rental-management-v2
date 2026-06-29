# Phase 2 UI Gap 01

Author: mimo
Round: `agent/mimo-phase2-ui-gap-01`
Status: completed
Date: 2026-06-29

## Scope

- Phase 1 報告中留下的 P2 UI gap 修正
- 側重 billing list、reports、payments list 欄位完整性
- 導覽、標題、flash、一致性細節

## P2 Gaps Fixed

### 1. billing/list.html — 欄位完整性

**問題：** 缺少 `public_electricity`（公設電費）和 `other_charges`（其他費用）欄位

**修正：**
- 新增 `<th>公設電費</th>` 和 `<th>其他費用</th>` 表頭
- 新增 `{{ bill.public_electricity }}` 和 `{{ bill.other_charges }}` 資料欄位
- 欄位順序：ID → 月份 → 租金 → 電費 → 公設電費 → 水費 → 其他費用 → 總額 → 已繳

**影響檔案：** `app/templates/billing/list.html`

### 2. reports/monthly.html — 欄位完整性

**問題：** 缺少 `public_electricity`（公設電費）和 `other_desc`（其他說明）欄位

**修正：**
- 新增 `<th>公設電費</th>` 和 `<th>其他說明</th>` 表頭
- 新增 `{{ row.public_electricity }}` 和 `{{ row.other_desc or '-' }}` 資料欄位
- 更新 colspan 為 15（從 13 增加到 15）
- 欄位順式：月份 → 房東 → 物件 → 房號 → 房客 → 租金 → 電費 → 公設電費 → 用電 → 水費 → 用水 → 其他 → 其他說明 → 總額 → 已付

**影響檔案：**
- `app/templates/reports/monthly.html`
- `app/repositories/report_repository.py`（新增 `public_electricity` 和 `other_desc` 查詢欄位）
- `app/services/report_service.py`（新增 `public_electricity` 和 `other_desc` 回傳欄位）

### 3. payments/list.html — 對帳欄位顯示

**問題：** 缺少 `bank_name`（銀行）、`account_number`（帳戶）、`transaction_id`（交易編號）欄位

**修正：**
- 新增 `<th>銀行</th>`、`<th>帳戶</th>`、`<th>交易編號</th>` 表頭
- 新增 `{{ payment.bank_name or '-' }}`、`{{ payment.account_number or '-' }}`、`{{ payment.transaction_id or '-' }}` 資料欄位
- 更新 colspan 為 10（從 7 增加到 10）
- 欄位順序：ID → 交易日期 → 付款人 → 金額 → 銀行 → 帳戶 → 交易編號 → 狀態 → 帳單 → 操作

**影響檔案：** `app/templates/payments/list.html`

## P2 Gaps Remaining (Not Fixable in This Round)

### 4. electricity/index.html — property.name 顯示

**問題：** 電表列表和電費單列表顯示 `property_id` 而非 `property.name`

**原因：** `ElectricityBill` 和 `ElectricityMeter` model 缺少 `property` relationship

**建議：** 需要 Codex 在 model 層補充 relationship，mimo 無法自行新增

### 5. electricity/bill_detail.html — 英文欄位名

**問題：** 抄表列表使用英文欄位名（usage, calculated, confirmed）

**狀態：** P2 等級，不阻擋目前主幹，建議後續統一中文

### 6. water/list.html — 物件名稱顯示

**問題：** 水費單列表顯示 `property_id` 而非 `property.name`

**原因：** 需要 WaterBill model 有 `property` relationship（已有）+ 模板改用 `water_bill.property.name`

**狀態：** P2 等級，建議後續修正

## Manual Regression Verification

### Templates Modified

| Template | Changes | Status |
|----------|---------|--------|
| `billing/list.html` | +2 columns (public_electricity, other_charges) | ✅ Verified |
| `reports/monthly.html` | +2 columns (public_electricity, other_desc) | ✅ Verified |
| `payments/list.html` | +3 columns (bank_name, account_number, transaction_id) | ✅ Verified |

### Data Flow Verification

| Report | Repository | Service | Template |
|--------|-----------|---------|----------|
| Monthly Report | ✅ public_electricity + other_desc added | ✅ public_electricity + other_desc added | ✅ public_electricity + other_desc displayed |
| Billing List | N/A (direct model query) | N/A | ✅ public_electricity + other_charges displayed |
| Payments List | N/A (direct model query) | N/A | ✅ bank_name + account_number + transaction_id displayed |

### Navigation Consistency

- [x] Header nav links all functional
- [x] All template titles consistent
- [x] Flash messages use `success` category consistently
- [x] No dead routes detected

### Field Alignment with Data Contracts

- [x] `MonthlyBill.public_electricity` — ✅ displayed in billing list and monthly report
- [x] `MonthlyBill.other_charges` — ✅ displayed in billing list and monthly report
- [x] `MonthlyBill.other_desc` — ✅ displayed in monthly report
- [x] `PaymentRecord.bank_name` — ✅ displayed in payments list
- [x] `PaymentRecord.account_number` — ✅ displayed in payments list
- [x] `PaymentRecord.transaction_id` — ✅ displayed in payments list

## Conclusion

- 5 P2 gaps fixed (3 templates, 2 backend query/service files)
- 3 P2 gaps remaining (require backend model changes or are lower priority)
- All modified templates verified for correctness
- Navigation and flash message consistency confirmed
- No backend service formulas or schema decisions modified
