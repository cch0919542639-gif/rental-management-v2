# UI Field Matrix

Date: 2026-06-28
Author: mimo

---

## Page: Dashboard

- Name: Dashboard
- Route: `/`
- Primary Module: `modules/dashboard` (or `core`)

| UI Section | Field Label | Display Variable | Source Module | Source Entity/Field | Empty State Rule | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Top Stats | 總房數 | room_count | repositories/room_repo | Room (count) | 顯示 0 | P2 | |
| Top Stats | 已出租 | occupied_count | repositories/room_repo | Room (count WHERE status='occupied') | 顯示 0 | P2 | 來源為 Room.status，非 tenant.name |
| Top Stats | 空房 | vacant_count | repositories/room_repo | Room (count WHERE status='vacant') | 顯示 0 | P2 | 來源為 Room.status |
| Top Stats | 本月应收 | month_revenue | repositories/billing_repo | MonthlyBill (sum WHERE year_month=current AND paid=0) | 顯示 0 | P0 | year_month 使用 YYYYMM 查詢，UI 顯示 YYYY-MM |
| Top Stats | 本月已收 | month_collected | repositories/billing_repo | MonthlyBill (sum WHERE year_month=current AND paid=1) | 顯示 0 | P0 | 同上 |
| Top Stats | 本月未繳 | month_unpaid | repositories/billing_repo | MonthlyBill (sum WHERE year_month=current AND paid=0) | 顯示 0 | P0 | |
| Recent Bills | 帳單列表 | bill_items | repositories/billing_repo | MonthlyBill + Contract + Room (JOIN, limit) | "暫無帳單" | P1 | |
| Recent Payments | 付款紀錄 | payment_items | repositories/payment_repo | PaymentRecord (order by created_at, limit) | "暫無付款紀錄" | P1 | |

### Unclear Or Duplicate Sources

- 舊系統 dashboard 的 year_month 格式在 app.py 與 app.aliyun.py 不同。新版需統一使用 core/year_month.py helper。
- 舊系統用 tenant.name 判定空房，新版改用 Room.status。

### High Risk Display Rules

- year_month 查詢必須使用 YYYYMM（DB 格式），UI 顯示使用 YYYY-MM（透過 year_month helper）。
- 月帳單總額計算公式：`total = rent + electricity_amount + public_electricity + water_amount + other_charges`（與 billing-contract.md 一致）。

---

## Page: Landlords

- Name: Landlords
- Route: `/landlords`
- Primary Module: `modules/landlords`

| UI Section | Field Label | Display Variable | Source Module | Source Entity/Field | Empty State Rule | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| List | 房東姓名 | landlord.name | repositories/landlord_repo | Landlord.name | "—" | P2 | |
| List | 聯絡電話 | landlord.phone | repositories/landlord_repo | Landlord.phone | "—" | P2 | |
| List | 電費帳號 | landlord.electricity_account | repositories/landlord_repo | Landlord.electricity_account | "—" | P2 | |
| List | 水費帳號 | landlord.water_account | repositories/landlord_repo | Landlord.water_account | "—" | P2 | |
| List | 電費費率類型 | landlord.electricity_rate_type | repositories/landlord_repo | Landlord.electricity_rate_type | "—" | P2 | |
| List | 電費費率 | landlord.electricity_rate | repositories/landlord_repo | Landlord.electricity_rate | "—" | P2 | |
| List | 水費費率類型 | landlord.water_rate_type | repositories/landlord_repo | Landlord.water_rate_type | "—" | P2 | |
| List | 水費費率 | landlord.water_rate | repositories/landlord_repo | Landlord.water_rate | "—" | P2 | |
| List | 備註 | landlord.notes | repositories/landlord_repo | Landlord.notes | "—" | P2 | |
| List | 房產數量 | property_count | repositories/landlord_repo | Property (count WHERE landlord_id) | 顯示 0 | P2 | |
| Form (Create/Edit) | 姓名 | form.name | modules/landlords/forms | Landlord.name | 必填 | P2 | |
| Form | 電話 | form.phone | modules/landlords/forms | Landlord.phone | 選填 | P2 | |
| Form | 電費帳號 | form.electricity_account | modules/landlords/forms | Landlord.electricity_account | 選填 | P2 | |
| Form | 水費帳號 | form.water_account | modules/landlords/forms | Landlord.water_account | 選填 | P2 | |
| Form | 電費費率類型 | form.electricity_rate_type | modules/landlords/forms | Landlord.electricity_rate_type | 選填 | P2 | |
| Form | 電費費率 | form.electricity_rate | modules/landlords/forms | Landlord.electricity_rate | 選填 | P2 | |
| Form | 水費費率類型 | form.water_rate_type | modules/landlords/forms | Landlord.water_rate_type | 選填 | P2 | |
| Form | 水費費率 | form.water_rate | modules/landlords/forms | Landlord.water_rate | 選填 | P2 | |
| Form | 備註 | form.notes | modules/landlords/forms | Landlord.notes | 選填 | P2 | |

