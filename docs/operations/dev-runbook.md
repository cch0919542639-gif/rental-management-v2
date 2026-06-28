# Dev Runbook

Last Updated: 2026-06-29

## Purpose

這份文件提供其他電腦或其他 agent 在本地啟動 `rebuild` 專案的最短路徑。

## Prerequisites

- Python 3.13
- PowerShell
- Git

> **⚠️ Important — Python version**: This project requires Python 3.13 (or 3.12+).  
> The system-level `python` command on some setups may point to a different Python (e.g., Hermes Agent's 3.11 venv) that does **not** have Flask installed.  
> Always verify with:
> ```powershell
> python --version
> pip list | findstr Flask
> ```
> If Flask is missing, use the bundled Python 3.13 launcher:
> ```powershell
> py -3 --version
> ```

## Python Dependencies

安裝：

```powershell
py -3 -m pip install -r .\requirements-dev.txt
```

## First-Time Setup

1. 進入 repo 根目錄：

```powershell
cd D:\CodexRuntime\rental\rebuild
```

2. 建 demo data：

```powershell
py -3 .\scripts\seed_demo_data.py
```

3. 驗證 demo data：

```powershell
py -3 .\scripts\check_db_demo_state.py
```

4. 跑 smoke tests：

```powershell
pytest tests\integration -q
```
或
```powershell
.\scripts\run_tests.bat
```

## Start Development Server

方式一：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_dev.ps1
```

方式二：

```powershell
py -3 -m flask --app app.wsgi run --debug
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

| Command | Description |
|---------|-------------|
| `pytest tests\integration -q` | Run all integration tests (quick) |
| `.\scripts\run_tests.bat` | Same, via batch wrapper |
| `py -3 .\scripts\seed_demo_data.py` | Create / reset demo data (destructive) |
| `.\scripts\reset_demo_data.bat` | Same, via batch wrapper |
| `py -3 .\scripts\check_db_demo_state.py` | Verify demo data consistency |
| `powershell -ExecutionPolicy Bypass -File .\scripts\run_smoke_tests.ps1` | Run smoke tests via PS |
| `powershell -ExecutionPolicy Bypass -File .\scripts\github_preflight_check.ps1` | Pre-push check |

## Available Scripts

| Script | Description |
|--------|-------------|
| `scripts/seed_demo_data.py` | Drop all tables, recreate, seed demo data |
| `scripts/check_db_demo_state.py` | Verify demo data consistency (no destructive ops) |
| `scripts/run_dev.ps1` | Start Flask dev server |
| `scripts/run_smoke_tests.ps1` | Run `pytest tests\integration -q` |
| `scripts/run_tests.bat` | Same as above, batch wrapper |
| `scripts/reset_demo_data.bat` | Wrapper: drop + re-seed in one step |
| `scripts/github_preflight_check.ps1` | Check for risky files before git push |

## Available Integration Tests

| Test File | Coverage |
|-----------|----------|
| `test_auth_billing_payments_smoke.py` | Auth, dashboard, billing list, payment CRUD (create → verify → link) |
| `test_utilities_reporting_smoke.py` | Electricity meter/bill/reading/calculate/post, water create/post, reports monthly, maintenance page |
| `test_billing_placeholders_and_edges.py` | Billing edge cases (no-data month, default month) + placeholders for deeper billing tests |
| `test_payments_reject_and_status.py` | Payment reject flow, list rendering + placeholders for duplicate TXN, reconciliation |
| `test_electricity_meter_edit_and_post.py` | Meter edit, bill + reading → calculate → post to monthly bill + placeholders for status transitions |
| `test_water_edit_and_independent_post.py` | Water bill edit, independent mode post, landlord summary, yearly overview + placeholders |

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
