# Real Data Import Gate Checklist

Date: 2026-07-02
Owner: Codex
Status: Active control document

## Purpose

這份文件定義正式資料導入前、中、後的 gate。  
任何一次正式 `--execute` 匯入，都必須照這份順序跑。

## Gate A — Read-Only Audit

目標：先證明資料庫狀態與污染風險。

**Dependency**: 無（第一關，可直接執行）

- [ ] `py -3 .\scripts\health_check.py --config default`
- [ ] `py -3 .\scripts\repair\year_month_audit.py`
- [ ] `py -3 .\scripts\repair\room_status_audit.py`
- [ ] `py -3 .\scripts\repair\user_table_audit.py`
- [ ] `py -3 .\scripts\migration\maintenance_legacy_scan.py`
- [ ] `py -3 .\scripts\migration\migration_index.py`

Gate A must pass:

- `year_month` 無非 6 碼值，或異常已逐筆列管
- `Room.status` 只有 `vacant` / `occupied`，或異常已列管
- `user/users` 雙表現況已查明
- 虛擬 tenant / 待修語義候選已被掃出

**A stop conditions** (任一發生則中止，不可進入 Gate B):

- `year_month_audit.py` 發現非 `YYYYMM` 格式且未列管
- `room_status_audit.py` 發現非 `vacant`/`occupied` 且未列管
- `user_table_audit.py` 無法判定 `user`/`users` 實際來源
- `maintenance_legacy_scan.py` 掃出超過 10 筆未確認虛擬 tenant
- `health_check.py` exit 非 0

### Gate A Waiver Rule — `SECRET_KEY` for Dry-Run Only

若 `health_check.py` 唯一失敗原因是 `SECRET_KEY` 仍為預設值，且本次任務僅為本機 `dry-run import / rehearsal`，可由專案 Owner 明確豁免後，視為 **條件式通過 Gate A**。

此豁免只適用於：

- 本機資料演練
- Gate C / Gate D 的備份、匯出、目標庫建立、dry-run 匯入
- 不對外開放的測試環境

此豁免不適用於：

- 正式環境
- 對外可登入或可連線環境
- Gate E 正式營運資料寫入
- 任何可視為上線的場景

豁免成立條件：

1. `health_check.py` 之外的 5 支 Gate A read-only 指令全部通過
2. `year_month`、`room.status`、`user/users`、`virtual tenant` 四類資料稽核均無 blocker
3. 本次回報明確記錄為 `SECRET_KEY dry-run waiver`

## Gate B — Manual Decision Freeze

目標：把人工決策定稿，避免匯入時邊跑邊猜。

**Dependency**:
- [ ] Gate A passed
- [ ] `docs/operations/real-data-manual-fields-checklist.md` 的 M1-M16 全部有明確決議

允許例外：

- 若 Gate A 僅因 `SECRET_KEY` 預設值失敗，且已符合上方 `Gate A Waiver Rule`，可視為 `Gate A (waived)` 進入 Gate B。

- [ ] [real-data-manual-fields-checklist.md](D:/CodexRuntime/rental/rebuild/docs/operations/real-data-manual-fields-checklist.md) 的 M1-M16 已補完
- [ ] `R06 (-33646)` 極端值已確認處理方式
- [ ] `user/users` 正式來源已決定
- [ ] `Room.status` 清洗規則已凍結
- [ ] 虛擬 tenant 清洗規則已凍結
- [ ] 首批匯入範圍已定義：核心資料 only / 含水電 / 含 payments

**B stop conditions** (任一發生則中止，不可進入 Gate C):

- M1-M16 仍有 `REQUIRED` 項目為空白或 `待補明細`
- `R06` 極端值來源不明
- `user/users` 出現雙方都有正式帳號但無合併決議
- `Room.status` 出現非 `vacant` / `occupied` 且無清洗決議
- 虛擬 tenant 與 active contract 交錯，無清洗決議

## Gate C — Safe Backup & Export

目標：在不動正式匯入目標庫前，先完整備份與抽出。

**Dependency**:
- [ ] Gate A passed
- [ ] Gate B passed (all manual decisions frozen)

允許例外：

- 若本次為 `dry-run import`，且 Gate A 的唯一未通過項是 `SECRET_KEY` 預設值，則在 Owner 豁免下可進入 Gate C。

- [ ] `py -3 .\scripts\backup_runtime_db.py`
- [ ] `py -3 .\scripts\export_source_db.py`
- [ ] `py -3 .\scripts\prepare_target_db.py`