### Unclear Or Duplicate Sources

- Landlord 不含 address 欄位。address 屬於 Property。若 UI 需顯示地址，需 JOIN Property。

### High Risk Display Rules

- Landlord 預設費率可被合約費率覆蓋（core-entities.md 規則）。

---

## Page: Properties / Rooms

- Name: Properties & Rooms
- Route: `/rooms` (rooms list), `/properties/<pid>/rooms/create` (room create)
- Primary Module: `modules/rooms`, `modules/properties`

| UI Section | Field Label | Display Variable | Source Module | Source Entity/Field | Empty State Rule | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Room List | 房號 | room.room_number | repositories/room_repo | Room.room_number | "—" | P2 | 同一 property_id 下唯一 |
| Room List | 所屬房產 | property.name | repositories/room_repo | Property.name (JOIN) | "—" | P2 | |
| Room List | 所屬房東 | landlord.name | repositories/room_repo | Landlord.name (JOIN) | "—" | P2 | |
| Room List | 狀態 | room.status | repositories/room_repo | Room.status | "—" | P0 | 僅允許 vacant/occupied |
| Room List | 月租金 | room.rent | repositories/room_repo | Room.rent | "—" | P2 | |
| Room List | 押金 | room.deposit | repositories/room_repo | Room.deposit | "—" | P2 | |
| Room List | 面積（坪） | room.area_ping | repositories/room_repo | Room.area_ping | "—" | P2 | |
| Room List | 目前房客 | current_tenant | repositories/room_repo | Tenant.name (JOIN via Contract) | "暫無房客" | P1 | 需透過 active Contract 查詢 |
| Room List | 合約到期日 | contract_end_date | repositories/room_repo | Contract.end_date (JOIN, WHERE status='active') | "—" | P1 | |
| Room List | 備註 | room.notes | repositories/room_repo | Room.notes | "—" | P2 | |
| Room Form | 房號 | form.room_number | modules/rooms/forms | Room.room_number | 必填 | P2 | 同一 property_id 下唯一 |
| Room Form | 月租金 | form.rent | modules/rooms/forms | Room.rent | 必填 | P2 | |
| Room Form | 押金 | form.deposit | modules/rooms/forms | Room.deposit | 選填 | P2 | |
| Room Form | 面積（坪） | form.area_ping | modules/rooms/forms | Room.area_ping | 選填 | P2 | |
| Room Form | 狀態 | form.status | modules/rooms/forms | Room.status | 預設 vacant | P0 | 僅允許 vacant/occupied |
| Room Form | 備註 | form.notes | modules/rooms/forms | Room.notes | 選填 | P2 | |

### Unclear Or Duplicate Sources

- 舊系統 Room.status 可能含非標準值（如「待修」）。新版僅允許 vacant/occupied，待修獨立處理。
- 舊系統 occupancy 由 tenant.name 關鍵字驅動，新版改由 Room.status + Contract.status 為 single source of truth。

### High Risk Display Rules

- Room.status 僅接受 `vacant` / `occupied`。待修狀態需由獨立 maintenance 模組管理，不得寫入 Room.status 或 tenant.name。
- 判斷「目前房客」需透過 active Contract（status='active'），而非直接查 Room。

---

## Page: Tenants

- Name: Tenants
- Route: `/tenants`
- Primary Module: `modules/tenants`

| UI Section | Field Label | Display Variable | Source Module | Source Entity/Field | Empty State Rule | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| List | 房客姓名 | tenant.name | repositories/tenant_repo | Tenant.name | "—" | P1 | 需排除虛擬 tenant（清理後不再存在） |
| List | 聯絡電話 | tenant.phone | repositories/tenant_repo | Tenant.phone | "—" | P2 | |
| List | 身份證號 | tenant.id_number | repositories/tenant_repo | Tenant.id_number | "—" | P2 | |
| List | 緊急聯絡人 | tenant.emergency_contact | repositories/tenant_repo | Tenant.emergency_contact | "—" | P2 | |
| List | 緊急聯絡電話 | tenant.emergency_phone | repositories/tenant_repo | Tenant.emergency_phone | "—" | P2 | |
| List | 目前合約 | active_contract | repositories/tenant_repo | Contract (JOIN, WHERE status='active') | "無 active 合約" | P1 | |
| List | 目前房間 | current_room | repositories/tenant_repo | Room (JOIN via Contract) | "—" | P1 | |
| List | 備註 | tenant.notes | repositories/tenant_repo | Tenant.notes | "—" | P2 | |
| Form (Create/Edit) | 姓名 | form.name | modules/tenants/forms | Tenant.name | 必填 | P1 | 新版不得使用虛擬名稱 |
| Form | 電話 | form.phone | modules/tenants/forms | Tenant.phone | 選填 | P2 | |
| Form | 身份證號 | form.id_number | modules/tenants/forms | Tenant.id_number | 選填 | P2 | |
| Form | 緊急聯絡人 | form.emergency_contact | modules/tenants/forms | Tenant.emergency_contact | 選填 | P2 | |
| Form | 緊急聯絡電話 | form.emergency_phone | modules/tenants/forms | Tenant.emergency_phone | 選填 | P2 | |
| Form | 備註 | form.notes | modules/tenants/forms | Tenant.notes | 選填 | P2 | |

