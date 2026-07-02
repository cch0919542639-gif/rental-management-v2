# Deployment Guide

Last Updated: 2026-07-01

## Scope

目前這份指南覆蓋：

- 本地或單機驗收環境
- Phase 5 PostgreSQL bridge 前後的 production-like 啟動
- backup / restore baseline

不涵蓋：

- Docker / container orchestration
- 雲端 secret manager
- PostgreSQL HA / PITR / managed service ADR

## Required Files

- `.env.example`
- `docs/operations/phase5.env.example`
- `requirements.txt`
- `scripts/run_prod.ps1`
- `scripts/health_check.py`
- `scripts/backup_runtime_db.py`
- `scripts/restore_runtime_db.py`

## Minimum Environment

Phase 5 production 目標環境：

```powershell
$env:APP_ENV = "production"
$env:SECRET_KEY = "replace-with-a-long-random-secret"
$env:DATABASE_URL = "postgresql://postgres:replace-password@127.0.0.1:5432/rental_rebuild"
```

若只是本地橋接或回歸驗收，仍可暫用 SQLite，但不得視為 production-ready。

建議操作人直接從 `docs/operations/phase5.env.example` 複製一份本地環境設定，不要手動拼湊 production 參數。

## Install

```powershell
py -3 -m pip install -r .\requirements.txt
```

## Migration Check

```powershell
py -3 .\scripts\migration\run_migrations.py --list
```

若有經核准的 pending migration：

```powershell
py -3 .\scripts\migration\run_migrations.py --execute
```

若要執行 Alembic bridge：

```powershell
py -3 .\scripts\migration\run_migrations.py --execute --id 20260701_000002_alembic_bridge --allow-bridge
```

注意：

- 未帶 `--allow-bridge` 會被 runner 擋下
- 若前序 migration 尚未套用，bridge 也會被擋下

## Preflight

```powershell
py -3 .\scripts\check_postgres_tooling.py --skip-binaries
py -3 .\scripts\health_check.py --config production
```

這一步在 Phase 5 會拒絕 SQLite production URL，屬預期保護。

若機器已安裝 PostgreSQL client tools，可再跑：

```powershell
py -3 .\scripts\check_postgres_tooling.py
```

## Backup Before Start

```powershell
py -3 .\scripts\backup_runtime_db.py --dry-run
py -3 .\scripts\backup_runtime_db.py
```

SQLite 會複製 `.db` 檔；PostgreSQL 會改成 `pg_dump` 路徑。

## Start Server

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_prod.ps1
```

## Restore Procedure

先確認服務已停掉，再執行：

SQLite:

```powershell
py -3 .\scripts\restore_runtime_db.py --source .\backups\runtime_YYYYMMDD_HHMMSS.db --execute
```

PostgreSQL:

```powershell
py -3 .\scripts\restore_runtime_db.py --source .\backups\runtime_YYYYMMDD_HHMMSS.sql
py -3 .\scripts\restore_runtime_db.py --source .\backups\runtime_YYYYMMDD_HHMMSS.sql --execute
```

## Launch Gate

啟動前至少確認：

- `pytest tests\integration -q` 通過
- `scripts/health_check.py --config production` 通過
- `run_migrations.py --list` 可列出 migration 狀態
- 若要切換到 Alembic，bridge 已經過審查並明確用 `--allow-bridge`
- backup 已成功建立
- `/readyz` 回傳 `200`

## Operator Docs

Phase 5 正式操作時，請一併閱讀：

- `docs/operations/phase5-closeout-summary.md`
- `docs/operations/phase5-operator-runbook.md`
- `docs/operations/phase5-cutover-checklist.md`
- `docs/operations/phase5-rollback-checklist.md`
