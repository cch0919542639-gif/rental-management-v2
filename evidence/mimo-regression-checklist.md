# Regression Checklist

Date: 2026-06-28
Author: mimo

---

## Manual Checks

### Auth & Dashboard

- [ ] 正常登入流程：使用 admin 帳號成功登入，重導向至 /dashboard
- [ ] 登入失敗：錯誤密碼時顯示錯誤訊息，session 未建立
- [ ] 登出：session 清除，重導向至 /login
- [ ] Dashboard 統計：總房數、已出租、空房數量正確（來源為 Room.status）
- [ ] Dashboard 月份切換：切換月份後統計正確更新

### Landlords

- [ ] Landlord List 顯示正確資料：姓名(name)、電話(phone)、電費帳號(electricity_account)、水費帳號(water_account)、電費費率類型(electricity_rate_type)、電費費率(electricity_rate)、水費費率類型(water_rate_type)、水費費率(water_rate)、備註(notes)、房產數量
- [ ] Landlord 不含 address 欄位：若需顯示地址，應 JOIN Property.address
- [ ] Landlord Create：表單驗證通過，資料正確寫入 DB
- [ ] Landlord Edit：資料正確更新
- [ ] Landlord Delete：確認刪除，關聯資料處理正確

### Properties / Rooms

- [ ] Room List 顯示正確資料：房號(room_number)、所屬房產、所屬房東、狀態(status)、月租金(rent)、押金(deposit)、面積(area_ping)、目前房客、合約到期日、備註(notes)
- [ ] Room.room_number 在同一 property_id 下唯一
- [ ] Room.status 僅顯示 vacant/occupied，無其他值
- [ ] Room Create：表單驗證通過，資料正確寫入 DB
- [ ] Room Edit：資料正確更新
- [ ] 空房顯示：Room.status='vacant' 的房間正確標示為空房

### Tenants

- [ ] Tenant List 顯示正確資料：姓名(name)、電話(phone)、身份證號(id_number)、緊急聯絡人(emergency_contact)、緊急聯絡電話(emergency_phone)、目前合約、目前房間、備註(notes)
- [ ] 無虛擬 tenant：tenants 表無 name 含「空房」「待修」「待補」「倉庫」「鐵皮」的紀錄
- [ ] Tenant Create：表單驗證通過，資料正確寫入 DB
- [ ] Tenant Edit：資料正確更新
- [ ] Tenant Delete：確認刪除，關聯資料處理正確

### Contracts

- [ ] Contract List 顯示正確資料：房客、房間(room_number)、起始日(start_date)、到期日(end_date)、狀態(status)、月租金(rent)、押金(deposit)、電費費率(electricity_rate)、水費費率(water_rate)、起始電表讀數(start_electricity_reading)、起始水表讀數(start_water_reading)
- [ ] Contract.status 僅顯示 active/expired/terminated
- [ ] Contract Create：表單驗證通過，Room.status 正確更新
- [ ] 同一房間唯一 active 合約：嘗試建立重複 active 合約時系統拒絕
- [ ] Contract.end_date 必須晚於 start_date：嘗試建立 end_date <= start_date 時系統拒絕
- [ ] 已到期合約：end_date < today 且 status='active' 的合約正確顯示
- [ ] 提前終止合約：Contract.status → 'terminated'，Room.status → 'vacant'
- [ ] 提前終止 — 當月帳單保留：合約終止後當月帳單不自動刪除
- [ ] 合約費率回退：Contract.electricity_rate 為空時，回退到 Landlord.electricity_rate

### Monthly Bills

- [ ] Bill List 顯示正確資料：月份(year_month)、合約、房租(rent)、電費上期(electricity_prev)、電費本期(electricity_curr)、用電量(electricity_usage)、電費金額(electricity_amount)、公設電費(public_electricity)、水費上期(water_prev)、水費本期(water_curr)、用水量(water_usage)、水費金額(water_amount)、其他費用(other_charges)、其他費用說明(other_desc)、總額(total)、已繳狀態(paid)、繳費日期(paid_date)
- [ ] year_month 格式：DB 顯示 YYYYMM，UI 顯示 YYYY-MM
- [ ] 月帳單總額公式：total = rent + electricity_amount + public_electricity + water_amount + other_charges（與 billing-contract.md 一致）
- [ ] management_fee 不在正式欄位中：Bill List 和 Bill Form 不顯示 management_fee
- [ ] Bill Create：表單驗證通過，year_month 正確轉換
- [ ] Bill Edit：資料正確更新
- [ ] Batch Bill Entry：多合約批次操作正確
- [ ] Bill Generate：所有 active contract 批次產生月帳單正確