### Unclear Or Duplicate Sources

- 舊系統含虛擬 tenant（空房/待修/待補/倉庫/鐵皮），新版需全部清除或標記為 legacy。
- 虛擬 tenant 清理後，此頁面僅顯示真實房客。

### High Risk Display Rules

- 不得建立 name 為「空房」「待修」「待補」「倉庫」「鐵皮」的 tenant。
- 目前合約判斷使用 Contract.status='active'，不使用 Room.status。

---

## Page: Contracts

- Name: Contracts
- Route: `/contracts`
- Primary Module: `modules/contracts`

| UI Section | Field Label | Display Variable | Source Module | Source Entity/Field | Empty State Rule | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| List | 房客 | tenant.name | repositories/contract_repo | Tenant.name (JOIN) | "—" | P1 | |
| List | 房間 | room.room_number | repositories/contract_repo | Room.room_number (JOIN) | "—" | P2 | |
| List | 起始日 | contract.start_date | repositories/contract_repo | Contract.start_date | "—" | P2 | |
| List | 到期日 | contract.end_date | repositories/contract_repo | Contract.end_date | "—" | P1 | 用於判斷已到期合約 |
| List | 狀態 | contract.status | repositories/contract_repo | Contract.status | "—" | P1 | 僅 active/expired/terminated |
| List | 月租金 | contract.rent | repositories/contract_repo | Contract.rent | "—" | P2 | |
| List | 押金 | contract.deposit | repositories/contract_repo | Contract.deposit | "—" | P2 | |
| List | 電費費率 | contract.electricity_rate | repositories/contract_repo | Contract.electricity_rate | "—" | P2 | 可覆蓋房東預設 |
| List | 水費費率 | contract.water_rate | repositories/contract_repo | Contract.water_rate | "—" | P2 | 可覆蓋房東預設 |
| List | 起始電表讀數 | contract.start_electricity_reading | repositories/contract_repo | Contract.start_electricity_reading | "—" | P2 | |
| List | 起始水表讀數 | contract.start_water_reading | repositories/contract_repo | Contract.start_water_reading | "—" | P2 | |
| Form (Create/Edit) | 房客 | form.tenant_id | modules/contracts/forms | Tenant.id | 必填 | P1 | |
| Form | 房間 | form.room_id | modules/contracts/forms | Room.id | 必填 | P1 | 需檢查是否已有 active 合約 |
| Form | 起始日 | form.start_date | modules/contracts/forms | Contract.start_date | 必填 | P2 | |
| Form | 到期日 | form.end_date | modules/contracts/forms | Contract.end_date | 必填 | P1 | end_date 必須晚於 start_date |
| Form | 月租金 | form.rent | modules/contracts/forms | Contract.rent | 必填 | P2 | |
| Form | 押金 | form.deposit | modules/contracts/forms | Contract.deposit | 選填 | P2 | |
| Form | 電費費率 | form.electricity_rate | modules/contracts/forms | Contract.electricity_rate | 選填 | P2 | 若空，回退到房東預設 |
| Form | 水費費率 | form.water_rate | modules/contracts/forms | Contract.water_rate | 選填 | P2 | 若空，回退到房東預設 |
| Form | 起始電表讀數 | form.start_electricity_reading | modules/contracts/forms | Contract.start_electricity_reading | 選填 | P2 | |
| Form | 起始水表讀數 | form.start_water_reading | modules/contracts/forms | Contract.start_water_reading | 選填 | P2 | |
| Action | 終止合約 | contract_terminate | modules/contracts/routes | Contract.status → 'terminated' | — | P1 | 需同步更新 Room.status → vacant |

### Unclear Or Duplicate Sources

- 舊系統 Contract.status 可能含非正式值（如 draft），新版僅允許 active/expired/terminated。
- 同一房間只允許一個 active 合約，舊系統靠 UI 約束，新版需在 service 層驗證。

### High Risk Display Rules

- 終止合約時必須同步更新 Room.status 為 vacant。
- 已到期合約（end_date < today 且 status='active'）需由 batch job 或 service 定期修正為 expired。
- 合約費率為空時，回退到 Landlord 預設費率。

