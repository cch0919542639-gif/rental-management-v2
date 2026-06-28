# Water Contract

## 範圍

- `WaterBill`
- 水費分攤規則
- 水費回寫 `MonthlyBill` 的契約

## 已確認事實

- 舊 ORM 存在 `WaterBill`
- 舊 `water_bill.py` 以居住天數分攤共用水表費用
- `water_bills` 目前資料量為 0
- 舊邏輯使用 `billing_start.strftime('%Y%m')` 回寫月帳單

## WaterBill 正式欄位

- `id`
- `property_id`
- `billing_start`
- `billing_end`
- `total_amount`
- `meter_prev_1`
- `meter_curr_1`
- `sub_meter_1`
- `actual_usage_1`
- `meter_prev_2`
- `meter_curr_2`
- `sub_meter_2`
- `actual_usage_2`
- `notes`
- `created_at`

## 契約規則

- `property_id` 不可為空
- `billing_end` 必須晚於 `billing_start`
- `total_amount` 不可小於 0
- 若為單水表物件，第二組 meter 欄位可為空或 0

## 分攤模式

第一版先支援：

- `shared_by_stay_days`
- `independent_meter`

說明：

- 舊案實作的是 `shared_by_stay_days`
- 若物件為獨立水表，應由帳單生成邏輯改走房間/合約讀數，不應硬套共用分攤

## shared_by_stay_days 規則

- 分母為帳期內所有有效居住天數總和
- 分子為單一合約在帳期內的實際居住天數
- 金額由 service 統一計算與四捨/進位規則控制

待明確化：

- 是否維持 `ROUND_UP`
- 是否允許最後一戶吸收尾差

## 與 MonthlyBill 的關聯

- `WaterBill` 是物件層級帳單
- `MonthlyBill` 是合約層級帳單
- 水費 service 需將分攤結果回寫到對應 `MonthlyBill.water_amount`

## year_month 契約

- 回寫 `MonthlyBill` 時，DB 格式固定為 `YYYYMM`
- 禁止 water route 自行決定儲存格式

## 已知舊案問題

- 舊 route 與 service 混在同檔
- 水費分攤與月帳單寫入缺少明確回滾策略
- `water_bills` 無現存資料，需先決定歷史補建方式
