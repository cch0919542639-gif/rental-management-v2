# scripts

正式工具腳本入口。

## Available Scripts

| Script | Description | Destructive? |
|--------|-------------|-------------|
| `seed_demo_data.py` | Drop all tables, recreate, seed demo data | ✅ Yes (drops DB) |
| `check_db_demo_state.py` | Verify demo data consistency (read-only) | ❌ No |
| `run_dev.ps1` | Start Flask dev server | ❌ No |
| `run_smoke_tests.ps1` | Run `pytest tests\integration -q` | ❌ No |
| `run_tests.bat` | Run all integration tests (batch wrapper) | ❌ No |
| `run_single_test.bat` | Run one specific test file by name (verbose) | ❌ No |
| `reset_demo_data.bat` | Wrapper: drop + re-seed in one step | ✅ Yes |
| `seed_reset_check.ps1` | Seed, then run tests (seed/check/all modes) | ✅ Yes (seed) |
| `github_preflight_check.ps1` | Check for risky files before git push | ❌ No |

## Repair Scripts

| Script | Mode | Destructive? | Usage |
|--------|------|-------------|-------|
| `repair/year_month_audit.py` | Read-only audit | ❌ No | `py -3 .\scripts\repair\year_month_audit.py` |
| `repair/room_status_audit.py` | Read-only audit | ❌ No | `py -3 .\scripts\repair\room_status_audit.py` |
| `repair/user_table_audit.py` | Read-only audit | ❌ No | `py -3 .\scripts\repair\user_table_audit.py` |
| `repair/contract_expiry_repair.py` | Dry-run | ⚠️ `--execute` | `py -3 .\scripts\repair\contract_expiry_repair.py [--execute]` |

## Migration Scripts

See `scripts/migration/README.md`.

### Seed / Reset Demo Data

```powershell
py -3 .\scripts\seed_demo_data.py
```

Or via batch wrapper (resets + seeds):

```powershell
.\scripts\reset_demo_data.bat
```

### Verify Demo Data

```powershell
py -3 .\scripts\check_db_demo_state.py
```

### Run Tests

```powershell
pytest tests\integration -q
.\scripts\run_tests.bat
powershell -ExecutionPolicy Bypass -File .\scripts\run_smoke_tests.ps1
```

### Development Server

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_dev.ps1
```

> ⚠️ **Python version note**: If `python` resolves to the Hermes Agent venv (Python 3.11, no Flask), use `py -3` instead for all Python commands.
