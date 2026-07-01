# Phase 5 Bridge Drill

Last Updated: 2026-07-02

## Purpose

這份文件定義 PostgreSQL bridge rehearsal 的最小執行順序。

目標不是直接 cutover，而是先驗證：

- SQLite source 可被盤點 / 匯出
- row parity 驗證流程可跑
- Alembic bridge 仍保持 pending
- operator 有固定 preflight/checklist 入口

## Drill Sequence

1. 準備 source 環境

```powershell
py -3 .\scripts\check_postgres_tooling.py --skip-binaries
py -3 .\scripts\migration\run_migrations.py --list
```

2. 匯出 source SQLite

```powershell
py -3 .\scripts\migration\export_sqlite_to_pg.py
py -3 .\scripts\migration\export_sqlite_to_pg.py --execute
```

3. 檢查 bridge drill checklist

```powershell
py -3 .\scripts\migration\bridge_drill_checklist.py
```

4. 對 target copy 做 row parity 驗證

先準備乾淨 target schema：

```powershell
py -3 .\scripts\migration\prepare_target_db.py --target-url postgresql://...
py -3 .\scripts\migration\prepare_target_db.py --target-url postgresql://... --execute
```

先做 import dry-run，再對乾淨 target import：

```powershell
py -3 .\scripts\migration\import_csv_to_target.py --manifest .\migration_exports\manifest.json --target-url postgresql://...
py -3 .\scripts\migration\import_csv_to_target.py --manifest .\migration_exports\manifest.json --target-url postgresql://... --execute
```

```powershell
py -3 .\scripts\migration\verify_row_parity.py --source-url sqlite:///source.db --target-url postgresql://...
```

5. 產出 rehearsal evidence bundle

```powershell
py -3 .\scripts\migration\write_rehearsal_evidence.py --label rehearsal-01 --manifest .\migration_exports\manifest.json
py -3 .\scripts\migration\write_rehearsal_evidence.py --label rehearsal-01 --manifest .\migration_exports\manifest.json --parity-log .\parity.log --checklist-log .\checklist.log --execute
```

6. 確認 Alembic bridge 仍 pending

```powershell
py -3 .\scripts\migration\run_migrations.py --list
```

## Stop Conditions

出現以下任一狀況時，停止 drill，不得直接 bridge：

- `bridge_drill_checklist.py` 回傳 FAIL
- `prepare_target_db.py --execute` 遇到非空 target 且未明確允許
- `import_csv_to_target.py --execute` 遇到非空 target 或欄位轉換錯誤
- `verify_row_parity.py` 有任一 table mismatch
- `run_migrations.py --list` 看不到 baseline marker
- `run_migrations.py --list` 顯示 bridge 已套用，但本次不是正式 cutover

## Explicit Non-Goals

- 本文件不授權直接執行 `apply_20260701_000002_alembic_bridge.py`
- 本文件不處理 production cutover rollback
