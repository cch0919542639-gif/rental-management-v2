# Phase 1 UI Regression Report (Round 02)

Date: 2026-06-28
Author: mimo
Branch: agent/mimo-ui-regression-02

---

## Scope

針對 Phase 1 已完成頁面，逐頁比對模板欄位 vs 契約欄位、標題、導覽、flash 訊息一致性。重點檢查 payments / electricity / water / reports / maintenance。

## Method

1. 讀取 `data_contracts/` 凍結欄位
2. 讀取 `app/modules/*/routes.py` 與 `app/modules/*/forms.py`
3. 讀取 `app/templates/**/*.html` 逐一比對
4. 比對 `mimo-ui-field-matrix.md` 定義的欄位清單

---

## 1. Payments

### 模板檔案

- `payments/list.html`
- `payments/form.html`
- `payments/review_form.html`
- `payments/link_form.html`

### 欄位比對

| 契約欄位 | Form 有 | List 顯示 | 狀態 |
| --- | --- | --- | --- |
| contract_id | Y | - | OK |
| monthly_bill_id | Y | Y (bill id) | OK |
| amount | Y | Y | OK |
| bank_name | Y | - | GAP: list 未顯示 |
| account_number | Y | - | GAP: list 未顯示 |
| account_holder | Y | - | GAP: list 未顯示 |
| transaction_date | Y | Y | OK |
| payer_name | Y | Y | OK |
| transaction_id | Y | - | GAP: list 未顯示 |
| status_text | Y | - | OK (optional) |
| raw_ocr_text | Y | - | OK (form only) |
| raw_llm_response | Y | - | OK (form only) |
| image_path | Y | - | OK (form only) |
| ocr_engine | Y | - | OK (form only) |
| record_status | auto | Y | OK |
| verified_by_id | auto | - | OK (internal) |
| verified_at | auto | - | OK (internal) |
| notes | Y | - | OK |

### Flash 訊息

- 建立: "付款記錄已建立" ✅
- 驗證: "付款記錄已驗證" ✅
- 駁回: "付款記錄已駁回" ✅
- 連結: "付款記錄已連結帳單" ✅

### 導覽

- base.html nav 有 Payments 連結 ✅
- list.html 有「新增付款記錄」連結 ✅
- pending 狀態顯示「驗證」「駁回」 ✅
- verified 狀態顯示「連結帳單」 ✅

### Gap 清單

| # | 項目 | 嚴重度 | 說明 |
| --- | --- | --- | --- |
| P-1 | payments list 未顯示 bank_name, account_number, account_holder, transaction_id | P2 | 不影響功能，但對帳時需點進去看 |
| P-2 | payments list 未顯示 contract_id | P2 | 无法从列表直接看到关联合约 |

---

## 2. Electricity

### 模板檔案

- `electricity/index.html`
- `electricity/bill_form.html`
- `electricity/bill_detail.html`
- `electricity/meter_form.html`
- `electricity/reading_form.html`
- `electricity/post_form.html`

### 欄位比對

| 契約欄位 | Form 有 | List/Detail 顯示 | 狀態 |
| --- | --- | --- | --- |
| property_id | Y | Y (id only) | GAP: list 顯示 id 而非 name |
| meter_id | Y | - | OK |
| calc_method_id | Y | - | OK |
| year_month | Y | Y (year_month_ui) | OK |
| period_start | Y | - | OK |
| period_end | Y | - | OK |
| prev_reading | Y | - | OK |
| curr_reading | Y | - | OK |
| total_amount | Y | Y (detail) | OK |
| public_amount | Y | - | OK |
| flow_amount | Y | - | OK |
| ocr_raw_text | Y | - | OK |
| status | auto | Y (detail + list) | OK |
| ElectricityMeter.property_id | - | Y (id only) | GAP: 顯示 id 而非 name |
| ElectricityMeter.room_id | - | Y (id or '-') | OK |
| ElectricityMeter.is_main | - | Y (Y/N) | OK |
| ElectricityReading.usage | - | Y (detail) | OK |
| ElectricityReading.calculated_amount | - | Y (detail) | OK |
| ElectricityReading.confirmed_amount | - | Y (detail) | OK |

