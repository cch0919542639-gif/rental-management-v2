# auth module

## 責任

- 登入/登出
- 使用者驗證
- 角色授權
- session / token 邊界

## 依賴文件

- `../../../data_contracts/auth-and-roles.md`
- `../../../data_contracts/core-entities.md`

## 第一批要做

- app auth entrypoint
- password hash policy
- role guard
- current user context

## 不負責

- 房東資料 CRUD
- 付款流程

## 驗收

- 角色權限可明確限制
- 不再有預設管理員自動建立行為
