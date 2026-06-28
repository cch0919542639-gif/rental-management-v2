# Reports Contract

## 範圍

- 月報表
- 房東報表
- 年度總覽
- 之後的對帳輸出

## 核心原則

- 報表是查詢輸出，不是規則來源
- 報表不得自行發明欄位語義
- 每個顯示欄位都必須回溯到資料契約與 query/service

## 月報表契約

資料來源：

- `MonthlyBill`
- `Contract`
- `Room`
- `Property`
- `Landlord`
- `Tenant`

必要欄位：

- `year_month`
- `landlord`
- `property`
- `room_number`
- `tenant_name`
- `rent`
- `electricity_amount`
- `electricity_usage`
- `water_amount`
- `water_usage`
- `other_charges`
- `total`
- `paid`

規則：

- `year_month` UI 顯示 `YYYY-MM`
- 查詢層仍以 DB 格式 `YYYYMM`
- `tenant_name` 必須來自正式 tenant 或 occupancy presenter，不可用關鍵字修補

## 房東報表契約

目標：

- 依房東 -> 物件 -> 房間彙總
- 顯示已收/未收/欠款/異常項

規則：

- 欠款、已收、未收定義必須引用 `MonthlyBill` 與 `PaymentRecord` 正式狀態
- 不可直接依自由文字 notes 或 tenant 名稱判定異常

## 年度總覽契約

目標：

- 以月份維度展示 `total`、`paid`、`unpaid`

規則：

- 所有月份查詢必須經過統一的 `year_month` helper

## Presenter / DTO 規則

- 報表頁面不得直接吃 ORM 物件到處判斷
- 應由 `reports` 模組提供固定 DTO 或 presenter

## 驗收要求

- 每張報表都需有欄位說明
- 每張報表都需有至少一種驗證方法：
  - SQL 對帳
  - service assertion
  - 手工驗收清單

## 已知舊案問題

- 月報表把空房判定混在 tenant 名稱規則
- 房東報表透過 `from app import ...` 反向引用主程式
- 不同報表對 `year_month` 轉換方式不一致
