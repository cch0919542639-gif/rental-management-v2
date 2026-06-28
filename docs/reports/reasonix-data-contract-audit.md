# Data Contract Audit

Date: 2026-06-27
Author: reasonix

---

## Entity 1: User

- Name: User
- Source Files: `D:\rental\app.py` (class User), `D:\rental\app.aliyun.py`
- Source Tables: `user`, `users`（雙表並存）

### Confirmed Schema

| Field | Type | Nullable | Default | Confirmed From |
| --- | --- | --- | --- | --- |
| id | INTEGER | NO | auto | core-entities.md, ORM |
| username | VARCHAR | NO | — | core-entities.md |
| password_hash | VARCHAR | NO | — | core-entities.md |
| name | VARCHAR | YES | — | ORM |
| role | VARCHAR | NO | — | auth-and-roles.md |
| landlord_id | INTEGER | YES | NULL | core-entities.md |
| created_at | DATETIME | YES | now | ORM |

### Actual Data Pattern

| Field | Observed Pattern | Example | Risk |
| --- | --- | --- | --- |
| role | 舊資料可能含未定義值（超出 {admin, landlord, viewer}） | — | HIGH: 需 mapping |
| username | 雙表可能不同步 | — | HIGH: 合併時可能 conflict |
| landlord_id | role=landlord 時可能為空 | — | MEDIUM: 違反契約規則 |

### Current Hidden Rules

- 舊系統 `create_admin()` 在啟動時自動建立預設 admin 帳號（被 auth-and-roles.md 禁止）。
- `User.is_admin()` 僅檢查 `role == 'admin'`，不檢查 `landlord_id`。

### Proposed Contract

| Field | Required Rule | Rationale |
| --- | --- | --- |
| username | UNIQUE NOT NULL | 登入唯一識別 |
| password_hash | NOT NULL, werkzeug generate_password_hash | 安全基準 |
| role | CHECK IN ('admin', 'landlord', 'viewer') | 角色封閉集合 |
| landlord_id | NOT NULL WHEN role='landlord' ELSE NULL | 資料關聯正確性 |

### Mismatches Between Code And Data

- DB 內同時存在 `user` 與 `users` 兩張表。ORM `User` class 無 `__tablename__`，SQLAlchemy 預設為 `user`。`users` 表來源不明，可能為歷史殘留或備份。
- 舊 ORM 的部分欄位（如 `landlord_id`）需確認實際存在於 `user` 表中。

### Migration Need

- **HIGH**: 必須解決雙表問題（比對、合併、刪除冗餘表）。

### Open Questions

- `users` 表的來源與用途為何？是備份、舊 schema 殘留、還是特定 migration 產物？

---

## Entity 2: MonthlyBill.year_month

- Name: MonthlyBill（focus: year_month 欄位）
- Source Files: `D:\rental\app.py` (class MonthlyBill)
- Source Tables: `monthly_bills`

### Confirmed Schema

| Field | Type | Nullable | Default | Confirmed From |
| --- | --- | --- | --- | --- |
| year_month (ORM) | String(7) | NO | — | ORM 宣告 |
| year_month (DB) | 實際 YYYYMM (6 chars) | NO | — | billing-contract.md |
| contract_id + year_month | UNIQUE | — | — | billing-contract.md |

### Actual Data Pattern

| Field | Observed Pattern | Example | Risk |
| --- | --- | --- | --- |
| year_month | DB 實際值為 `YYYYMM` (6 chars) | `202606` | HIGH: ORM 宣告 String(7) 與實際不符 |
| year_month | 舊程式在 9 處以上各自做 replace/strftime 轉換 | 見下列清單 | HIGH: 格式不一致 |

### Current Hidden Rules (year_month 轉換散落位置)

- `app.py:691`: `current_month_db = current_month.replace('-', '')`（dashboard）
- `app.py:982`: `db_year_month = bill.year_month.replace('-', '')`（bill edit 回寫）
- `app.py:1013`: `year_month=datetime.now().strftime('%Y%m')`（自動生成帳單）
- `app.py:1043`: `db_year_month = year_month.replace('-', '')`（batch_bill_entry）
- `app.py:1066`: `db_year_month = year_month.replace('-', '')`（report_monthly）
- `app.py:1684`: `ym = (data.get("year_month") or ps.strftime("%Y-%m")).replace('-', '')`（electricity OCR）
- `water_bill.py:105`: `year_month = billing_start.strftime('%Y%m')`（水費回寫）
- `electricity_bp.py:70`: `year_month=request.form['period_end'][:7].replace('-', '')`（電費建立）
- `electricity_bp.py:275`: `year_month=_d.today().strftime('%Y%m')`（快速抄表）

