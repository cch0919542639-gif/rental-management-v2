# Title

R3 Property Expense Production Migration

## Owner

Database Operator / Owner

## Phase

R3 Production Readiness

## Goal

在指定的實際資料庫，安全套用 `20260717_000005_property_expenses` 遷移，並保留可復原證據。

## Allowed Files

- `backups/*`
- `evidence/*`
- `docs/reports/*`
- `coordination/*`

## Do Not Touch

- 任何既有 `MonthlyBill`、`PaymentRecord`、`Contract` 資料
- 非 R3 的 migration
- 未經核准的正式資料庫

## Acceptance

- 執行前完成可還原備份並記錄檔名、時間與資料庫目標。
- 使用唯讀 dry-run 確認前置表存在，且遷移狀態為 pending。
- 取得 Owner 對目標資料庫與寫入操作的明確核准後，才執行 `--execute --id 20260717_000005_property_expenses`。
- 確認 `property_expenses` 與必要索引存在，migration log 有對應 ID，且 rerun 顯示 already applied。
- 將命令、輸出摘要與驗證結果寫入 evidence；失敗時停止並回報，不自行修復資料。

## Dependencies

- `40c2090 feat: add property expense ledger`
- 唯讀 dry-run 修正已驗證。
- Owner 提供目標資料庫、維護時段與寫入核准。

## Status

BLOCKED — awaiting Owner database-write approval and target confirmation
