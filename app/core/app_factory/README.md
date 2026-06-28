# app_factory

## 責任

- 建立 Flask app 實例
- 載入 config
- 註冊 extensions
- 註冊模組/blueprints
- 初始化 error handlers 與 logging

## 第一批要做

- `create_app(config_name: str | None = None)`
- extension bootstrap
- module registration policy

## 禁止事項

- 不得在 import 時直接做 `db.create_all()`
- 不得在 app 啟動時自動建立預設帳號
