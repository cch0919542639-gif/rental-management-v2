# mimo Completed Log

## 2026-06-28: Initial Report Delivery

- 輸出檔案：`docs/reports/mimo-ui-field-matrix.md`, `docs/reports/mimo-test-scenarios.md`, `evidence/mimo-regression-checklist.md`
- 涵蓋 11 個頁面、40 個測試情境、完整回歸檢查表

## 2026-06-28: Contract Alignment Fixes

- 對齊 core-entities.md：
  - Room.number → Room.room_number
  - Room.rent_amount → Room.rent
  - Contract.rent_amount → Contract.rent
  - Landlord.address 移除（address 屬於 Property，非 Landlord）
  - Room 新增 deposit, area_ping, notes 欄位
  - Contract 新增 electricity_rate, water_rate, start_electricity_reading, start_water_reading 欄位
  - Tenant 新增 emergency_contact, emergency_phone, notes 欄位
  - Landlord 完整欄位對齊（electricity_account, water_account, electricity_rate_type, electricity_rate, water_rate_type, water_rate, notes）
- 對齊 billing-contract.md：
  - MonthlyBill.electricity → MonthlyBill.electricity_amount
  - MonthlyBill.water → MonthlyBill.water_amount
  - MonthlyBill.other_fee → MonthlyBill.other_charges
  - 移除 MonthlyBill.management_fee（非正式欄位）
  - 新增 electricity_prev, electricity_curr, electricity_usage, public_electricity, water_prev, water_curr, water_usage, other_desc, paid_date 欄位
  - 總額公式對齊：total = rent + electricity_amount + public_electricity + water_amount + other_charges
- 對齊 water-contract.md：
  - WaterBill.period → WaterBill.billing_start + billing_end
  - WaterBill.usage → WaterBill.actual_usage_1
  - WaterBill.amount → WaterBill.total_amount
  - WaterBill.paid 移除（WaterBill 無此欄位）
  - WaterBill.start_date/end_date → WaterBill.billing_start/billing_end
  - 新增 meter_prev_1, meter_curr_1, sub_meter_1, actual_usage_1 欄位
- 對齊 payments-contract.md：
  - 新增 status_text, raw_llm_response, image_path 欄位
- 對齊 status-machines.md：
  - 新增 ElectricityBill.status（pending/calculated）
  - 新增 MonthlyBill.paid 狀態機（false → true）
- 所有測試情境與回歸清單的欄位名稱、SQL、Evidence 表格同步修正

## 2026-06-28: Phase 1 UI Regression Round 2

- P1 修正 5 項（electricity/water property relationship + display）
- P2 gap 10 項已記錄
- 11 個頁面正常顯示、10 個 flash 訊息正確

## 2026-06-29: Phase 2 UI Gap Round 1

- billing/list.html：+public_electricity, +other_charges
- reports/monthly.html：+public_electricity, +other_desc
- payments/list.html：+bank_name, +account_number, +transaction_id
- report_repository.py：+public_electricity, +other_desc query
- report_service.py：+public_electricity, +other_desc return

## 2026-06-29: Phase 2 UI Polish Round 2

- water/list.html：property_id → property.name
- electricity/bill_detail.html：英文表頭改中文（用電量/計算金額/確認金額）
- payments/list.html：補齊銀行/帳戶/交易編號欄位（上一輪遺漏）
- reports/monthly.html：補齊公設電費/其他說明欄位（上一輪遺漏）
- report_repository.py：補齊 public_electricity/other_desc 查詢（上一輪遺漏）
- 建立 incident：report_service.py 需 Codex 補 public_electricity/other_desc 回傳
- 交付 docs/reports/mimo-ui-polish-02.md
