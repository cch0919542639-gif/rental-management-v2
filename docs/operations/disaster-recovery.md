# Disaster Recovery

Last Updated: 2026-07-01

## Scope

這份文件只定義目前主幹可執行的最小災難復原流程：

- SQLite 本地驗收環境
- PostgreSQL Phase 5 bridge 環境

不涵蓋：

- 多節點 HA
- point-in-time recovery
- 雲端 managed backup policy

## Backup Baseline

SQLite:

```powershell
py -3 .\scripts\backup_runtime_db.py --dry-run
py -3 .\scripts\backup_runtime_db.py
```

PostgreSQL:

```powershell
$env:DATABASE_URL = "postgresql://postgres:replace-password@127.0.0.1:5432/rental_rebuild"
py -3 .\scripts\check_postgres_tooling.py --skip-binaries
py -3 .\scripts\backup_runtime_db.py --dry-run
py -3 .\scripts\backup_runtime_db.py
```

## Restore Baseline

先停用應用程式，再執行 restore。

SQLite:

```powershell
py -3 .\scripts\restore_runtime_db.py --source .\backups\runtime_YYYYMMDD_HHMMSS.db
py -3 .\scripts\restore_runtime_db.py --source .\backups\runtime_YYYYMMDD_HHMMSS.db --execute
```

PostgreSQL:

```powershell
py -3 .\scripts\restore_runtime_db.py --source .\backups\runtime_YYYYMMDD_HHMMSS.sql
py -3 .\scripts\restore_runtime_db.py --source .\backups\runtime_YYYYMMDD_HHMMSS.sql --execute
```

## Recovery Drill

1. 跑 `backup_runtime_db.py --dry-run`
2. 建立正式 backup
3. 在隔離環境做 restore dry-run
4. 若是 SQLite，可在測試路徑實際 restore 驗證
5. 跑 `py -3 .\scripts\health_check.py --config production`
6. 跑 `pytest tests\integration -q`
7. 確認 `/readyz` 正常

## Bridge Guard

若這次復原涉及 Alembic bridge：

- 先跑 `py -3 .\scripts\migration\run_migrations.py --list`
- 確認前序 migration 均已套用
- 僅在審查完成後執行：

```powershell
py -3 .\scripts\migration\run_migrations.py --execute --id 20260701_000002_alembic_bridge --allow-bridge
```

## Known Limits

- PostgreSQL 目前只完成最小 command wrapper，尚未完成正式 PITR / archive policy
- SQLite 不再視為 Phase 5 production 合格環境