---

## Page: Monthly Bills

- Name: Monthly Bills
- Route: `/contracts/<cid>/bills`, `/bills/generate`
- Primary Module: `modules/billing`

| UI Section | Field Label | Display Variable | Source Module | Source Entity/Field | Empty State Rule | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Bill List | 月份 | bill.year_month (display) | repositories/billing_repo | MonthlyBill.year_month | "—" | P0 | DB 儲存 YYYYMM，UI 顯示 YYYY-MM |
| Bill List | 合約 | contract info | repositories/billing_repo | Contract + Tenant + Room (JOIN) | "—" | P1 | |
| Bill List | 房租 | bill.rent | repositories/billing_repo | MonthlyBill.rent | 0 | P2 | 來源：Contract.rent |
| Bill List | 電費（上期） | bill.electricity_prev | repositories/billing_repo | MonthlyBill.electricity_prev | "—" | P1 | |
| Bill List | 電費（本期） | bill.electricity_curr | repositories/billing_repo | MonthlyBill.electricity_curr | "—" | P1 | |
| Bill List | 用電量 | bill.electricity_usage | repositories/billing_repo | MonthlyBill.electricity_usage | "—" | P1 | |
| Bill List | 電費金額 | bill.electricity_amount | repositories/billing_repo | MonthlyBill.electricity_amount | 0 | P0 | 需與 ElectricityBill 來源一致 |
| Bill List | 公設電費 | bill.public_electricity | repositories/billing_repo | MonthlyBill.public_electricity | 0 | P0 | |
| Bill List | 水費（上期） | bill.water_prev | repositories/billing_repo | MonthlyBill.water_prev | "—" | P1 | |
| Bill List | 水費（本期） | bill.water_curr | repositories/billing_repo | MonthlyBill.water_curr | "—" | P1 | |
| Bill List | 用水量 | bill.water_usage | repositories/billing_repo | MonthlyBill.water_usage | "—" | P1 | |
| Bill List | 水費金額 | bill.water_amount | repositories/billing_repo | MonthlyBill.water_amount | 0 | P1 | 需與 WaterBill 來源一致 |
| Bill List | 其他費用 | bill.other_charges | repositories/billing_repo | MonthlyBill.other_charges | 0 | P2 | |
| Bill List | 其他費用說明 | bill.other_desc | repositories/billing_repo | MonthlyBill.other_desc | "—" | P2 | |
| Bill List | 總額 | bill.total | repositories/billing_repo | MonthlyBill.total | 0 | P0 | total = rent + electricity_amount + public_electricity + water_amount + other_charges |
| Bill List | 已繳狀態 | bill.paid | repositories/billing_repo | MonthlyBill.paid | false | P1 | 需與 PaymentRecord reconciliation 一致 |
| Bill List | 繳費日期 | bill.paid_date | repositories/billing_repo | MonthlyBill.paid_date | "—" | P2 | |
| Bill List | 動作 | toggle_paid | modules/billing/routes | MonthlyBill.paid (flip) | — | P1 | 舊系統直接 flip boolean，新版需走 reconciliation service |
| Bill Form | 月份 | form.year_month | modules/billing/forms | MonthlyBill.year_month | 必填 | P0 | UI 接受 YYYY-MM，轉為 YYYYMM 存入 DB |
| Bill Form | 房租 | form.rent | modules/billing/forms | MonthlyBill.rent | 必填 | P2 | |
| Bill Form | 電費金額 | form.electricity_amount | modules/billing/forms | MonthlyBill.electricity_amount | 選填 | P0 | |
| Bill Form | 公設電費 | form.public_electricity | modules/billing/forms | MonthlyBill.public_electricity | 選填 | P0 | |
| Bill Form | 水費金額 | form.water_amount | modules/billing/forms | MonthlyBill.water_amount | 選填 | P1 | |
| Bill Form | 其他費用 | form.other_charges | modules/billing/forms | MonthlyBill.other_charges | 選填 | P2 | |
| Bill Form | 其他費用說明 | form.other_desc | modules/billing/forms | MonthlyBill.other_desc | 選填 | P2 | |
| Bill Form | 總額 | form.total | modules/billing/forms | MonthlyBill.total | 自動計算 | P0 | total = rent + electricity_amount + public_electricity + water_amount + other_charges |

### Unclear Or Duplicate Sources

- 舊系統 year_month 格式在 app.py 與 app.aliyun.py 不同，且有 9+ 處各自轉換。新版統一由 core/year_month.py helper 處理。
- 舊系統月帳單總額計算含/不含 public_electricity 在不同變體中不一致。
- management_fee 不是 billing-contract.md 正式欄位，不列入正式來源。

### High Risk Display Rules