### Flash 訊息

- 電表建立: "電表已建立" ✅
- 電表更新: "電表已更新" ✅
- 電費單建立: "電費單已建立" ✅
- 抄表建立: "抄表資料已建立" ✅
- 標記 calculated: "電費單已標記為 calculated" ✅
- 回寫月帳單: "電費已回寫月帳單" ✅

### 導覽

- base.html nav 有 Electricity 連結 ✅
- index.html 有「新增電表」「新增電費單」連結 ✅
- bill_detail 有「新增抄表」「回寫月帳單」「標記 calculated」 ✅

### Gap 清單

| # | 項目 | 嚴重度 | 說明 |
| --- | --- | --- | --- |
| E-1 | index.html 電表 list 顯示 property_id (數字) 而非 property.name | P1 | 使用者無法直觀辨識物件 |
| E-2 | index.html 電費單 list 顯示 property_id (數字) 而非 property.name | P1 | 同上 |
| E-3 | bill_detail.html 讀數表格表頭為英文 "usage", "calculated", "confirmed" | P2 | 應改為中文標籤 |
| E-4 | bill_detail.html 未顯示 property_name 與 meter_number | P2 | 需 JOIN 查詢 |

---

## 3. Water

### 模板檔案

- `water/list.html`
- `water/form.html`
- `water/post_form.html`

### 欄位比對

| 契約欄位 | Form 有 | List 顯示 | 狀態 |
| --- | --- | --- | --- |
| property_id | Y | Y (id only) | GAP: 顯示 id 而非 name |
| billing_start | Y | Y | OK |
| billing_end | Y | Y | OK |
| total_amount | Y | Y | OK |
| meter_prev_1 | Y | - | OK |
| meter_curr_1 | Y | - | OK |
| sub_meter_1 | Y | - | OK |
| actual_usage_1 | Y | - | OK |
| meter_prev_2 | Y | - | OK |
| meter_curr_2 | Y | - | OK |
| sub_meter_2 | Y | - | OK |
| actual_usage_2 | Y | - | OK |
| notes | Y | - | OK |

### Flash 訊息

- 建立: "水費單已建立" ✅
- 更新: "水費單已更新" ✅
- 回寫: "水費已回寫月帳單" ✅

### 導覽

- base.html nav 有 Water 連結 ✅
- list.html 有「新增水費單」連結 ✅
- list.html 有「回寫月帳單」連結 ✅

### Gap 清單

| # | 項目 | 嚴重度 | 說明 |
| --- | --- | --- | --- |
| W-1 | water list 顯示 property_id (數字) 而非 property.name | P1 | 使用者無法直觀辨識物件 |
| W-2 | water list 未顯示 meter_prev_1 / meter_curr_1 / actual_usage_1 | P2 | 對帳時需點進去看 |

---

## 4. Reports

### 模板檔案

- `reports/index.html`
- `reports/monthly.html`
- `reports/landlord_summary.html`
- `reports/yearly.html`

### 欄位比對 (Monthly Report)

| 契約欄位 | 顯示 | 狀態 |
| --- | --- | --- |
| year_month | Y | OK |
| landlord_name | Y | OK |
| property_name | Y | OK |
| room_number | Y | OK |
| tenant_name | Y | OK |
| rent | Y | OK |
| electricity_amount | Y | OK |
| electricity_usage | Y | OK |
| water_amount | Y | OK |
| water_usage | Y | OK |
| other_charges | Y | OK |
| total | Y | OK |
| paid | Y (Y/N) | OK |

### 欄位比對 (Landlord Summary)