### Electricity

- [ ] Electricity Property List 顯示正確資料：房產名稱、電表數量、本月電費
- [ ] Electricity Bill Detail 顯示正確資料：月份(year_month)、電表、本期讀數(current_reading)、上期讀數(previous_reading)、用電量、計費方式(calc_method)、電費金額(amount)、公設電費(public_amount)、狀態(status)
- [ ] ElectricityBill.status 僅顯示 pending/calculated
- [ ] 電表選擇不硬編碼 meter_id=1：快速抄表從 ElectricityMeter 動態列出
- [ ] 電費金額與來源一致：ElectricityBill.amount 正確顯示
- [ ] 共用電表：多房間共用同一電表時，各房間顯示正確的電表資訊

### Water

- [ ] Water Bill List 顯示正確資料：房產、帳期起始(billing_start)、帳期結束(billing_end)、總金額(total_amount)、主表上期(meter_prev_1)、主表本期(meter_curr_1)、分表讀數(sub_meter_1)、實際用量(actual_usage_1)、備註(notes)
- [ ] WaterBill 不使用非正式欄位：無 period、usage、amount、paid、start_date、end_date
- [ ] billing_end 必須晚於 billing_start：嘗試建立 billing_end <= billing_start 時系統拒絕
- [ ] total_amount 不可小於 0：嘗試建立 total_amount<0 時系統拒絕
- [ ] 單水表物件：第二組 meter 欄位（meter_prev_2, meter_curr_2, sub_meter_2, actual_usage_2）可為空或 0
- [ ] 水費回寫 MonthlyBill.water_amount：分攤結果正確寫入 MonthlyBill
- [ ] 水費回寫 year_month 格式：DB 固定 YYYYMM

### Payments

- [ ] Payment Record List 顯示正確資料：金額(amount)、付款日期(transaction_date)、付款人(payer_name)、銀行(bank_name)、帳戶(account_number)、交易編號(transaction_id)、狀態(record_status)、狀態說明(status_text)、關聯合約、關聯帳單、備註(notes)
- [ ] PaymentRecord.record_status 僅顯示 pending/verified/rejected/linked
- [ ] PaymentRecord 審核通過：record_status → 'verified'，verified_by_id 和 verified_at 設定
- [ ] PaymentRecord 拒絕：record_status → 'rejected'
- [ ] PaymentRecord 連結狀態：linked 時 contract_id 和 monthly_bill_id 已設定
- [ ] PaymentRecord 未關聯：pending 時顯示「未關聯」
- [ ] amount 不可為負值：嘗試建立 amount<0 時系統拒絕
- [ ] 付款狀態與 PaymentRecord 一致：MonthlyBill.paid 由 reconciliation service 推導，不直接 flip boolean
- [ ] 死碼路由不存在：/payment/new、/payment/history、/admin/payments、/admin/payment/<pid>/confirm、/admin/payment/<pid>/cancel 均返回 404

### Monthly Report

- [ ] 報表月份篩選正確
- [ ] 總房數、已出租、空房數量正確（來源為 Room.status）
- [ ] 應收總額與來源一致：SUM(MonthlyBill.total WHERE year_month)
- [ ] 已收總額與來源一致：SUM(MonthlyBill.total WHERE paid=1)
- [ ] 未繳總額與來源一致：SUM(MonthlyBill.total WHERE paid=0)
- [ ] 詳細資料正確顯示：房東、房產、房間(room_number)、房客、房租(rent)、電費金額(electricity_amount)、公設電費(public_electricity)、水費金額(water_amount)、其他費用(other_charges)、其他說明(other_desc)、總額(total)、已繳(paid)
- [ ] 空房判定使用 Room.status='vacant'，不使用 tenant.name 關鍵字

### Landlord Report（孤立報表）

- [ ] 舊版 /reports/landlord-report 無法存取（404，因 Blueprint 未註冊）
- [ ] 新版 Landlord Report 已重新設計並正式掛載到 reports 模組
- [ ] 報表總額與來源一致：SUM(MonthlyBill.total WHERE landlord_id)
- [ ] 房東篩選正確
- [ ] 月份篩選正確

---

## Focused Risks

