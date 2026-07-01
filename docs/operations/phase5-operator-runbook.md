# Phase 5 Operator Runbook

Last Updated: 2026-07-02

## Purpose

這份文件是給實際執行 Phase 5 rehearsal / cutover 的操作人員使用。

它只回答三件事：

1. 先準備什麼環境
2. 指令用什麼順序跑
3. 哪些輸出一定要留證

## Environment Baseline

請先複製以下模板作為本次操作的環境基線：

- `docs/operations/phase5.env.example`

最少要確認：

- `APP_ENV=production`
- `SECRET_KEY` 已替換
- `DATABASE_URL` 指向 PostgreSQL target
- `PG_DUMP_BIN` / `PSQL_BIN` 若 PATH 不標準，需明確覆寫

## Rehearsal Command Order

1. 工具與環境前置

```powershell
py -3 .\scripts\check_postgres_tooling.py
py -3 .\scripts\health_check.py --config production
py -3 .\scripts\migration\run_migrations.py --list
```

2. source 匯出

```powershell
py -3 .\scripts\migration\export_sqlite_to_pg.py
py -3 .\scripts\migration\export_sqlite_to_pg.py --execute
```

3. target 準備

```powershell
py -3 .\scripts\migration\prepare_target_db.py --target-url postgresql://...
py -3 .\scripts\migration\prepare_target_db.py --target-url postgresql://... --execute
```

4. import + parity

```powershell
py -3 .\scripts\migration\import_csv_to_target.py --manifest .\migration_exports\manifest.json --target-url postgresql://...
py -3 .\scripts\migration\import_csv_to_target.py --manifest .\migration_exports\manifest.json --target-url postgresql://... --execute
py -3 .\scripts\migration\verify_row_parity.py --source-url sqlite:///source.db --target-url postgresql://...
```

5. checklist + evidence

```powershell
py -3 .\scripts\migration\bridge_drill_checklist.py
py -3 .\scripts\migration\write_rehearsal_evidence.py --label rehearsal-01 --manifest .\migration_exports\manifest.json --parity-log .\parity.log --checklist-log .\checklist.log --execute
```

## Cutover Gate

正式 bridge 前，必須再確認：

- `phase5-cutover-checklist.md` 全部成立
- `phase5-rollback-checklist.md` 已備好
- `run_migrations.py --list` 仍顯示 bridge pending
- 本次不是 rehearsal，而是明確批准的 cutover 視窗

## Required Evidence Bundle

至少保留以下檔案或輸出：

- `migration_exports\manifest.json`
- `verify_row_parity.py` 輸出
- `bridge_drill_checklist.py` 輸出
- `write_rehearsal_evidence.py` 產生的 JSON
- `run_migrations.py --list` 輸出
- `health_check.py --config production` 輸出

## Stop Rules

出現以下任一情況，立刻停：

- `check_postgres_tooling.py` FAIL
- `prepare_target_db.py` 指出 target 非空且無法解釋
- `verify_row_parity.py` FAIL
- `bridge_drill_checklist.py` FAIL
- `run_migrations.py --list` 顯示 bridge 已套用，但本次明明只是 rehearsal

## Non-Goals

- 這份文件不授權直接跳過 rehearsal
- 這份文件不授權在未備份情況下執行 bridge
- 這份文件不授權手動修 PostgreSQL production 資料
