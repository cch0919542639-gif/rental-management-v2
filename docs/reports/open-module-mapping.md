# Module Mapping

Date: 2026-06-28
Author: open

| Current File / Route Group | Proposed New Module | Confidence | Dependencies | Notes |
| --- | --- | --- | --- | --- |
| app.py → login/logout | `app/modules/auth/` | High | User model | 搬家即可，無特殊邏輯 |
| app.py → User model + admin CRUD | `app/models/user.py` + `app/modules/auth/` | High | user 表 | 雙表合併後僅保留 User model |
| app.py → Landlord CRUD | `app/modules/landlords/` | High | Landlord model | 搬家即可 |
| app.py → Property CRUD | `app/modules/properties/` | High | Property model | 搬家即可 |
| app.py → Room CRUD | `app/modules/rooms/` | High | Room model | 注意 status 正規化 |
| app.py → Tenant CRUD | `app/modules/tenants/` | High | Tenant model | 注意虛擬 tenant 清理 |
| app.py → Contract CRUD | `app/modules/contracts/` | High | Contract model | 注意 status 正規化 |
| app.py → bill CRUD + batch_entry + generate | `app/modules/billing/` | High | MonthlyBill + Contract | 需抽離計算邏輯到 service |
| app.py → report_monthly, report_summary | `app/modules/reports/` | Medium | MonthlyBill + Contract + Room + Property + Landlord | app.py 與 app.aliyun.py 實作不同，需統一為 Room.status 判斷 |
| app.py → payment_list (PaymentRecord) | `app/modules/payments/` | High | PaymentRecord | 表為空，schema 完整 |
| app.py → PaymentRecord API routes | `app/modules/payments/` (api 子目錄) | High | PaymentRecord + receipt_ocr | OCR→審核→對帳流程 |
| app.py → bill_toggle_paid | `app/modules/payments/` (reconciliation service) | Medium | MonthlyBill + PaymentRecord | 需改由 reconciliation service 推導 paid |
| `electricity_bp.py` | `app/modules/electricity/` | High | ElectricityBill + ElectricityMeter + ElectricityReading | 拆為 route + service + repository，移除 meter_id=1 硬編碼 |
| `water_bill.py` | `app/modules/water/` | High | WaterBill + Contract | 拆為 route + service + repository |
| `landlord_report.py` | `app/modules/reports/` | Medium | Landlord + Property + Room + Contract + Tenant + MonthlyBill + PaymentRecord | 重新設計，不保留舊實作 |
| app.py → config, app factory, db, errors, logging | `app/core/` | High | — | 建立 app factory pattern |
| `config.py` | `app/core/config/` | High | 環境變數 | 移除明文金鑰 |
| app.py → ORM models (全部) | `app/models/` | High | SQLAlchemy | 純 ORM 定義，零業務邏輯 |
| app.py → UtilityCalculator | `app/services/billing_service.py` | High | MonthlyBill + Contract + ElectricityBill | 拆出獨立 service |
| `ct_meter_proportional.py` | `app/services/electricity_calculator.py` | High | ElectricityBill + ElectricityReading | 演算法模組 |
| `dual_meter_tou.py` | `app/services/electricity_calculator.py` | High | ElectricityBill + ElectricityReading | 演算法模組 |
| app.py → dashboard | `app/modules/dashboard/` 或合併入 core | Medium | Contract + MonthlyBill | year_month 格式先統一 |
| app.py → LINE callback | `app/integrations/line/` | High | PaymentRecord + MessageLog | webhook handler |
| app.py → OCR (receipt analysis) | `app/integrations/ocr/` | High | receipt_ocr | 保留演算法 |
| app.py → sheets/import | `app/integrations/sheets/` | High | SheetsImportLog | |
| app.py → DB queries (所有 query.filter 寫法) | `app/repositories/` | High | ORM models | 集中查詢層，禁止 route 直接操作 ORM |
| app.py → `init_db()`, CLI commands | `app/core/cli.py` 或 `scripts/` | High | db | |
| `check_*` 診斷腳本系列 (11 個) | `scripts/repair/` 或保留原位 | Medium | SQLite | 多為 property 13 臨時除錯，部分可歸檔 |
| `fix_*` 修復腳本系列 (6 個) | `scripts/repair/` | Medium | SQLite | 多為 property 13 臨時資料修正 |
| `create_*` 建立腳本系列 (4 個) | `scripts/migration/` | Medium | SQLite | 資料遷移腳本 |
| `update_*` 腳本系列 (2 個) | `scripts/repair/` | Medium | SQLite | 資料修正 |
| `verify_*` 腳本系列 (2 個) | `scripts/repair/` | Medium | SQLite | 驗證腳本 |
| `test_*` / `render_test` / `orm_check` 等測試腳本 (7 個) | `tests/` 或保留原位 | Low | Flask app context | 改為正式 pytest |
| `deploy.py` | `scripts/deployment/` | Low | paramiko | 改為新版 deploy script |
| `backup_rental.py` | `scripts/deployment/` | Low | cloudflared + scp | 保留 |

## Cross Module Tangles

| Tangle | Files Involved | Description |
| --- | --- | --- |
| app.py ↔ water_bill.py 雙向耦合 | app.py, water_bill.py | app.py → register_water_routes(app, db, models)；water_bill.py → from app import Property, Contract, MonthlyBill, Room, WaterBill |
| app.py ↔ electricity_bp.py 參數耦合 | app.py, electricity_bp.py | app.py 傳入 model class 給 create_electricity_bp()，非雙向 import 但 route 內仍直接操作 ORM |
| app.py ↔ 外部測試腳本 | app.py + 10 個腳本 (check_property_page.py, final_verify.py, orm_check.py, render_test.py, test_flask_report.py, test_import.py, test_property_page.py, test_report.py, test_import.py) | 全部 `from app import ...`，任何 app.py 重構都會破壞 |
| app.py ↔ receipt_ocr | app.py, receipt_ocr.py | api_analyze_receipt 內 late import，輕度耦合 |
| app.py ↔ sheets import | app.py, scripts/smart_import | sheets_import 內 late import |
| year_month 格式 | 9 處以上 | 無集中 helper，格式散落在 route/blueprint/外部腳本/template |
| 計費公式 | app.py (UtilityCalculator), electricity_bp.py, water_bill.py, ct_meter_proportional.py, dual_meter_tou.py | 公式散落在各處，無單一 service 層 |
| Room.status 與 tenant.name 脫鉤 | app.py (report_monthly), tenants 表, rooms 表 | occupancy 判定用 tenant.name 而非 Room.status |

## Suggested First Moves

1. **建立 `core/` 骨架**: app factory、config (環境變數)、db session、`core/year_month.py` helper。這是所有後續模組的基礎。
2. **建立 `models/`**: 從 app.py 抽出所有 ORM class 到獨立檔案，依 data_contracts 凍結欄位。不可加入任何業務邏輯。
3. **建立 `repositories/`**: 從 app.py 抽出所有 database query，集中管理。這個步驟會讓後續 route 移植變簡單。
4. **建立 `services/billing_service.py` + `services/electricity_calculator.py`**: 抽出 UtilityCalculator、電費/水費計算公式。這三組公式有測試驗證需求。
5. **移植 `modules/electricity/`** (高風險優先): electricity_bp.py 路由多、有硬編碼問題 (meter_id=1)、年月份格式不一致，最適合做第一個移植目標驗證拆層流程。