- year_month 格式：DB 固定 YYYYMM，UI/API 使用 YYYY-MM，轉換集中在 core/year_month.py。
- 月帳單總額公式：`total = rent + electricity_amount + public_electricity + water_amount + other_charges`（與 billing-contract.md 一致）。
- paid 狀態需與 PaymentRecord reconciliation 結果一致，不再直接 flip boolean。

---

## Page: Electricity

- Name: Electricity
- Route: `/electricity/`
- Primary Module: `modules/electricity`

| UI Section | Field Label | Display Variable | Source Module | Source Entity/Field | Empty State Rule | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Property List | 房產名稱 | property.name | repositories/electricity_repo | Property.name | "—" | P2 | |
| Property List | 電表數量 | meter_count | repositories/electricity_repo | ElectricityMeter (count WHERE property_id) | 顯示 0 | P1 | 不再硬編碼 meter_id=1 |
| Property List | 本月電費 | month_total | repositories/electricity_repo | ElectricityBill (sum WHERE year_month) | 顯示 0 | P0 | |
| Bill Detail | 月份 | bill.year_month (display) | repositories/electricity_repo | ElectricityBill.year_month | "—" | P0 | DB YYYYMM, UI YYYY-MM |
| Bill Detail | 電表 | meter info | repositories/electricity_repo | ElectricityMeter (JOIN) | "—" | P1 | |
| Bill Detail | 本期讀數 | reading.current | repositories/electricity_repo | ElectricityReading.current_reading | "—" | P1 | |
| Bill Detail | 上期讀數 | reading.previous | repositories/electricity_repo | ElectricityReading.previous_reading | "—" | P1 | |
| Bill Detail | 用電量 | usage_kwh | repositories/electricity_repo | ElectricityReading (計算) | "—" | P1 | |
| Bill Detail | 計費方式 | calc_method | repositories/electricity_repo | CalcMethod.name | "—" | P1 | |
| Bill Detail | 電費金額 | bill.amount | repositories/electricity_repo | ElectricityBill.amount | 0 | P0 | |
| Bill Detail | 公設電費 | bill.public_amount | repositories/electricity_repo | ElectricityBill.public_amount | 0 | P0 | |
| Bill Detail | 狀態 | bill.status | repositories/electricity_repo | ElectricityBill.status | pending | P1 | 僅 pending/calculated |
| Bill Form | 月份 | form.year_month | modules/electricity/forms | ElectricityBill.year_month | 必填 | P0 | UI YYYY-MM, DB YYYYMM |
| Bill Form | 電表 | form.meter_id | modules/electricity/forms | ElectricityMeter.id | 必填 | P0 | 不再硬編碼 meter_id=1 |
| Bill Form | 本期讀數 | form.current_reading | modules/electricity/forms | ElectricityReading.current_reading | 必填 | P1 | |
| Quick Reading | 電表選擇 | meter_select | modules/electricity/routes | ElectricityMeter (list) | — | P0 | 需列出所有電表，不硬編碼 |

### Unclear Or Duplicate Sources

- 舊系統 electricity_bp.py 硬編碼 meter_id=1，多電表場域直接錯誤。新版需從 ElectricityMeter 動態查詢。
- 舊系統 year_month 在 electricity_bills 表同樣有格式不一致問題。

### High Risk Display Rules

- year_month 轉換統一由 core/year_month.py 處理。
- 電表 ID 必須從 ElectricityMeter 查詢取得，禁止硬編碼。
- 計費公式（ct_meter_proportional / dual_meter_tou）需抽取到 services/electricity_calculator.py。

---

## Page: Water

- Name: Water Bills
- Route: `/water/bills`
- Primary Module: `modules/water`

