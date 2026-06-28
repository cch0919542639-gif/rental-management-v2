# config

## 責任

- 管理執行環境設定
- 區分 dev / test / prod
- 管理 secrets 讀取規則

## 第一批要做

- base config
- env-based config
- secret validation

## 禁止事項

- 不得將 API key 寫死在 repo
- 不得讓測試與正式共用不安全預設值