| 欄位 | 顯示 | 狀態 |
| --- | --- | --- |
| landlord_name | Y | OK |
| property_name | Y | OK |
| bill_count | Y | OK |
| total_amount | Y | OK |
| paid_amount | Y | OK |
| unpaid_amount | Y | OK |

### 欄位比對 (Yearly Overview)

| 欄位 | 顯示 | 狀態 |
| --- | --- | --- |
| year_month | Y | OK |
| total_amount | Y | OK |
| paid_amount | Y | OK |
| unpaid_amount | Y | OK |

### 導覽

- base.html nav 有 Reports 連結 ✅
- index.html 有三個子頁面入口 ✅
- monthly / landlord_summary / yearly 都有月份/年份篩選 ✅

### Gap 清單

| # | 項目 | 嚴重度 | 說明 |
| --- | --- | --- | --- |
| R-1 | monthly.html 未顯示 public_electricity 欄位 | P2 | 契約有此欄位但月報未獨立顯示 |
| R-2 | monthly.html 未顯示 other_desc 欄位 | P2 | 契約有此欄位但月報未獨立顯示 |
| R-3 | monthly.html 未顯示 paid_date 欄位 | P2 | 契約有此欄位但月報未獨立顯示 |

---

## 5. Maintenance

### 模板檔案

- `maintenance/index.html`

### 狀態

- 正式 schema 尚未凍結（phase1-master-status.md 已確認）
- 目前只提供房間快照，避免把「待修」塞回 Room.status 或虛擬 tenant 名稱
- 頁面顯示: Room ID / 物件 / 房號 / 狀態 / 備註

### Gap 清單

| # | 項目 | 嚴重度 | 說明 |
| --- | --- | --- | --- |
| M-1 | maintenance schema 未凍結 | P1 | 需等 reasonix 決策後才能做完整 UI 對齊 |

---

## 6. Dashboard

### 欄位比對

| 契約欄位 | 顯示 | 狀態 |
| --- | --- | --- |
| room_count | Y | OK |
| occupied_count | Y | OK |
| vacant_count | Y | OK |
| month_collected | Y | OK |
| month_unpaid | Y | OK |
| active_contracts | Y | OK |
| recent_bills | Y | OK |

### Gap 清單

| # | 項目 | 嚴重度 | 說明 |
| --- | --- | --- | --- |
| D-1 | 未顯示「本月应收」(month_revenue) | P2 | field matrix 定義有此欄位，dashboard 未獨立顯示 |

---

## 7. Billing

### 欄位比對

| 契約欄位 | 顯示 | 狀態 |
| --- | --- | --- |
| year_month | Y (year_month_ui) | OK |
| rent | Y | OK |
| electricity_amount | Y | OK |
| water_amount | Y | OK |
| total | Y | OK |
| paid | Y (是/否) | OK |

### Gap 清單

| # | 項目 | 嚴重度 | 說明 |
| --- | --- | --- | --- |
| B-1 | 未顯示 public_electricity | P2 | 契約有此欄位 |
| B-2 | 未顯示 other_charges | P2 | 契約有此欄位 |
| B-3 | 未顯示 contract_id / tenant_name | P2 | 無法從列表看到關聯合約 |

---

## 8. Base Template / Navigation

### 導覽連結

| 頁面 | 連結 | 狀態 |
| --- | --- | --- |
| Dashboard | url_for('dashboard.dashboard_home') | ✅ |
| Billing | url_for('billing.billing_list') | ✅ |
| Payments | url_for('payments.payment_list') | ✅ |
| Electricity | url_for('electricity.electricity_dashboard') | ✅ |
| Water | url_for('water.water_list') | ✅ |
| Reports | url_for('reports.report_index') | ✅ |
| Maintenance | url_for('maintenance.maintenance_index') | ✅ |
| Landlords | url_for('landlords.landlord_list') | ✅ |
| Properties | url_for('properties.property_list') | ✅ |
| Rooms | url_for('rooms.room_list') | ✅ |
| Tenants | url_for('tenants.tenant_list') | ✅ |
| Contracts | url_for('contracts.contract_list') | ✅ |
| Logout | url_for('auth.logout') | ✅ |

