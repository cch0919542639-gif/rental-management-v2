# billing module

## 責任

- 月帳單生成
- 帳單重算
- 帳單總額一致性

## 依賴文件

- `../../../data_contracts/billing-contract.md`
- `../../../data_contracts/status-machines.md`

## 第一批要做

- `year_month` 轉換 helper
- monthly bill service
- total calculation policy

## 注意

- 不可在 route 或 template 拼接帳單總額
