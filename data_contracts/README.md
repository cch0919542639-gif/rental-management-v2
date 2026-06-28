# data_contracts

核心表契約、欄位規則、狀態機、格式標準都放這裡。

## 第一批文件

- `core-entities.md`
- `auth-and-roles.md`
- `billing-contract.md`
- `electricity-contract.md`
- `payments-contract.md`
- `status-machines.md`

## 第二批文件

- `water-contract.md`
- `reports-contract.md`
- `integrations-contract.md`
- `migration-and-compatibility.md`

## 使用原則

- 這裡的格式與狀態定義優先於舊系統註解
- 若舊資料與契約不一致，先記錄在 incident，再規劃 migration
- 未寫入契約的隱性規則，不得直接實作成新版邏輯
