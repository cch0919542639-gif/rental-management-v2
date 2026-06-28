# Dev Runbook

Last Updated: 2026-06-28 15:18

## Purpose

這份文件提供其他電腦或其他 agent 在本地啟動 `rebuild` 專案的最短路徑。

## Prerequisites

- Python 3.13
- PowerShell
- Git

## Python Dependencies

安裝：

```powershell
python -m pip install -r .\requirements-dev.txt
```

## First-Time Setup

1. 進入 repo 根目錄：

```powershell
cd D:\CodexRuntime\rental\rebuild
```

2. 建 demo data：

```powershell
python .\scripts\seed_demo_data.py
```

3. 跑 smoke tests：

```powershell
pytest tests\integration -q
```

## Start Development Server

方式一：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_dev.ps1
```

方式二：

```powershell
python -m flask --app app.wsgi run --debug
```

預設 URL：

- `http://127.0.0.1:5000`

## Demo Login

- Username: `admin`
- Password: `admin123`

## Quick Verification

啟動後至少驗證以下頁面：

- `/auth/login`
- `/`
- `/billing/`
- `/payments/`
- `/electricity/`
- `/water/`
- `/reports/`
- `/maintenance/`

## Common Commands

跑 smoke tests：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_smoke_tests.ps1
```

重新建立 demo data：

```powershell
python .\scripts\seed_demo_data.py
```

檢查 GitHub 上傳前狀態：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\github_preflight_check.ps1
```

## Current Limitations

- `maintenance` 只有模組入口，正式 schema 尚未凍結
- deeper billing / electricity / water algorithm 尚未完成
- migration 與正式資料導入未完成

## Required Read Before Work

- `docs/operations/phase1-master-status.md`
- `docs/operations/current-dispatch-and-handoff-plan.md`
- `coordination/progress/codex.md`

## Before Handing Off

- 更新自己的 `coordination/progress/<agent>.md`
- 若完成工作，更新 `coordination/completed/<agent>.md`
- 若被阻塞，建立 `coordination/incidents/<timestamp>_<agent>_<topic>.md`
