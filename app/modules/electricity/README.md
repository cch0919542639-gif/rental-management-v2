# electricity module

## 責任

- 電費帳單
- 抄表資料
- 分攤與計算

## 依賴文件

- `../../../data_contracts/electricity-contract.md`
- `../../../data_contracts/billing-contract.md`

## 第一批要做

- calculation service registry
- main meter / room meter mapping
- monthly bill electricity posting

## 注意

- 不可硬編碼 meter id
- 不可把主要算法留在 route