| UI Section | Field Label | Display Variable | Source Module | Source Entity/Field | Empty State Rule | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Bill List | 房產 | property.name | repositories/water_repo | Property.name (JOIN) | "—" | P2 | |
| Bill List | 帳期起始 | bill.billing_start | repositories/water_repo | WaterBill.billing_start | "—" | P1 | 正式欄位，非 period |
| Bill List | 帳期結束 | bill.billing_end | repositories/water_repo | WaterBill.billing_end | "—" | P1 | |
| Bill List | 總金額 | bill.total_amount | repositories/water_repo | WaterBill.total_amount | 0 | P1 | 正式欄位，非 amount |
| Bill List | 主表上期 | bill.meter_prev_1 | repositories/water_repo | WaterBill.meter_prev_1 | "—" | P2 | |
| Bill List | 主表本期 | bill.meter_curr_1 | repositories/water_repo | WaterBill.meter_curr_1 | "—" | P2 | |
| Bill List | 分表讀數 | bill.sub_meter_1 | repositories/water_repo | WaterBill.sub_meter_1 | "—" | P2 | |
| Bill List | 實際用量 | bill.actual_usage_1 | repositories/water_repo | WaterBill.actual_usage_1 | "—" | P2 | |
| Bill List | 備註 | bill.notes | repositories/water_repo | WaterBill.notes | "—" | P2 | |
| Bill Form | 房產 | form.property_id | modules/water/forms | Property.id | 必填 | P2 | |
| Bill Form | 帳期起始 | form.billing_start | modules/water/forms | WaterBill.billing_start | 必填 | P1 | |
| Bill Form | 帳期結束 | form.billing_end | modules/water/forms | WaterBill.billing_end | 必填 | P1 | billing_end 必須晚於 billing_start |
| Bill Form | 總金額 | form.total_amount | modules/water/forms | WaterBill.total_amount | 必填 | P1 | 不可小於 0 |
| Bill Form | 主表上期 | form.meter_prev_1 | modules/water/forms | WaterBill.meter_prev_1 | 選填 | P2 | |
| Bill Form | 主表本期 | form.meter_curr_1 | modules/water/forms | WaterBill.meter_curr_1 | 選填 | P2 | |
| Bill Form | 分表讀數 | form.sub_meter_1 | modules/water/forms | WaterBill.sub_meter_1 | 選填 | P2 | |
| Bill Form | 實際用量 | form.actual_usage_1 | modules/water/forms | WaterBill.actual_usage_1 | 選填 | P2 | |
| Bill Form | 備註 | form.notes | modules/water/forms | WaterBill.notes | 選填 | P2 | |

### Unclear Or Duplicate Sources

- 舊系統 water_bill.py 計算公式混在 route 中。新版需抽取到 service 層。
- WaterBill 為物件層級帳單，水費 service 需將分攤結果回寫到 MonthlyBill.water_amount。

### High Risk Display Rules

- 水費分攤公式（shared_by_stay_days）需抽取到 services/water_service.py。
- 水費回寫 MonthlyBill 時，year_month 格式固定為 YYYYMM。
- 若為單水表物件，第二組 meter 欄位（meter_prev_2, meter_curr_2, sub_meter_2, actual_usage_2）可為空或 0。

---

## Page: Payments

- Name: Payments
- Route: `/payments`, `/api/payment-records`
- Primary Module: `modules/payments`

| UI Section | Field Label | Display Variable | Source Module | Source Entity/Field | Empty State Rule | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Record List | 金額 | record.amount | repositories/payment_repo | PaymentRecord.amount | "—" | P1 | |
| Record List | 付款日期 | record.transaction_date | repositories/payment_repo | PaymentRecord.transaction_date | "—" | P1 | |
| Record List | 付款人 | record.payer_name | repositories/payment_repo | PaymentRecord.payer_name | "—" | P2 | |
| Record List | 銀行 | record.bank_name | repositories/payment_repo | PaymentRecord.bank_name | "—" | P2 | |
| Record List | 帳戶 | record.account_number | repositories/payment_repo | PaymentRecord.account_number | "—" | P2 | |
| Record List | 交易編號 | record.transaction_id | repositories/payment_repo | PaymentRecord.transaction_id | "—" | P1 | 若存在應盡量唯一 |
| Record List | 狀態 | record.record_status | repositories/payment_repo | PaymentRecord.record_status | pending | P1 | 僅 pending/verified/rejected/linked |
| Record List | 狀態說明 | record.status_text | repositories/payment_repo | PaymentRecord.status_text | "—" | P2 | |
| Record List | 關聯合約 | contract info | repositories/payment_repo | Contract + Tenant (JOIN) | "未關聯" | P1 | contract_id 可為空 |
| Record List | 關聯帳單 | bill info | repositories/payment_repo | MonthlyBill (JOIN) | "未關聯" | P1 | monthly_bill_id 可為空 |
| Record List | 備註 | record.notes | repositories/payment_repo | PaymentRecord.notes | "—" | P2 | |
| Record Detail | OCR 原文 | record.raw_ocr_text | repositories/payment_repo | PaymentRecord.raw_ocr_text | "—" | P2 | |
| Record Detail | LLM 回應 | record.raw_llm_response | repositories/payment_repo | PaymentRecord.raw_llm_response | "—" | P2 | |
| Record Detail | 圖片路徑 | record.image_path | repositories/payment_repo | PaymentRecord.image_path | "—" | P2 | |
| Record Detail | OCR 引擎 | record.ocr_engine | repositories/payment_repo | PaymentRecord.ocr_engine | "—" | P2 | |
| Record Detail | 審核人 | verified_by.name | repositories/payment_repo | User.name (JOIN) | "—" | P2 | |
| Record Detail | 審核時間 | record.verified_at | repositories/payment_repo | PaymentRecord.verified_at | "—" | P2 | |
| Action | 審核通過 | api_verify_payment | modules/payments/routes | record_status → 'verified' | — | P1 | 需更新 MonthlyBill.paid |
| Action | 拒絕 | api_verify_payment | modules/payments/routes | record_status → 'rejected' | — | P1 | |
| Action | 對帳連結 | reconciliation | modules/payments/routes | record_status → 'linked' + 設定 contract_id/monthly_bill_id | — | P1 | |

