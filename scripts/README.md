# scripts

正式工具腳本入口。

## 目前已補

- `github_preflight_check.ps1`
- `seed_demo_data.py`
- `run_dev.ps1`
- `run_smoke_tests.ps1`

## Demo Seed

```powershell
python .\scripts\seed_demo_data.py
```

## Development Server

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_dev.ps1
```

## Smoke Tests

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_smoke_tests.ps1
```
