# Dependency Map

Date: 2026-06-27
Author: reasonix

## Module Graph (New Target)

```text
core/config
core/db
core/errors
core/logging
core/security
  ↓
models/ (all ORM)
  ↓
repositories/ (centralized queries)
  ↓
services/ (billing, electricity, water, payment reconciliation, reports)
  ↓
modules/auth
modules/landlords
modules/properties
modules/rooms
modules/tenants
modules/contracts
modules/billing
modules/electricity
modules/water
modules/payments
modules/reports
  ↓
integrations/ (line, ocr, sheets)
```

Dependency Rules:
- module → repository → model (allowed)
- module → service → repository → model (allowed)
- module_a → module_b (forbidden unless through service/repository)
- integrations → module (forbidden; integrations call services, never modules directly)

## Entity Graph

```text
User ──→ Landlord (1:1 when role=landlord)
Landlord ──→ Property (1:N)
Property ──→ Room (1:N)
Property ──→ WaterBill (1:N)
Property ──→ ElectricityBill (1:N)
ElectricityBill ──→ ElectricityReading (1:N)
ElectricityBill ──→ CalcMethod (N:1)
Room ──→ Contract (1:N)
Tenant ──→ Contract (1:N)
Contract ──→ MonthlyBill (1:N)
Contract ──→ PaymentRecord (1:N)
MonthlyBill ──→ PaymentRecord (1:N)
```

## Circular Dependency Risks

1. **舊系統 `from app import ...` 反向耦合**：`landlord_report.py`、`water_bill.py`、`check_property_page.py`、`test_report.py`、`test_property_page.py`、`render_test.py`、`final_verify.py` 等 10+ 個腳本以 `from app import db, Model1, Model2` 反向引用 `app.py`。任何對 `app.py` 的重構都會破壞這些腳本，而這些腳本反過來又限制了重構的可能。**解決**：新版 reports/service 取代這些外部腳本，舊腳本保留指向舊 `app.py` 直到切換。

2. **`water_bill.py` ↔ `app.py` 雙向耦合**：`app.py` 呼叫 `register_water_routes(app, db, models={Property, Contract, MonthlyBill, Room, WaterBill})`，而 `water_bill.py` 內部又 `from app import Property, Contract, MonthlyBill, Room, WaterBill`。**解決**：新版 water module 只依賴 service + repository，不反向 import。

3. **`electricity_bp.py` ↔ `app.py` 雙向耦合**：同上模式，`app.py` 傳入 model class，blueprint 內部又直接操作 ORM。**解決**：新版 electricity module 走 service 層。

4. **`MonthlyBill` ↔ `PaymentRecord` backref 命名衝突**：`PaymentRecord.contract` 的 backref 名為 `payments`，與不存在的 `Payment` class 同名，未來若有人嘗試建立 `Payment` model 會立即衝突。**解決**：新版統一只用 `PaymentRecord`，backref 改名為 `payment_records`。

## Current Boundary Violations

| Area | Current Violation | Why It Is Risky | Proposed Fix |
| --- | --- | --- | --- |
| 計費公式 | `UtilityCalculator.calc_electricity()` 在 `app.py` 內與 route/form 同檔 | 公式無法獨立測試，修改 route 時可能誤改公式 | 移至 `services/electricity_calculator.py` |
| 計費公式 | `MonthlyBill.calculate_total()` 混在 ORM model 內 | model 層不該有業務邏輯 | 移至 `services/billing_service.py` |
| year_month | 9 處以上各自做 `replace('-', '')` 或 `strftime('%Y%m')` | 任一處格式錯誤就會寫入不一致資料 | 集中到 `core/year_month.py` helper |
| 電費 route | `electricity_bp.py` 內硬編碼 `meter_id=1` | 多電表場域直接錯誤 | 由 repository 查詢正確 meter |
| 電費 route | `api_electricity_create` 直接在 route 內做資料轉換與 `db.session.add` | route 承載 service + repository 職責 | 分為 route (parse) → service (compute) → repository (persist) |
| 報表 | `report_monthly()` 以 `tenant.name` 關鍵字（`待補`、`待修`、`空房`、`倉庫`、`鐵皮`）判定空房 | Room.status 被無視，tenant 表被汙染 | 改用 `Room.status` + `Contract.status`，tenant name 只顯示 |
| 付款 | `/payment/new` 等 route 使用未定義的 `Payment` class | NameError 死碼，但存在於 route table 中造成混淆 | 刪除五個 route，新版只掛載 `PaymentRecord` route |
| 外部腳本 | `landlord_report.py` 等以 `from app import ...` 反向耦合 | 重構 app.py 會破壞所有外部腳本 | 新版由 `reports` 模組 + service 取代 |
| 設定 | `config.py` 有明文 API key | 安全性漏洞 | 移至環境變數或 secret store |
| OCR | `_process_image_with_ocr()` 在 `app.py` 內混合 LINE webhook 邏輯 | 整合層與業務層不分 | 分為 `integrations/line.py` (webhook) → `services/ocr_service.py` (辨識) → `modules/payments/` (寫入 PaymentRecord) |
| 水費 | `water_bill.py` 內同時有 route、計算、DB 寫入 | 無法獨立測試分攤邏輯 | 分為 route → service → repository |
| 使用者 | `user` / `users` 雙表，ORM 只操作其一 | 另一張表的資料可能被忽略或覆蓋 | Migration 合併後 drop 冗餘表 |
| 月帳單 | `bill_toggle_paid()` 直接 flip boolean，無對帳流程 | 付款狀態與 PaymentRecord 脫鉤 | `paid` 改由 payment reconciliation service 推導 |

## Recommended Cut Lines

1. **`core/` 邊界**：app factory、config、db session、security、logging、errors。這些模組之間可互相引用，但不可引用 `modules/`、`services/`、`repositories/`。

2. **`models/` 邊界**：純 ORM 定義，零業務邏輯。`models/` 只被 `repositories/` 與 migration scripts 引用，不被 `modules/` 直接引用。

3. **`repositories/` 邊界**：所有 SQLAlchemy query 集中在此。`modules/` 不直接 `Model.query.filter(...)`，只透過 repository interface。

4. **`services/` 邊界**：業務計算與流程编排。`services/` 可引用 `repositories/` 與 `models/`，不可引用 `modules/`。多個 service 可互相呼叫（如 billing_service → electricity_service）。

5. **`modules/` 邊界**：每個 module 為獨立 Blueprint，包含自己的 `routes.py`、`forms.py`。module 透過 service 取得資料，透過 repository 查詢（不直接操作 ORM）。module 之間不可互相 import，跨模組需求走 service 層。

6. **`integrations/` 邊界**：LINE webhook、OCR client、Sheets API。只被 `modules/` 或 `services/` 單向呼叫，integrations 不反向依賴業務模組。

7. **新舊隔離線**：`rebuild/app/` 與 `D:\rental/` 完全不互相 import。唯一共用的是同一份 SQLite DB 檔案。Migration scripts 在 `rebuild/scripts/migration/` 內，獨立於新舊系統執行。