### Unclear Or Duplicate Sources

- PaymentRecord 表為空（0 rows），無歷史資料需遷移。Schema 已完整定義。
- 舊系統 /payment/new 等 route 使用不存在的 Payment class（死碼），新版不實作。
- PaymentRecord.contract 的 backref 名為 payments（與不存在的 Payment class 同名），新版改為 payment_records。

### High Risk Display Rules

- record_status 僅接受 pending/verified/rejected/linked。
- 付款狀態變更需同步更新 MonthlyBill.paid（透過 reconciliation service）。
- OCR/LINE 流程寫入 PaymentRecord，管理 UI 使用 PaymentRecord（非 Payment）。
- amount 不可為負值。

---

## Page: Monthly Report

- Name: Monthly Report
- Route: `/reports/monthly`
- Primary Module: `modules/reports`

| UI Section | Field Label | Display Variable | Source Module | Source Entity/Field | Empty State Rule | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Filter | 月份 | filter_year_month | modules/reports/routes | year_month (YYYY-MM) | 預設本月 | P0 | UI 接受 YYYY-MM |
| Header | 報表月份 | report_month | modules/reports/routes | — | — | P0 | |
| Summary | 總房數 | total_rooms | repositories/report_repo | Room (count) | 0 | P2 | |
| Summary | 已出租 | occupied_rooms | repositories/report_repo | Room (count WHERE status='occupied') | 0 | P0 | 使用 Room.status |
| Summary | 空房 | vacant_rooms | repositories/report_repo | Room (count WHERE status='vacant') | 0 | P0 | 使用 Room.status |
| Summary | 應收總額 | total_revenue | repositories/report_repo | MonthlyBill (sum WHERE year_month) | 0 | P0 | 需與 data_contract 一致 |
| Summary | 已收總額 | total_collected | repositories/report_repo | MonthlyBill (sum WHERE year_month AND paid=1) | 0 | P0 | |
| Summary | 未繳總額 | total_unpaid | repositories/report_repo | MonthlyBill (sum WHERE year_month AND paid=0) | 0 | P0 | |
| Detail | 房東 | landlord.name | repositories/report_repo | Landlord.name (JOIN) | "—" | P2 | |
| Detail | 房產 | property.name | repositories/report_repo | Property.name (JOIN) | "—" | P2 | |
| Detail | 房間 | room.room_number | repositories/report_repo | Room.room_number (JOIN) | "—" | P2 | |
| Detail | 房客 | tenant.name | repositories/report_repo | Tenant.name (JOIN via Contract) | "空房" | P1 | 顯示 tenant.name，非用於判定 occupancy |
| Detail | 月租金 | rent | repositories/report_repo | MonthlyBill.rent | 0 | P2 | |
| Detail | 電費金額 | electricity_amount | repositories/report_repo | MonthlyBill.electricity_amount | 0 | P0 | |
| Detail | 公設電費 | public_electricity | repositories/report_repo | MonthlyBill.public_electricity | 0 | P0 | |
| Detail | 水費金額 | water_amount | repositories/report_repo | MonthlyBill.water_amount | 0 | P1 | |
| Detail | 其他費用 | other_charges | repositories/report_repo | MonthlyBill.other_charges | 0 | P2 | |
| Detail | 其他說明 | other_desc | repositories/report_repo | MonthlyBill.other_desc | "—" | P2 | |
| Detail | 總額 | total | repositories/report_repo | MonthlyBill.total | 0 | P0 | total = rent + electricity_amount + public_electricity + water_amount + other_charges |
| Detail | 已繳 | paid | repositories/report_repo | MonthlyBill.paid | false | P1 | |

### Unclear Or Duplicate Sources

- 舊系統 report_monthly() 使用 tenant.name 關鍵字判定空房（待補/待修/空房/倉庫/鐵皮），新版改用 Room.status + Contract.status。
- 舊系統 app.py 與 app.aliyun.py 實作不同（app.py 用 DummyBill，app.aliyun.py 用 JOIN），新版統一為 JOIN 查詢。

### High Risk Display Rules

- 空房判定使用 Room.status='vacant'，不使用 tenant.name 關鍵字。
- tenant.name 僅用於顯示房客姓名，不參與 occupancy 判定。
- 月報總額公式：`total = rent + electricity_amount + public_electricity + water_amount + other_charges`。

---

## Page: Landlord Report