### Proposed Contract

| Field | Required Rule | Rationale |
| --- | --- | --- |
| year_month | DB 固定 `YYYYMM` (String(6)) | 與實際資料一致 |
| year_month | UI/API 接受 `YYYY-MM`，由單一 helper 轉換 | 禁止散落轉換 |
| contract_id + year_month | UNIQUE | 避免重複帳單 |

### Mismatches Between Code And Data

- ORM 宣告 `String(7)` 但實際儲存 `YYYYMM`（6 字元），可能是早期設計殘留。
- `electricity_bills.year_month` 同樣宣告 `String(7)`，也存在格式不一致風險。

### Migration Need

- **HIGH**: 需要 repair script 檢查並修正任何非 `YYYYMM` 格式的殘留值。需要 alter `monthly_bills.year_month` 與 `electricity_bills.year_month` 為 `String(6)` 或保留長度但 enforce 格式。

### Open Questions

- 是否有歷史資料以 `YYYY-MM` 格式寫入？需要 SQL 查驗 `SELECT DISTINCT length(year_month) FROM monthly_bills`。

---

## Entity 3: PaymentRecord

- Name: PaymentRecord
- Source Files: `D:\rental\app.py` (class PaymentRecord)
- Source Tables: `payment_records`

### Confirmed Schema

| Field | Type | Nullable | Default | Confirmed From |
| --- | --- | --- | --- | --- |
| id | INTEGER | NO | auto | ORM |
| contract_id | INTEGER | YES | NULL | ORM |
| monthly_bill_id | INTEGER | YES | NULL | ORM |
| amount | NUMERIC(10,2) | YES | NULL | ORM |
| bank_name | VARCHAR(50) | YES | NULL | ORM |
| account_number | VARCHAR(50) | YES | NULL | ORM |
| account_holder | VARCHAR(50) | YES | NULL | ORM |
| transaction_date | DATE | YES | NULL | ORM |
| payer_name | VARCHAR(50) | YES | NULL | ORM |
| transaction_id | VARCHAR(100) | YES | NULL | ORM |
| status_text | VARCHAR(20) | YES | NULL | ORM |
| raw_ocr_text | TEXT | YES | NULL | ORM |
| raw_llm_response | TEXT | YES | NULL | ORM |
| image_path | VARCHAR(500) | YES | NULL | ORM |
| ocr_engine | VARCHAR(20) | YES | NULL | ORM |
| record_status | VARCHAR(20) | YES | 'pending' | ORM, status-machines.md |
| verified_by_id | INTEGER | YES | NULL | ORM |
| verified_at | DATETIME | YES | NULL | ORM |
| notes | TEXT | YES | NULL | ORM |
| created_at | DATETIME | YES | now | ORM |

### Actual Data Pattern

| Field | Observed Pattern | Example | Risk |
| --- | --- | --- | --- |
| (all) | 表為空 (0 rows) | — | LOW: 無歷史資料需遷移 |
| record_status | 從未使用，僅有 default 值 | pending | LOW |

### Current Hidden Rules

- `PaymentRecord.contract` backref 名為 `payments`，與不存在的舊 `Payment` class 同名，可能造成混淆。
- `to_dict()` 方法存在，但無任何 route 使用它輸出（現有 route 使用不存在的 `Payment` class 而非 `PaymentRecord`）。

### Proposed Contract

| Field | Required Rule | Rationale |
| --- | --- | --- |
| amount | >= 0, NOT NULL when record_status != 'pending' | 付款金額不可為負 |
| transaction_id | UNIQUE if present | 避免重複對帳 |
| record_status | CHECK IN ('pending', 'verified', 'rejected', 'linked') | 狀態機封閉 |
| contract_id + monthly_bill_id | 可為空，支援先收件後對帳 | payments-contract.md |

### Mismatches Between Code And Data

- `PaymentRecord` 模型定義完整，但從未被 route 正式使用。OCR 流程（`api_analyze_receipt`、`_process_image_with_ocr`）寫入 `PaymentRecord`，但管理 UI（`payment_list`）使用的是不存在的 `Payment` class。
- `payment_records` 表空置，表示 OCR/LINE 流程從未成功寫入過資料，或寫入後被清空。

### Migration Need

- **None**（表為空，無資料需遷移；schema 已符合契約）。

### Open Questions

- OCR/LINE webhook 是否曾成功觸發並嘗試寫入 `PaymentRecord`？若曾寫入但後來被清空，需確認原因。

---

## Entity 4: Room.status

