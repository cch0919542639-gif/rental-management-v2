# Dev Runbook

Last Updated: 2026-06-30

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

production runtime 最小安裝：

```powershell
py -3 -m pip install -r .\requirements.txt
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

## Start Production-Like Server

最低要求：

- `APP_ENV=production`
- `SECRET_KEY` 必填

啟動：

```powershell
$env:SECRET_KEY = "replace-with-real-secret"
powershell -ExecutionPolicy Bypass -File .\scripts\run_prod.ps1
```

可選自訂 host / port：

```powershell
$env:SECRET_KEY = "replace-with-real-secret"
powershell -ExecutionPolicy Bypass -File .\scripts\run_prod.ps1 -Host 127.0.0.1 -Port 8000
```

預設 URL：

- `http://127.0.0.1:8000`

readiness check：

```powershell
curl http://127.0.0.1:8000/readyz
```

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
| `powershell -ExecutionPolicy Bypass -File .\scripts\run_prod.ps1` | Start production-like Waitress server |
| `powershell -ExecutionPolicy Bypass -File .\scripts\github_preflight_check.ps1` | Pre-push check |
| `py -3 .\scripts\health_check.py --config production` | Run preflight health check |
| `py -3 .\scripts\migration\migration_index.py` | List available migration entry scripts (read-only) |
| `py -3 .\scripts\migration\run_migrations.py --list` | List tracked apply migrations and status |
| `py -3 .\scripts\migration\maintenance_legacy_scan.py` | Scan legacy maintenance migration candidates (read-only) |

## Available Scripts

| Script | Description |
|--------|-------------|
| `scripts/seed_demo_data.py` | Drop all tables, recreate, seed demo data |
| `scripts/check_db_demo_state.py` | Verify demo data consistency (no destructive ops) |
| `scripts/run_dev.ps1` | Start Flask dev server |
| `scripts/run_prod.ps1` | Start production-like Waitress server |
| `scripts/run_production.py` | Python entrypoint for Waitress server |
| `scripts/health_check.py` | Read-only production preflight health check |
| `scripts/run_smoke_tests.ps1` | Run `pytest tests\integration -q` |
| `scripts/run_tests.bat` | Same as above, batch wrapper |
| `scripts/run_single_test.bat` | Run one integration test file by name |
| `scripts/reset_demo_data.bat` | Wrapper: drop + re-seed in one step |
| `scripts/seed_reset_check.ps1` | Seed + check in one command |
| `scripts/github_preflight_check.ps1` | Check for risky files before git push |

## Available Repair Scripts

| Script | Mode | Destructive? | Usage |
|--------|------|-------------|-------|
| `scripts/repair/year_month_audit.py` | Read-only audit | ❌ No | `py -3 .\scripts\repair\year_month_audit.py` |
| `scripts/repair/room_status_audit.py` | Read-only audit | ❌ No | `py -3 .\scripts\repair\room_status_audit.py` |
| `scripts/repair/user_table_audit.py` | Read-only audit | ❌ No | `py -3 .\scripts\repair\user_table_audit.py` |
| `scripts/repair/contract_expiry_repair.py` | Dry-run | ⚠️ `--execute` | `py -3 .\scripts\repair\contract_expiry_repair.py [--execute]` |

## Integration Skeletons

| Module | Type | Endpoint | Status |
|--------|------|----------|--------|
| `app/integrations/line_webhook.py` | Route placeholder | `POST /integrations/line/callback` | Returns 501 (Phase 3) |
| `app/integrations/ocr_client.py` | Protocol interface | — | Interface only, no impl |
| `app/integrations/sheets_client.py` | Protocol interface | — | Interface only, no impl |
| `scripts/migration/migration_index.py` | List available migration scripts and safety notes |
| `scripts/migration/maintenance_legacy_scan.py` | Scan legacy maintenance migration candidates |

## Available Integration Tests