Expected outputs:

- `backups/runtime_*.db`
- `real_import/*.csv`
- `runtime-real.db`

Rollback point:

- 只刪 `runtime-real.db`
- 不刪 `runtime.db`

**C stop conditions** (任一發生則中止，不可進入 Gate D):

- `backup_runtime_db.py` 執行失敗或輸出的 backup 檔大小為 0
- `export_source_db.py` 產出的 CSV 為空白或 header-only
- `prepare_target_db.py` 無法建立 `runtime-real.db`
- 任何腳本 exit 非 0

## Gate D — Dry-Run Import

目標：先證明順序、筆數、manifest 都正確。

**Dependency**:
- [ ] Gate C passed (CSV + target DB ready)
- [ ] `real_import/*.csv` 全部存在且非空

- [ ] `py -3 .\scripts\import_csv_to_target.py`
- [ ] 如需逐表檢查：`py -3 .\scripts\import_csv_to_target.py --table monthly_bills`
- [ ] 人工核對 dry-run 列出的 row counts 是否合理

Gate D must pass:

- 所有首批匯入表都有正確 CSV
- row count 與預期一致
- 沒有因 FK 順序錯誤而中止

**D stop conditions** (任一發生則中止，不可進入 Gate E):

- dry-run 報告 row count 為 0（資料未載入）
- 預期 row count 與實際差異 > 5%（需檢查 CSV 品質）
- dry-run 因 FK 約束錯誤而中止
- 某個首批表完全無對應 CSV

## Gate E — Execute Import

目標：只在 Gate A-D 全通過後執行正式寫入。

**Dependency**:
- [ ] Gate A passed
- [ ] Gate B passed
- [ ] Gate C passed
- [ ] Gate D passed (dry-run row counts verified)

限制：

- 若存在 `SECRET_KEY dry-run waiver`，則 Gate E 只允許在非正式營運資料、非對外環境、且 Owner 再次明確批准的情況下執行。
- 若本次目標是正式上線或正式營運資料切換，必須先移除豁免並設定非預設 `SECRET_KEY`。

- [ ] `py -3 .\scripts\import_csv_to_target.py --execute`

Scope recommendation:

1. 第一批：`landlords` / `tenants` / `properties` / `rooms` / `contracts` / `monthly_bills`
2. 第二批：`electricity_*` / `water_bills`
3. 第三批：`payment_records` / `maintenance_requests` / `user`

Hard rule:

- 第一批核心資料未核對前，不進第二批
- 第二批水電資料未核對前，不進第三批

**E stop conditions** (任一發生則中止，立即回滾 Batch):

- `--execute` 中途 exit 非 0
- 部分 table 寫入成功、部分失敗（需手動 reconciliation）
- 匯入後 row count 與 dry-run 預期不一致
- 發現 FK constraint violation（表示順序錯誤或 CSV 有髒資料）

## Gate F — Structural Verification

目標：確認匯入後結構與筆數一致。

**Dependency**:
- [ ] Gate E completed (all batches written)
- [ ] App stopped or in read-only mode during verification

- [ ] `py -3 .\scripts\verify_import.py`
- [ ] `py -3 .\scripts\migration\verify_row_parity.py`
- [ ] `py -3 .\scripts\health_check.py --config default`

Gate F must pass:

- `15/15 tables match`
- `schema_migration_log` 狀態一致
- health check exit 0

**F stop conditions** (任一發生則中止，不可進入 Gate G):

- `verify_import.py` 非 0 exit
- `verify_row_parity.py` 報告任一 table row count 不一致
- `health_check.py` exit 非 0
- 任一 table 筆數為 0（不應為空的表）

## Gate G — UI / Report Reconciliation

目標：從使用者畫面驗證資料是否真的可用。

**Dependency**:
- [ ] Gate F passed (structural verification complete)
- [ ] `mimo-real-data-regression-checklist-01.md` 可用
- [ ] App 已啟動，可透過瀏覽器訪問

優先順序：

1. Billing — List
2. Reports — Monthly Report
3. Reports — Yearly Overview
4. Dashboard
5. Payments
6. Electricity
7. Water
8. Maintenance

必做核對：

- [ ] `Billing / List` 總額公式：`rent + electricity_amount + public_electricity + water_amount + other_charges = total`
- [ ] `Reports / Monthly Report` 15 欄交叉比對
- [ ] `Reports / Yearly Overview` 12 月加總與月報一致
- [ ] 容許差異只允許 `±0.01`

Reference:

- [mimo-real-data-regression-checklist-01.md](D:/CodexRuntime/rental/rebuild/docs/reports/mimo-real-data-regression-checklist-01.md)

### Gate G — 6 Go / No-Go Conditions

下列 6 項必須 **全部通過** 才能宣告 Gate G passed：

| # | Condition | Pass Criteria | Verification Method |
|:-:|-----------|--------------|-------------------|
| GG-1 | **Billing List 總額 integrity** | 隨機抽查 5 筆帳單，手動驗證 `rent + electricity_amount + public_electricity + water_amount + other_charges = total`，100% 吻合 | 瀏覽器開啟 Billing/List，對照 DB query |
| GG-2 | **Monthly Report 15 欄交叉比對** | 所有 15 欄位值與 DB 逐欄一致，無欄位移位或缺失 | 對照 mimo checklist §9 |
| GG-3 | **Yearly Overview 年度加總** | 12 月 total_amount 加總 = MonthlyBill 表該年 SELECT SUM(total) VALUES，容許 ±0.01 | DB query vs 頁面顯示 |
| GG-4 | **Dashboard KPI parity** | `month_collected` + `month_unpaid` = `active_contracts` 對應月份的 billing 合計 | Dashboard 數字 vs billing 表 paid/unpaid 合計 |
| GG-5 | **Old system reconciliation** | 月報 A1-A14 對帳項目全部通過，無超標差異 | 依 mimo checklist 附錄對帳表逐項核對 |
| GG-6 | **Electricity / Water page reachable** | Electricity 與 Water 頁面可正確渲染，無 500 error，property 名稱正確顯示 | 瀏覽器實際訪問 |

### G8 — Maintenance 驗證標準

對應 Gate G 優先順序第 8 項 (Maintenance)：

| # | Check | Expected | Method |
|:-:|-------|----------|--------|
| M1 | 請求總數 (`request_count`) | = `maintenance_requests` 表筆數 | DB count vs 頁面顯示 |
| M2 | 未結案數 (`open_count`) | = status≠已解決/已結案 的筆數 | 狀態篩選核對 |
| M3 | 預估總額 (`estimated_total`) | = DB SUM(estimated_cost) WHERE NOT NULL | 頁面數字 vs DB query |
| M4 | 實際總額 (`actual_total`) | = DB SUM(actual_cost) WHERE NOT NULL | 同上 |
| M5 | 無虛擬 tenant 資料外洩 | Tenant.name 不存在 `空房`/`待修`/`待補` 等虛擬值 | maintenance 頁面 tenant_name 欄位抽查 |
| M6 | 狀態中文標籤 | `已通報`/`已指派`/`進行中`/`已解決`/`已結案` 正確顯示 | 瀏覽器檢查 |

### G10 — Reports Landlord Summary 驗證標準

對應 mimo-regression-checklist §10 (Landlord Summary)：

| # | Check | Expected | Method |
|:-:|-------|----------|--------|
| L1 | 房東名稱 (`landlord_name`) | 與 landlords 表一致 | 頁面 vs DB |
| L2 | 屬性名稱 (`property_name`) | 與 properties 表一致 | 同上 |
| L3 | 帳單數 (`bill_count`) | = 該 landlord 對應的 monthly_bills 筆數 | DB count |
| L4 | 總金額 (`total_amount`) | = `paid_amount` + `unpaid_amount` | 頁面加總校驗 |
| L5 | 加總公式校驗 | `paid_amount + unpaid_amount = total_amount` for each row | 逐列驗證 |
| L6 | 月份篩選 | 切換月份後 landlord summary 數字隨之更新 | 瀏覽器操作 |

## Stop Conditions

發生下列任一情況必須停止，不可繼續下一 gate：

- `R06` 極端值來源不明
- `user/users` 出現雙方都有正式帳號但無合併決議
- `Room.status` 出現非 `vacant` / `occupied`
- 虛擬 tenant 與 active contract 交錯，無清洗決議
- `verify_import.py` 非 0 exit
- 月報 / 年報 / 帳單總額出現超過 `±0.01` 差異
- 存在 `SECRET_KEY dry-run waiver` 卻嘗試宣告正式上線或正式營運切換

## Recommended Execution Order

1. 先完成 Gate A-B
2. 再執行 Gate C-D
3. Gate D 通過才執行 Gate E
4. Gate E 完成後立刻做 Gate F
5. Gate F 通過後立刻做 Gate G
6. 全部完成後，才可宣告正式資料可用