- [ ] **year_month 格式**：所有頁面的 year_month 顯示均使用 YYYY-MM（透過 core/year_month.py to_ui()），DB 儲存均為 YYYYMM（透過 core/year_month.py to_db()）
- [ ] **Room.status 唯一來源**：occupancy 判定使用 Room.status（vacant/occupied），不使用 tenant.name 關鍵字
- [ ] **PaymentRecord 為唯一付款流程**：所有付款相關功能使用 PaymentRecord，不使用 Payment class（已刪除死碼）
- [ ] **虛擬 tenant 已清理**：tenants 表無「空房」「待修」「待補」「倉庫」「鐵皮」等虛擬名稱
- [ ] **待修獨立處理**：待修狀態由 maintenance 模組管理，不寫入 Room.status 或 tenant.name
- [ ] **電表不硬編碼**：所有電表相關功能從 ElectricityMeter 動態查詢，不硬編碼 meter_id=1
- [ ] **月帳單總額一致**：MonthlyBill.total = rent + electricity_amount + public_electricity + water_amount + other_charges（與 billing-contract.md 一致）
- [ ] **電費與來源一致**：MonthlyBill.electricity_amount = ElectricityBill.amount
- [ ] **水費與來源一致**：MonthlyBill.water_amount = WaterBill.total_amount 經分攤後寫入
- [ ] **WaterBill 欄位正確**：使用 billing_start/billing_end/total_amount/meter_prev_1/meter_curr_1/sub_meter_1/actual_usage_1，不使用 period/usage/amount/paid/start_date/end_date

---

## Required Evidence

| Check Item | Evidence Type | Evidence Location | Status |
| --- | --- | --- | --- |
| 正常登入 | Screenshot + Query | screenshot: auth/login.png, query: SELECT * FROM user WHERE username='admin' | |
| 空房顯示 | Screenshot + Query | screenshot: dashboard/vacant.png, query: SELECT COUNT(*) FROM rooms WHERE status='vacant' | |
| 待修房顯示 | Screenshot + Query | screenshot: rooms/maintenance.png, query: SELECT * FROM rooms WHERE maintenance_flag=true | |
| 新簽約當月帳單 | Screenshot + Query | screenshot: bills/new_contract.png, query: SELECT * FROM monthly_bills WHERE year_month='202606' | |
| 已到期合約 | Screenshot + Query | screenshot: contracts/expired.png, query: SELECT * FROM contracts WHERE end_date < date('now') AND status='active' | |
| 提前終止合約 | Screenshot + Query | screenshot: contracts/terminated.png, query: SELECT * FROM contracts WHERE status='terminated' | |
| 未繳帳單 | Screenshot + Query | screenshot: dashboard/unpaid.png, query: SELECT * FROM monthly_bills WHERE paid=0 | |
| 溢繳/對帳 | Screenshot + Query | screenshot: payments/reconciliation.png, query: SELECT * FROM payment_records WHERE record_status='linked' | |
| 共用電表 | Screenshot + Query | screenshot: electricity/shared.png, query: SELECT * FROM electricity_meters WHERE id IN (SELECT meter_id FROM room_meters GROUP BY meter_id HAVING COUNT(*) > 1) | |
| 共用水表 | Screenshot + Query | screenshot: water/shared.png, query: SELECT * FROM water_bills WHERE property_id IN (SELECT property_id FROM water_bills GROUP BY property_id HAVING COUNT(*) > 1) | |
| year_month 格式 | Query | query: SELECT DISTINCT length(year_month) FROM monthly_bills — 應全部為 6 | |
| PaymentRecord 狀態 | Query | query: SELECT record_status, COUNT(*) FROM payment_records GROUP BY record_status | |
| 月帳單總額一致 | Query | query: SELECT ym, rent, electricity_amount, public_electricity, water_amount, other_charges, total FROM monthly_bills WHERE year_month='202606' — 確認 total = rent + electricity_amount + public_electricity + water_amount + other_charges | |
| 電費一致 | Query | query: SELECT mb.id, mb.electricity_amount, eb.amount FROM monthly_bills mb JOIN electricity_bills eb ON ... — 比對 | |
| 水費一致 | Query | query: SELECT mb.id, mb.water_amount, wb.total_amount FROM monthly_bills mb JOIN water_bills wb ON ... — 比對 | |
| 月報總額一致 | Query | query: SELECT SUM(total) FROM monthly_bills WHERE year_month='202606' — 與月報顯示比對 | |
| 房東報表總額一致 | Query | query: SELECT SUM(mb.total) FROM monthly_bills mb JOIN contracts c ON ... WHERE c.landlord_id=? — 與房東報表比對 | |
| WaterBill 欄位正確 | Query | query: SELECT billing_start, billing_end, total_amount, meter_prev_1, meter_curr_1, sub_meter_1, actual_usage_1 FROM water_bills — 確認無 period/usage/amount/paid/start_date/end_date | |
