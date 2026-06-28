# reports module

## 責任

- 月報表
- 房東報表
- 年度總覽
- 對帳與驗證輸出

## 依賴文件

- `../../../data_contracts/billing-contract.md`
- `../../../data_contracts/payments-contract.md`
- `../../../data_contracts/core-entities.md`

## 第一批要做

- report query layer
- reporting DTO / presenter
- 欄位格式統一

## 注意

- 報表不得再依賴 tenant 名稱關鍵字判斷空房
- 報表欄位要可回溯到資料契約與 query
