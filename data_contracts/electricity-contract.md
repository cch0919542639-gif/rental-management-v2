# Electricity Contract

## 範圍

- `CalcMethod`
- `ElectricityMeter`
- `ElectricityBill`
- `ElectricityReading`

## CalcMethod

正式欄位：

- `id`
- `name`
- `module_key`
- `description`
- `params_schema`
- `is_active`
- `created_at`

規則：

- `module_key` 必須唯一
- 新版計算方式必須由 service registry 管理，不可散落於 route

## ElectricityMeter

正式欄位：

- `id`
- `property_id`
- `is_main`
- `meter_number`
- `room_id`
- `room_number`
- `notes`
- `created_at`

規則：

- 一筆 meter 必須明確屬於主表或房間表
- 不接受 route 內硬編碼 `meter_id=1`

## ElectricityBill

正式欄位：

- `id`
- `property_id`
- `meter_id`
- `period_start`
- `period_end`
- `year_month`
- `prev_reading`
- `curr_reading`
- `total_usage`
- `total_amount`
- `public_amount`
- `flow_amount`
- `calc_method_id`
- `status`
- `ocr_raw_text`
- `notes`
- `created_at`
- `created_by`

第一版狀態：

- `pending`
- `calculated`

規則：

- `year_month` 與 `MonthlyBill` 一樣，DB 固定 `YYYYMM`
- `status` 只描述電費單自身處理狀態，不等於月帳單是否已入帳

## ElectricityReading

正式欄位：

- `id`
- `bill_id`
- `meter_id`
- `room_id`
- `prev_reading`
- `curr_reading`
- `usage`
- `calculated_amount`
- `confirmed_amount`
- `notes`
- `created_at`

規則：

- `confirmed_amount` 若存在，優先於 `calculated_amount`
- `usage` 不得為負值

## 計算邊界

- route 只收參數與回應結果
- 真正計算放在 `services/electricity_*`
- `dual_meter_tou`、`proportional_split` 這類算法要有獨立 service 與單元測試

## 已知舊案問題

- route 內混入公式
- 以 JSON 塞在 `bill.notes` 承載細分公電資料
- 建 bill/readings 時有硬編碼 meter id
