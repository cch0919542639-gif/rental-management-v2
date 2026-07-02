# Real Data Import Gate Checklist

Date: 2026-07-02
Owner: Codex
Status: Active control document

## Purpose

這份文件定義正式資料導入前、中、後的 gate。  
任何一次正式 `--execute` 匯入，都必須照這份順序跑。

## Gate A — Read-Only Audit

目標：先證明資料庫狀態與污染風險。

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

## Gate B — Manual Decision Freeze

目標：把人工決策定稿，避免匯入時邊跑邊猜。

- [ ] [real-data-manual-fields-checklist.md](D:/CodexRuntime/rental/rebuild/docs/operations/real-data-manual-fields-checklist.md) 的 M1-M16 已補完
- [ ] `R06 (-33646)` 極端值已確認處理方式
- [ ] `user/users` 正式來源已決定
- [ ] `Room.status` 清洗規則已凍結
- [ ] 虛擬 tenant 清洗規則已凍結
- [ ] 首批匯入範圍已定義：核心資料 only / 含水電 / 含 payments

Gate B blocks:

- 不可讓 `Tenant.name` 保留虛擬值直接進正式資料
- 不可把 `Room.status` 非法值直接匯入
- 不可在 `user/users` 未決前匯正式 user
- 不可接受 `YYYY-MM` 或 NULL 的 `MonthlyBill.year_month`

## Gate C — Safe Backup & Export

目標：在不動正式匯入目標庫前，先完整備份與抽出。

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

## Gate D — Dry-Run Import

目標：先證明順序、筆數、manifest 都正確。

- [ ] `py -3 .\scripts\import_csv_to_target.py`
- [ ] 如需逐表檢查：`py -3 .\scripts\import_csv_to_target.py --table monthly_bills`
- [ ] 人工核對 dry-run 列出的 row counts 是否合理

Gate D must pass:

- 所有首批匯入表都有正確 CSV
- row count 與預期一致
- 沒有因 FK 順序錯誤而中止

## Gate E — Execute Import

目標：只在 Gate A-D 全通過後執行正式寫入。

- [ ] `py -3 .\scripts\import_csv_to_target.py --execute`

Scope recommendation:

1. 第一批：`landlords` / `tenants` / `properties` / `rooms` / `contracts` / `monthly_bills`
2. 第二批：`electricity_*` / `water_bills`
3. 第三批：`payment_records` / `maintenance_requests` / `user`

Hard rule:

- 第一批核心資料未核對前，不進第二批
- 第二批水電資料未核對前，不進第三批

## Gate F — Structural Verification

目標：確認匯入後結構與筆數一致。

- [ ] `py -3 .\scripts\verify_import.py`
- [ ] `py -3 .\scripts\migration\verify_row_parity.py`
- [ ] `py -3 .\scripts\health_check.py --config default`

Gate F must pass:

- `15/15 tables match`
- `schema_migration_log` 狀態一致
- health check exit 0

## Gate G — UI / Report Reconciliation

目標：從使用者畫面驗證資料是否真的可用。

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

## Stop Conditions

發生下列任一情況必須停止，不可繼續下一 gate：

- `R06` 極端值來源不明
- `user/users` 出現雙方都有正式帳號但無合併決議
- `Room.status` 出現非 `vacant` / `occupied`
- 虛擬 tenant 與 active contract 交錯，無清洗決議
- `verify_import.py` 非 0 exit
- 月報 / 年報 / 帳單總額出現超過 `±0.01` 差異

## Recommended Execution Order

1. 先完成 Gate A-B
2. 再執行 Gate C-D
3. Gate D 通過才執行 Gate E
4. Gate E 完成後立刻做 Gate F
5. Gate F 通過後立刻做 Gate G
6. 全部完成後，才可宣告正式資料可用
