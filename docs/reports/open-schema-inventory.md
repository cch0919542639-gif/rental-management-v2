# Schema Inventory

Date: 2026-06-28
Author: open

## Tables

| Table | ORM Model | Exists In DB | Approx Count | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- |
| `user` | User | yes | > 0 | P1 | ORM 無 `__tablename__`，SQLAlchemy 預設為 `user` |
| `users` | (無) | yes | ? | P1 | 冗餘表，來源不明，可能歷史殘留 |
| `landlords` | Landlord | yes | > 0 | P2 | |
| `properties` | Property | yes | > 0 | P2 | |
| `rooms` | Room | yes | > 0 | P1 | status 含非標準值 |
| `tenants` | Tenant | yes | > 0 | P0 | 含虛擬 tenant（空房/待修/待補/倉庫/鐵皮） |
| `contracts` | Contract | yes | > 0 | P1 | status 可能含非標準值 |
| `monthly_bills` | MonthlyBill | yes | > 0 | P0 | year_month 格式不一致，ORM 宣告 String(7) 但實際 YYYYMM |
| `payment_records` | PaymentRecord | yes | 0 | P2 | 表為空，schema 完整但從未被 route 正式使用 |
| `water_bills` | WaterBill | yes | > 0 | P2 | |
| `electricity_bills` | ElectricityBill | yes | > 0 | P0 | year_month 格式不一致，ORM 宣告 String(7) |
| `electricity_meters` | ElectricityMeter | yes | > 0 | P1 | |
| `electricity_readings` | ElectricityReading | yes | > 0 | P1 | |
| `calc_methods` | CalcMethod | yes | > 0 | P2 | |
| `message_log` | MessageLog | yes | 0? | P2 | LINE 訊息記錄 |
| `sheets_import_logs` | SheetsImportLog | yes | > 0 | P2 | |

## Duplicate Or Conflicting Tables

| Conflict | Details | Risk | Action |
| --- | --- | --- | --- |
| `user` vs `users` | 兩張表並存，ORM 只操作 `user`。`users` 來源不明。 | P1 | 比對筆數與欄位後合併，drop `users` |

## Field Mismatches

| Entity | Field | ORM Definition | DB Reality | Risk | Notes |
| --- | --- | --- | --- | --- | --- |
| MonthlyBill | year_month | String(7) | YYYYMM (6 chars) | P0 | ORM 宣告與 DB 實際值不符 |
| ElectricityBill | year_month | String(7) | YYYYMM (6 chars) | P0 | 同上，兩表同問題 |
| Room | status | VARCHAR, 無 CHECK | 可能含 `待修` 等非標準值 | P1 | 新契約要求僅 `vacant`/`occupied` |
| Contract | status | VARCHAR, 無 CHECK | 可能含 `draft` 等非 {active,expired,terminated} 值 | P1 | 需 repair script mapping |
| User | role | VARCHAR, 無 CHECK | 可能含非 {admin,landlord,viewer} 值 | P1 | 需 migration mapping |
| User | landlord_id | INTEGER, nullable | role=landlord 時可能為 NULL | P1 | 違反「landlord 必關聯 landlord_id」規則 |

## Format Mismatches

| Entity | Field | Issue | Risk |
| --- | --- | --- | --- |
| MonthlyBill | year_month | app.py 存 `YYYYMM`，app.aliyun.py 存 `YYYY-MM`，兩變體行為不同 | P0 |
| ElectricityBill | year_month | 同上，app.py 的 api_electricity_create 轉換格式而 app.aliyun.py 不轉 | P0 |
| MonthlyBill | total 計算 | app.py 含 public_electricity，app.aliyun.py 不含 | P0 |
| UtilityCalculator | 四捨五入 | app.py 用 ROUND_UP，app.aliyun.py 用 ROUND_HALF_UP | P1 |

## Recommended Cleanup Priority

1. **P0**: `MonthlyBill.year_month` 與 `ElectricityBill.year_month` 正規化為 YYYYMM → repair script
2. **P0**: `Room.status` 盤點實際值並 mapping 到 vacant/occupied
3. **P0**: 虛擬 tenant 資料清理（name = 待補/待修/空房/倉庫/鐵皮）
4. **P1**: `user`/`users` 雙表合併
5. **P1**: `Contract.status` 依據 end_date 比對後修正過期合約
6. **P1**: `User.role` 和 `landlord_id` 合規性檢查
7. **P2**: 確認 `payment_records` 表是否保留（reasonix 決議保留 schema 但無需遷移）