- Name: Room（focus: status 欄位）
- Source Files: `D:\rental\app.py` (class Room)
- Source Tables: `rooms`

### Confirmed Schema

| Field | Type | Nullable | Default | Confirmed From |
| --- | --- | --- | --- | --- |
| status | VARCHAR | YES | — | ORM, status-machines.md |

### Actual Data Pattern

| Field | Observed Pattern | Example | Risk |
| --- | --- | --- | --- |
| status | 舊資料可能含非正式值（超出 {vacant, occupied}） | 可能有 `待修` | HIGH: 與新契約衝突 |
| status | 舊系統 occupancy 實際由 tenant.name 關鍵字驅動，而非 room.status | tenant.name = '空房' | HIGH: status 與 display 脫鉤 |

### Current Hidden Rules

- `report_monthly()` 完全忽略 `Room.status`，改以 `tenant.name` 是否包含 `"待補"`、`"待修"`、`"空房"`、`"倉庫"`、`"鐵皮"` 判定空房顯示。
- `Room.status` 可能從未被可靠維護，實際 occupancy 資訊散落在 `tenant.name`、`contract.status` 與隱性慣例中。

### Proposed Contract

| Field | Required Rule | Rationale |
| --- | --- | --- |
| status | NOT NULL, CHECK IN ('vacant', 'occupied') | 明確的 occupancy 唯一來源 |
| (new) maintenance_flag | 獨立欄位或 maintenance 模組 | 待修不再汙染 tenant name |

### Mismatches Between Code And Data

- `Room.status` 存在但未被當作 occupancy 的 single source of truth。
- 虛擬 tenant 名稱（`空房`、`待修`、`待補`）使 `tenants` 表混入非真實房客資料。

### Migration Need

- **HIGH**: 需要盤點所有 `Room.status` 實際值，mapping 到 `vacant`/`occupied`。需要將虛擬 tenant 對應的 contract 重新歸檔，並清除虛擬 tenant row 或標記為 legacy。

### Open Questions

- 是否有 room 同時有 `status='occupied'` 但 tenant.name 為 `空房`？（資料矛盾）
- 「待修」與「待補」的業務語義差異為何？是否需要兩個獨立的 maintenance 子狀態？

---

## Entity 5: Contract.status

- Name: Contract（focus: status 欄位）
- Source Files: `D:\rental\app.py` (class Contract)
- Source Tables: `contracts`

### Confirmed Schema

| Field | Type | Nullable | Default | Confirmed From |
| --- | --- | --- | --- | --- |
| status | VARCHAR | YES | — | ORM, status-machines.md |

### Actual Data Pattern

| Field | Observed Pattern | Example | Risk |
| --- | --- | --- | --- |
| status | 舊資料可能含未定義值 | 可能含 `draft` 等 | MEDIUM: 需 mapping 到正式集合 |

### Current Hidden Rules

- `Contract.active_contract()` 方法存在但實作可能依賴 status 字串比對。
- 同一房間同時只允許一個 active 合約的規則在舊系統可能只靠 UI 約束，無 DB constraint。

### Proposed Contract

| Field | Required Rule | Rationale |
| --- | --- | --- |
| status | NOT NULL, CHECK IN ('active', 'expired', 'terminated') | 狀態機封閉 |
| room_id + status='active' | 全表最多一筆（應用層 unique） | 同一房間唯一 active 合約 |

### Mismatches Between Code And Data

- 若舊資料存在已過期但 status 仍為 `active` 的合約（`end_date < today` 但 status 未更新），需修復。
- 舊系統 `contract_terminate()` route 存在，但可能未廣為使用。

### Migration Need

- **MEDIUM**: 需要 repair script 依據 `end_date` 與 `today` 修正過期合約的 status。

### Open Questions

- 舊系統是否有 `draft`、`pending` 等非正式 status 值？需 SQL 查驗 `SELECT DISTINCT status FROM contracts`。

---

## Summary: Migration Priority

| Entity | Risk Level | Migration Need | Action |
| --- | --- | --- | --- |
| User（雙表） | HIGH: 帳號遺失風險 | HIGH | 比對筆數與欄位，合併後 drop `users` |
| MonthlyBill.year_month | HIGH: 格式不一致 bug | HIGH | 正規化為 YYYYMM + 建立統一 helper |
| PaymentRecord | LOW: 表為空 | None | 保留 schema，無需遷移 |
| Room.status | HIGH: 與 display 脫鉤 | HIGH | 盤點實際值，mapping 到 vacant/occupied |
| Contract.status | MEDIUM: 過期未更新 | MEDIUM | repair script 修正過期合約 status |
