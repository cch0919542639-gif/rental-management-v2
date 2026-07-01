# Phase 5 Cutover Checklist

Last Updated: 2026-07-02

## Scope

這份文件只列正式 cutover 前必須逐項確認的最小清單。

## Pre-Cutover

- `pytest tests\integration --disable-warnings` 通過
- `check_postgres_tooling.py` 通過
- `bridge_drill_checklist.py` 通過
- `export_sqlite_to_pg.py --execute` 已產出最新 manifest / CSV
- `import_csv_to_target.py --execute` 已在 rehearsal target 成功
- `verify_row_parity.py` 對 rehearsal target 回傳 PASS
- `run_migrations.py --list` 顯示 baseline marker 已套用、bridge 仍 pending
- 已建立 source 與 target 的 backup

## Cutover Gate

只有在以下條件同時成立時，才允許考慮 bridge：

- Phase 5 gate 已明確批准
- 本次不是 rehearsal
- operator 已確認 rollback 路徑
- `run_migrations.py --execute --id 20260701_000002_alembic_bridge --allow-bridge` 的執行人、時間、目標環境已記錄

## Post-Cutover Minimum Check

- `run_migrations.py --list` 或等效紀錄可證明 bridge 已執行
- `alembic_version` 存在且 revision 正確
- `/readyz` 正常
- `health_check.py --config production` 正常
- 關鍵頁面 smoke test 正常