| Test File | Active | Skip | Coverage | Author |
|-----------|--------|------|----------|--------|
| `test_auth_billing_payments_smoke.py` | 1 | 0 | Auth, dashboard, billing list, payment CRUD | box R1 |
| `test_billing_edit_and_contract_list.py` | 2 | 2 | Billing edit (total recalc), contract list page | box R2 |
| `test_billing_generate_flow.py` | 1 | 0 | Billing create, toggle-paid, generate, batch | open |
| `test_billing_monthly_bill_flow.py` | 1 | 0 | Billing view + payment linking | open |
| `test_billing_placeholders_and_edges.py` | 2 | 2 | Billing edge cases (no-data, default month) | box R1 |
| `test_billing_utility_algorithms.py` | 2 | 0 | Electricity rate fallback, water shared alloc | open |
| `test_billing_year_month_edges.py` | 4 | 2 | YYYYMM/YYYY-MM format, UI→DB storage | box R2 |
| `test_electricity_calculation_and_posting.py` | 1 | 0 | Electricity calculate + idempotency | mimo |
| `test_electricity_meter_edit_and_post.py` | 2 | 2 | Meter edit, bill→post to monthly bill | box R1 |
| `test_electricity_property_detail.py` | 1 | 0 | Property detail page (summary, meters, bills) | codex |
| `test_electricity_property_workflows.py` | 1 | 0 | new-bill → quick-reading → reading-log flow | codex |
| `test_electricity_water_edge_cases.py` | 3 | 2 | Water min/large amounts, multi-bill same meter | box R2 |
| `test_low_risk_crud_and_filters.py` | 2 | 0 | Property filter, low-risk delete | open R2 |
| `test_maintenance_core_flow.py` | 1 | 0 | Maintenance create + status transitions | codex |
| `test_maintenance_filters_and_summary.py` | 1 | 0 | Maintenance filters, open view, room list | codex |
| `test_maintenance_readiness.py` | 2 | 2 | Maintenance page, room_snapshot struct | box R2 |
| `test_nested_creation_routes.py` | 2 | 0 | Nested property→landlord, room→property | codex |
| `test_payments_reject_and_status.py` | 2 | 2 | Payment reject flow, list rendering | box R1 |
| `test_reports_maintenance_summary.py` | 1 | 0 | Maintenance summary report | codex |
| `test_reports_monthly_and_landlord_summary.py` | 1 | 0 | Monthly report with payment + paid status | mimo |
| `test_utilities_reporting_smoke.py` | 1 | 0 | Electricity/water/reports/maintenance smoke | open |
| `test_water_edit_and_independent_post.py` | 4 | 1 | Water edit, independent post, reports | box R1 |
| | **38** | **15** | | |

## Error Pages

目前本地開發版已提供正式 HTML 錯誤頁：

- `/missing-route` 會回傳 `404` 頁面
- 未預期例外會回傳 `500` 頁面

這些頁面是給本地操作與驗收使用，不代表 production-ready 設計。

## Migration Entry

在做任何 migration 相關工作前，先跑：

```powershell
py -3 .\scripts\migration\migration_index.py
```

若是 maintenance 舊資料盤點，使用：

```powershell
py -3 .\scripts\migration\maintenance_legacy_scan.py
```

若要執行正式 tracked migration 流程，先跑：

```powershell
py -3 .\scripts\migration\run_migrations.py --list
```

## Current Limitations

- deeper billing / electricity / water algorithm 尚未完成
- migration 與正式資料導入未完成
- integrations 目前只做到主幹邊界與本地流程，尚未實作外部正式串接

## Required Read Before Work

- `docs/operations/phase1-master-status.md`
- `docs/operations/current-dispatch-and-handoff-plan.md`
- `coordination/progress/codex.md`

## Before Handing Off

- 更新自己的 `coordination/progress/<agent>.md`
- 若完成工作，更新 `coordination/completed/<agent>.md`
- 若被阻塞，建立 `coordination/incidents/<timestamp>_<agent>_<topic>.md`
