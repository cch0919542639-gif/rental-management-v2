# migration

資料遷移腳本。需有輸入、輸出、驗證、回滾說明。

## Available Entry Points

| Script | Purpose | Safety |
|--------|---------|--------|
| `migration_index.py` | 列出目前可用 migration 腳本與用途 | Read-only |
| `run_migrations.py` | 列出 / dry-run / execute `apply_*` migration，並記錄已套用 ID | Review-required |
| `apply_20260701_000001_phase4_baseline_marker.py` | 建立第一個 tracked migration baseline，不改 domain tables | Safe write |
| `apply_20260701_000002_alembic_bridge.py` | 在 cutover 前將 Alembic revision table 與 custom runner 對齊 | Review-required |
| `maintenance_legacy_scan.py` | 掃描 maintenance 遷移候選（虛擬 tenant / room.status） | Read-only |
| `export_sqlite_to_pg.py` | 盤點 / 匯出 SQLite 資料為 CSV + manifest，供 PostgreSQL drill 使用 | Read-only-first |
| `verify_row_parity.py` | 比對 source / target 每張表的筆數是否一致 | Read-only |
| `bridge_drill_checklist.py` | 檢查 bridge rehearsal 前置條件、manifest、migration 狀態 | Read-only |
| `_template_write_migration.py` | write-capable migration 範本，不可直接用於正式遷移 | Review-required |

## Usage

```powershell
py -3 .\scripts\migration\migration_index.py
py -3 .\scripts\migration\run_migrations.py --list
py -3 .\scripts\migration\maintenance_legacy_scan.py
py -3 .\scripts\migration\export_sqlite_to_pg.py
py -3 .\scripts\migration\verify_row_parity.py --source-url sqlite:///source.db --target-url sqlite:///target.db
py -3 .\scripts\migration\bridge_drill_checklist.py
py -3 .\scripts\migration\run_migrations.py --execute --id 20260701_000002_alembic_bridge --allow-bridge
```

## Rule

- 目前 `scripts/migration/` 僅允許放入 read-only scan 或經 Codex 明確批准的 migration 腳本。
- 若腳本會修改資料，必須在檔頭寫清楚 rollback 與 verification 步驟。
- 正式 `apply_*` migration 應透過 `run_migrations.py` 執行，不要直接 `python apply_*.py`
- `apply_20260701_000002_alembic_bridge.py` 只能在 Phase 5B gate 開啟後執行，Phase 5A 僅允許 dry-run 與審查
- Alembic bridge execute 必須額外帶 `--allow-bridge`，且所有前序 migration 都必須已套用

## Naming Convention

- `scan_*`: 只讀盤點，不可寫入
- `export_*`: 預設 dry-run，僅在 `--execute` 下輸出檔案，不可修改來源 DB
- `verify_*`: 只讀驗證，不可寫入
- `*_checklist.py`: 只讀前置檢查，不可寫入
- `plan_*`: 產出候選、預計影響範圍、人工審查資料，不可寫入
- `apply_*`: 真正可寫入的 migration，預設必須是 dry-run，且僅在 `--execute` 下寫入

## Write-Safe Convention

- 預設模式必須是 read-only 或 dry-run
- 寫入型 migration 必須支援 `--execute`
- 若有日期判定，應支援 `--reference-date YYYY-MM-DD`
- 執行前必須印出候選筆數與受影響資料摘要
- 執行後必須提供 verification 指引
- 檔頭必須交代 rollback note
- 未經 Codex 明確批准，不得把高風險資料修復腳本放進 `apply_*`
