# Title

R3 Property Expense Real-Data Acceptance

## Owner

box

## Phase

R3 Reporting Acceptance

## Goal

在已完成 R3 遷移的指定環境，以真實或已核准的去識別資料，驗證物件支出明細與房東結算的金額口徑。

## Allowed Files

- `tests/integration/*`
- `docs/reports/*`
- `evidence/*`
- `coordination/progress/box.md`
- `coordination/completed/box.md`

## Do Not Touch

- `app/models/*`
- `app/services/*`
- `scripts/migration/*`
- 實際資料庫的既有帳單、付款與支出資料

## Acceptance

- 至少涵蓋一筆 posted、一筆 draft 或 voided 支出，以及一個當月無帳單但有 posted 支出的物件。
- 支出明細、CSV、XLSX 僅出現 posted 支出。
- 結算支出合計等於已過帳支出總和；淨額等於已連結付款扣除該支出。
- 產出可追溯的驗收紀錄；任何差異以 incident 記錄，不直接改寫資料。

## Dependencies

- `bf8efcd feat: add property expense reporting`
- R3 migration 已在指定的驗收環境成功執行。

## Status

READY
