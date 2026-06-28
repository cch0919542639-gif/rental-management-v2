# Core Entities Contract

本文件定義新版第一批核心主資料實體契約。內容基於 `D:\rental\app.py` 與現有 SQLite schema 的已確認事實整理。

## 關聯主線

```text
User -> Landlord
Landlord -> Property
Property -> Room
Tenant -> Contract
Room -> Contract
Contract -> MonthlyBill
Contract -> PaymentRecord
Property -> WaterBill
Property -> ElectricityBill
ElectricityBill -> ElectricityReading
```

## User

來源：

- 舊 ORM `User`
- DB 內同時存在 `user` 與 `users`，新版只保留單一正式表

正式欄位：

- `id`
- `username`
- `password_hash`
- `name`
- `role`
- `landlord_id`
- `created_at`

正式規則：

- `username` 必須唯一
- `password_hash` 不可為空
- `role` 只允許 `admin`、`landlord`、`viewer`
- `landlord_id` 僅在 `role=landlord` 時可為非空

待處理問題：

- 舊 DB 有 `user` / `users` 雙表，需要 migration 決議

## Landlord

正式欄位：

- `id`
- `name`
- `phone`
- `electricity_account`
- `water_account`
- `electricity_rate_type`
- `electricity_rate`
- `water_rate_type`
- `water_rate`
- `notes`
- `created_at`

正式規則：

- `name` 不可為空
- 電費與水費預設費率屬於房東層級預設值，可被合約覆蓋

## Property

正式欄位：

- `id`
- `landlord_id`
- `name`
- `address`
- `total_rooms`
- `electricity_meter_type`
- `water_meter_type`
- `billing_rule`
- `created_at`

正式規則：

- `landlord_id` 不可為空
- `electricity_meter_type` 建議只允許 `independent`、`shared`
- `water_meter_type` 建議只允許 `independent`、`shared`
- `billing_rule` 在新版要改成明確 enum，不接受隨意字串

## Room

正式欄位：

- `id`
- `property_id`
- `room_number`
- `rent`
- `deposit`
- `electricity_meter_id`
- `water_meter_id`
- `area_ping`
- `status`
- `notes`
- `created_at`

正式規則：

- `property_id` 不可為空
- `room_number` 在同一 `property_id` 下必須唯一
- `status` 第一版只允許 `vacant`、`occupied`

禁止規則：

- 不可再把 `待修` 視為 `status` 值；待修應改由獨立欄位或維修模組管理

## Tenant

正式欄位：

- `id`
- `name`
- `phone`
- `id_number`
- `emergency_contact`
- `emergency_phone`
- `notes`
- `created_at`

正式規則：

- `name` 不可為空

禁止規則：

- 新版不得再使用虛擬 tenant 名稱如 `空房`、`待修`、`待補` 承載房況

## Contract

正式欄位：

- 基本欄位：`id`、`tenant_id`、`room_id`、`start_date`、`end_date`、`rent`、`deposit`、`status`、`notes`、`created_at`
- 費率欄位：`electricity_rate`、`water_rate`
- 起始讀數：`start_electricity_reading`、`start_water_reading`
- 承租細節與附加資料：保留在 contract，但新版應評估拆到 profile/detail 結構

正式規則：

- 同一時間同一房間只允許一筆 `active` 合約
- `end_date` 必須晚於 `start_date`
- 合約租金為月帳單租金的預設來源
- 若合約費率為空，回退到房東預設值

第一版狀態：

- `active`
- `expired`
- `terminated`

## 設計決策

- 新版主資料要以「房間狀態」與「合約狀態」描述 occupancy，不再依賴 tenant 名稱判斷
- 合約上的大量租賃細節欄位先保留，但應由 `contracts` 模組明確分群管理
