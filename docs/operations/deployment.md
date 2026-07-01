# Deployment Guide

Last Updated: 2026-07-01

## Scope

目前這份指南只覆蓋：

- 本地或單機驗收環境
- SQLite-based production-like 啟動
- backup / restore baseline

不涵蓋：

- 正式 RDBMS 佈署
- Docker / container orchestration
- 雲端 secret manager

## Required Files

- `.env.example`
- `requirements.txt`
- `scripts/run_prod.ps1`
- `scripts/health_check.py`
- `scripts/backup_runtime_db.py`
- `scripts/restore_runtime_db.py`

## Minimum Environment

```powershell
$env:APP_ENV = "production"
$env:SECRET_KEY = "replace-with-a-long-random-secret"
$env:DATABASE_URL = "sqlite:///D:/CodexRuntime/rental/rebuild/runtime.db"
```

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

## Preflight

```powershell
py -3 .\scripts\health_check.py --config production
```

## Backup Before Start

```powershell
py -3 .\scripts\backup_runtime_db.py
```

## Start Server

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_prod.ps1
```

## Restore Procedure

先確認服務已停掉，再執行：

```powershell
py -3 .\scripts\restore_runtime_db.py --source .\backups\runtime_YYYYMMDD_HHMMSS.db --execute
```

## Launch Gate

啟動前至少確認：

- `pytest tests\integration -q` 通過
- `scripts/health_check.py --config production` 通過
- `run_migrations.py --list` 可列出 migration 狀態
- backup 已成功建立
- `/readyz` 回傳 `200`
