# Status Machines

本文件定義第一批正式狀態集合與狀態語義。

## User.role

- `admin`
- `landlord`
- `viewer`

## Room.status

- `vacant`
- `occupied`

說明：

- `待修` 不屬於 room status
- 若需要維修狀態，後續應增設獨立欄位或 maintenance 模組

## Contract.status

- `active`
- `expired`
- `terminated`

轉換：

- `active -> expired`
- `active -> terminated`

限制：

- 不應從 `terminated` 回到 `active`，除非建立新合約

## MonthlyBill.paid

- `false`
- `true`

轉換：

- `false -> true`

限制：

- 若付款被撤銷，應由正式對帳流程處理，不建議隨意手動切回

## PaymentRecord.record_status

- `pending`
- `verified`
- `rejected`
- `linked`

建議轉換：

- `pending -> verified`
- `pending -> rejected`
- `verified -> linked`

## ElectricityBill.status

- `pending`
- `calculated`

建議轉換：

- `pending -> calculated`

說明：

- 若未來加入複核，可新增 `confirmed`

## 禁止事項

- 禁止以自由文字塞入 `status` 欄位
- 禁止在不同模組使用同名不同義的狀態
