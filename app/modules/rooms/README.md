# rooms module

## 責任

- 房間主資料 CRUD
- 房間狀態維護
- 房間與合約、電水 meter 的連結

## 依賴文件

- `../../../data_contracts/core-entities.md`
- `../../../data_contracts/status-machines.md`

## 第一批要做

- room uniqueness rule
- occupancy 狀態規則
- room status 與 contract status 的協調

## 注意

- 不可再透過 tenant 名稱推導空房