### Flash 訊息样式

- base.html 定義 `.flash` / `.flash-danger` ✅
- 所有 route 使用 `flash("訊息", "success")` ✅
- 未使用 error category（目前無 `.flash-error` 定義）⚠️

---

## 總結：需要修正的項目

### P1 (應修正)

| # | 模組 | 問題 | 建議修正 |
| --- | --- | --- | --- |
| E-1 | electricity | index 電表 list 顯示 property_id 而非 name | route 傳入 property name 或 JOIN |
| E-2 | electricity | index 電費單 list 顯示 property_id 而非 name | 同上 |
| W-1 | water | list 顯示 property_id 而非 name | 同上 |

### P2 (建議修正)

| # | 模組 | 問題 | 建議修正 |
| --- | --- | --- | --- |
| E-3 | electricity | bill_detail 表頭英文 | 改為中文 |
| E-4 | electricity | bill_detail 未顯示 property/meter name | JOIN 查詢 |
| P-1 | payments | list 未顯示 bank/account/transaction_id | 加入欄位或做成 expandable row |
| W-2 | water | list 未顯示 meter 讀數 | 加入摘要欄位 |
| R-1 | reports | monthly 未顯示 public_electricity | 加入欄位 |
| R-2 | reports | monthly 未顯示 other_desc | 加入欄位 |
| B-1 | billing | list 未顯示 public_electricity | 加入欄位 |
| B-2 | billing | list 未顯示 other_charges | 加入欄位 |
| D-1 | dashboard | 未顯示 month_revenue | 加入卡片 |
| M-1 | maintenance | schema 未凍結 | 等 reasonix 決策 |

---

## 手動回歸證據

### 已驗證頁面

| 頁面 | 路由 | 結果 |
| --- | --- | --- |
| Login | /auth/login | ✅ 正常顯示 |
| Dashboard | / | ✅ 正常顯示 |
| Billing | /billing/ | ✅ 正常顯示 |
| Payments | /payments/ | ✅ 正常顯示 |
| Electricity | /electricity/ | ✅ 正常顯示 |
| Water | /water/ | ✅ 正常顯示 |
| Reports | /reports/ | ✅ 正常顯示 |
| Reports Monthly | /reports/monthly | ✅ 正常顯示 |
| Reports Landlord | /reports/landlord-summary | ✅ 正常顯示 |
| Reports Yearly | /reports/yearly | ✅ 正常顯示 |
| Maintenance | /maintenance/ | ✅ 正常顯示 |

### Flash 訊息驗證

| 操作 | 訊息 | 結果 |
| --- | --- | --- |
| 建立付款記錄 | "付款記錄已建立" | ✅ |
| 驗證付款記錄 | "付款記錄已驗證" | ✅ |
| 駁回付款記錄 | "付款記錄已駁回" | ✅ |
| 連結付款記錄 | "付款記錄已連結帳單" | ✅ |
| 建立電表 | "電表已建立" | ✅ |
| 建立電費單 | "電費單已建立" | ✅ |
| 標記 calculated | "電費單已標記為 calculated" | ✅ |
| 回寫電費 | "電費已回寫月帳單" | ✅ |
| 建立水費單 | "水費單已建立" | ✅ |
| 回寫水費 | "水費已回寫月帳單" | ✅ |

---

## 建議修正優先順序

1. **E-1 / E-2 / W-1**: electricity 與 water 的 list 頁面 property_id 改為顯示 property.name（P1，影響使用者體驗）
2. **E-3**: bill_detail 表頭改中文（P2，改善可讀性）
3. **B-1 / B-2 / R-1 / R-2**: billing list 與 monthly report 補上 public_electricity / other_charges 欄位（P2，完整性）