- Name: Landlord Report
- Route: `/reports/landlord-report`
- Primary Module: `modules/reports`（孤立報表，舊版未註冊）

| UI Section | Field Label | Display Variable | Source Module | Source Entity/Field | Empty State Rule | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Filter | 房東 | filter_landlord | modules/reports/routes | Landlord.id | 必填 | P1 | |
| Filter | 月份 | filter_year_month | modules/reports/routes | year_month (YYYY-MM) | 預設本月 | P1 | |
| Summary | 房東姓名 | landlord.name | repositories/report_repo | Landlord.name | "—" | P2 | |
| Summary | 房產數 | property_count | repositories/report_repo | Property (count WHERE landlord_id) | 0 | P2 | |
| Summary | 總房間數 | room_count | repositories/report_repo | Room (count, JOIN via Property) | 0 | P2 | |
| Summary | 應收總額 | total_revenue | repositories/report_repo | MonthlyBill (sum, JOIN via Contract) | 0 | P1 | |
| Summary | 已收總額 | total_collected | repositories/report_repo | MonthlyBill (sum WHERE paid=1) | 0 | P1 | |
| Summary | 未繳總額 | total_unpaid | repositories/report_repo | MonthlyBill (sum WHERE paid=0) | 0 | P1 | |
| Detail | 房產 | property.name | repositories/report_repo | Property.name | "—" | P2 | |
| Detail | 房間 | room.room_number | repositories/report_repo | Room.room_number | "—" | P2 | |
| Detail | 房客 | tenant.name | repositories/report_repo | Tenant.name (JOIN via Contract) | "空房" | P1 | |
| Detail | 月租金 | rent | repositories/report_repo | MonthlyBill.rent | 0 | P2 | |
| Detail | 電費金額 | electricity_amount | repositories/report_repo | MonthlyBill.electricity_amount | 0 | P1 | |
| Detail | 公設電費 | public_electricity | repositories/report_repo | MonthlyBill.public_electricity | 0 | P1 | |
| Detail | 水費金額 | water_amount | repositories/report_repo | MonthlyBill.water_amount | 0 | P1 | |
| Detail | 其他費用 | other_charges | repositories/report_repo | MonthlyBill.other_charges | 0 | P1 | |
| Detail | 總額 | total | repositories/report_repo | MonthlyBill.total | 0 | P1 | total = rent + electricity_amount + public_electricity + water_amount + other_charges |
| Detail | 已繳 | paid | repositories/report_repo | MonthlyBill.paid | false | P1 | |

### Unclear Or Duplicate Sources

- 此報表在舊版為孤立報表：landlord_report.py Blueprint 定義完整但從未被 app.register_blueprint() 掛載。
- 新版需重新設計並正式掛載到 reports 模組。

### High Risk Display Rules

- 此報表為孤立功能，無舊版實際使用數據可對照。
- 總額公式：`total = rent + electricity_amount + public_electricity + water_amount + other_charges`。

---

## Cross-Cutting: year_month Format Rules

| Context | Format | Conversion | Source |
| --- | --- | --- | --- |
| DB (monthly_bills, electricity_bills) | YYYYMM (e.g., 202606) | — | reasonix architecture decision |
| UI (all pages) | YYYY-MM (e.g., 2026-06) | core/year_month.py → to_ui() | reasonix architecture decision |
| API input | YYYY-MM | core/year_month.py → to_db() | reasonix architecture decision |
| Form input | YYYY-MM | modules route → to_db() | reasonix architecture decision |

## Cross-Cutting: Status Enums

| Entity | Field | Allowed Values | Source |
| --- | --- | --- | --- |
| Room | status | vacant, occupied | status-machines.md |
| Contract | status | active, expired, terminated | status-machines.md |
| PaymentRecord | record_status | pending, verified, rejected, linked | status-machines.md |
| ElectricityBill | status | pending, calculated | status-machines.md |
| MonthlyBill | paid | false, true | status-machines.md |
| User | role | admin, landlord, viewer | status-machines.md |

## Cross-Cutting: Total Formula

`MonthlyBill.total = rent + electricity_amount + public_electricity + water_amount + other_charges`

Source: billing-contract.md

## Cross-Cutting: Dead Code Exclusions

The following are NOT part of the new system and must not appear in any UI:

- `/payment/new` — uses non-existent Payment class (dead code)
- `/payment/history` — uses non-existent Payment class (dead code)
- `/admin/payments` — uses non-existent Payment class (dead code)
- `/admin/payment/<pid>/confirm` — uses non-existent Payment class (dead code)
- `/admin/payment/<pid>/cancel` — uses non-existent Payment class (dead code)
- Virtual tenant names (空房/待修/待補/倉庫/鐵皮) — not a valid occupancy mechanism
- `MonthlyBill.management_fee` — not in billing-contract.md formal fields
