# migrations

Phase 5A Alembic scaffold 目錄。

目前狀態：

- `alembic.ini` 已建立
- `env.py` / `script.py.mako` 已建立
- `versions/` 目錄已建立
- 已放入 placeholder baseline revision：`20260701_000001_phase5_baseline.py`
- 尚未生成正式 autogenerate baseline revision

下一步：

```powershell
py -3 -m pip install -r .\requirements.txt
$env:FLASK_APP="app.wsgi:app"
flask db migrate -m "baseline"
```

注意：

- 在 Alembic bridge 完成前，`scripts/migration/run_migrations.py` 仍是正式權威
- 不可先執行 `flask db upgrade`
- `scripts/migration/apply_20260701_000002_alembic_bridge.py` 只可 dry-run，不可在 Phase 5A execute
