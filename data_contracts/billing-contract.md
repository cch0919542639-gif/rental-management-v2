# Billing Contract

## 範圍

本文件定義 `MonthlyBill` 的格式、來源與總額規則。

## 正式實體

`MonthlyBill`

正式欄位：

- `id`
- `contract_id`
- `year_month`
- `rent`
- `electricity_prev`
- `electricity_curr`
- `electricity_usage`
- `electricity_amount`
- `public_electricity`
- `water_prev`
- `water_curr`
- `water_usage`
- `water_amount`
- `other_charges`
- `other_desc`
- `total`
- `paid`
- `paid_date`
- `notes`
- `created_at`

## 格式契約

### `year_month`

已確認舊 DB 實際資料為 `YYYYMM`，例如 `202606`。

新版決策：

- DB 儲存格式固定為 `YYYYMM`
- UI 輸入輸出可使用 `YYYY-MM`
- 所有 service / repository 需集中做格式轉換

禁止事項：

- 禁止在 template、route、service 各自隨手 `replace('-', '')`

### 唯一鍵

- `contract_id + year_month` 必須唯一

## 欄位來源規則

- `rent`
  - 預設來自 `Contract.rent`
- `electricity_*`
  - 來自電費 service 計算或人工確認值
- `water_*`
  - 來自水費 service 計算
- `other_charges`
  - 其他附加費用

## 水電草稿與入帳邊界

- 水電試算結果必須先存在 `UtilityCalculationDraft`；它不是 `MonthlyBill` 的替代品。
- 每張草稿必須且只能連結一張同類型來源水／電費單；草稿的物件、帳期與總額必須和來源帳單一致。
- `MonthlyBill.electricity_amount` 與 `MonthlyBill.water_amount` 只能由已確認草稿中、且明確對應該月帳單的水電 posting flow 更新。
- 草稿與水電單的分攤差額需分開保存；不得以 `other_charges` 或前期未收吸收差額。

## total 規則

正式公式：

`total = rent + electricity_amount + public_electricity + water_amount + other_charges + previous_balance`

要求：

- 由 service 統一計算
- 不允許 template 或 route 自行拼總額

## paid 契約

第一版延用布林值：

- `true`
- `false`

限制：

- `paid=true` 時可有 `paid_date`
- 若未來付款流程完整化，應逐步改為由 payment reconciliation 推導

## 已知風險

- 舊案以 `tenant.name` 關鍵字決定是否顯示空房，這不屬於帳單契約
- 舊 route 與表單對 `year_month` 的格式處理不一致
