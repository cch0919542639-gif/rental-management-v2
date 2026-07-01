# Phase 4 Launch Baseline

Last Updated: 2026-07-01

## Goal

這份文件定義新版系統在「本地可上線驗收」前的最低基線。

## Current Baseline

- 主要寫入 routes 已補上 `@admin_required`
- 已有 `/healthz` 與 `/readyz`
- 已有 production-like 啟動面：`requirements.txt`、`app/wsgi.py`、`scripts/run_production.py`、`scripts/run_prod.ps1`
- 已有 migration runner：`scripts/migration/run_migrations.py`
- 已有 production preflight：`scripts/health_check.py`
- 已有 SQLite backup / restore baseline

## Required Environment Variables

- `SECRET_KEY`
- `DATABASE_URL`

可選：

- `APP_ENV=production`
- `APP_HOST`
- `APP_PORT`
- `LINE_CHANNEL_SECRET`
- `LINE_CHANNEL_ACCESS_TOKEN`
- `OCR_PROVIDER`
- `OCR_API_KEY`

## Pre-Launch Sequence

1. 安裝 runtime 依賴

```powershell
py -3 -m pip install -r .\requirements.txt
```

2. 先列出 migration 狀態

```powershell
py -3 .\scripts\migration\run_migrations.py --list
```

3. 若有經核准的 pending `apply_*` migration，再執行

```powershell
py -3 .\scripts\migration\run_migrations.py --execute
```

4. 跑 preflight health check

```powershell
$env:SECRET_KEY = "replace-with-real-secret"
$env:DATABASE_URL = "sqlite:///D:/CodexRuntime/rental/rebuild/runtime.db"
py -3 .\scripts\health_check.py --config production
```

5. 啟動 production-like server

```powershell
$env:SECRET_KEY = "replace-with-real-secret"
powershell -ExecutionPolicy Bypass -File .\scripts\run_prod.ps1
```

## Backup / Restore Baseline

先建立備份：

```powershell
py -3 .\scripts\backup_runtime_db.py
```

若要還原，必須先停服務，再執行：

```powershell
py -3 .\scripts\restore_runtime_db.py --source .\backups\runtime_YYYYMMDD_HHMMSS.db --execute
```

## Known Remaining Risks

- 目前仍未導入正式外部 RDBMS；SQLite 僅適合低併發或單機驗收
- 尚未建立自動化備份 / restore drill
- 尚未導入 Alembic 類型的 ORM schema diff 工具
- LINE / OCR / Sheets 仍是邊界實作，非正式商用串接

## Phase 4 Exit Criteria

- `/readyz` 在 production config 下回 `200`
- `scripts/health_check.py --config production` 通過
- 所有 integration tests 通過
- migration list / execute / log 可正常工作
- 管理員寫入路由均受保護
