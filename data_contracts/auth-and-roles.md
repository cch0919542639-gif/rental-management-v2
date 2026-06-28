# Auth And Roles Contract

## 目標

定義新版登入、授權與角色可見範圍。

## 正式角色

- `admin`
- `landlord`
- `viewer`

## 角色權限草案

### admin

- 管理所有主資料
- 建立/修改合約
- 產生帳單
- 操作電費/水費/付款/報表
- 管理使用者

### landlord

- 查看自己名下 `Landlord` 的物件、房間、合約摘要、帳單與報表
- 不可跨房東讀取資料

### viewer

- 僅可讀取授權範圍頁面
- 不可寫入核心資料

## 資料關聯規則

- `role=landlord` 的使用者必須綁定 `landlord_id`
- `role=admin` 與 `viewer` 的 `landlord_id` 預設為空

## 禁止事項

- 禁止在 app 啟動時自動建立預設管理員帳號
- 禁止將明文密碼或 API key 留在版本控制

## Migration 注意事項

- 必須先解決舊 DB `user` / `users` 雙表問題
- 必須檢查現有帳號資料是否落在正式角色集合內
