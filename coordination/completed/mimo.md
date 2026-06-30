# mimo Completed Log

## 2026-06-30: Phase 3 UI/API Regression收尾

- Branch: `agent/mimo-phase3-ui-api-regression-01`
- Base: `codex-phase2-mainline-01`
- Checked 8 payment pages, 8 API endpoints, 3 LINE webhook scenarios
- Fixed 8 files (7 template + 1 handler) — all polish/consistency, no contract changes
- Fixed: English labels → Chinese in review_form/link_form, amount formatting, error page titles, OCR block overflow, API error messages language consistency
- Tests: 62 passed, 15 skipped (baseline maintained)
- No blockers, no incidents
- 交付 docs/reports/mimo-phase3-ui-api-regression-01.md

## 2026-06-28: Initial Report Delivery

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

## 2026-06-29: Phase 2 UI Regression Round 3

- water/list.html: property_id → property.name
- electricity/bill_detail.html: English headers → Chinese (用電量/計算金額/確認金額)
- payments/list.html: +bank_name, +account_number, +transaction_id
- reports/monthly.html: +public_electricity, +other_desc
- report_repository.py: +public_electricity, +other_desc query
- Created 3 incidents for Codex blockers:
  - report_service.py missing public_electricity/other_desc
  - ElectricityMeter/ElectricityBill missing property relationship
  - Maintenance module missing CRUD routes
- 交付 docs/reports/mimo-phase2-ui-regression-03.md

## 2026-06-29: Phase 2 UI Regression Round 4

- Base: `codex-phase2-mainline-01`
- Verified all 10 pages on mainline branch
- Confirmed all previous blockers resolved:
  - report_service.py: public_electricity/other_desc ✅
  - ElectricityMeter/ElectricityBill: property relationship ✅
  - Maintenance module: Full CRUD + status transitions ✅
- No template fixes needed
- No incidents created
- 交付 docs/reports/mimo-phase2-ui-regression-04.md

## 2026-06-29: Maintenance Phase 2B UI Regression Round 5

- Base: `codex-phase2-mainline-01`
- Verified all 6 maintenance pages
- Fixed status labels to Chinese throughout:
  - maintenance/index.html: status column, breakdown cards, transition buttons
  - reports/maintenance.html: status column
  - maintenance/forms.py: filter status choices
  - reports/forms.py: report filter status choices
- Tests: 35 passed, 15 skipped (maintains baseline)
- 交付 docs/reports/mimo-maintenance-ui-regression-05.md

## 2026-06-29: Phase 2 UI Regression Round 5

- Base: `codex-phase2-mainline-01`
- Verified new workflow pages: electricity property detail, reading-log
- Fixed status labels to Chinese:
  - property_detail.html: summary cards (待處理/已計算/已回寫)
  - reading_log.html: table headers (抄表編號/帳單編號)
  - billing/list.html: title (帳單管理) and contract link (合約)
  - payments/list.html: status labels (待審核/已驗證/已連結/已駁回)
- Tests: 41 passed, 15 skipped (maintains baseline)
- 交付 docs/reports/mimo-phase2-ui-regression-05.md

## 2026-06-29: Phase 2 UI Regression Round 6

- Base: `codex-phase2-mainline-01`
- Verified migration / integration placeholder pages:
  - Error pages (404, 500, app_error)
  - Migration scripts (migration_index, maintenance_legacy_scan)
  - Integration placeholders (OCR, Sheets, LINE)
- All pages verified normal
- No template fixes needed (test compatibility)
- Tests: 44 passed, 15 skipped (maintains baseline)
- 交付 docs/reports/mimo-phase2-ui-regression-06.md

## 2026-06-29: Water Preview UI Regression

- Base: `codex-phase2-mainline-01`
- Verified water preview flow: list → preview → post
- Fixed copy to Chinese:
  - preview.html: "Water Bill" → "水費單"
  - post_form.html: "Water Bill" → "水費單"
  - forms.py: mode choices (shared_by_stay_days → 按居住天數分攤, independent_meter → 獨立水表)
- Tests: 46 passed, 15 skipped (maintains baseline)
- 交付 docs/reports/mimo-phase3-water-preview-ui-01.md
