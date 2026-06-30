# migration

資料遷移腳本。需有輸入、輸出、驗證、回滾說明。

## Available Entry Points

| Script | Purpose | Safety |
|--------|---------|--------|
| `migration_index.py` | 列出目前可用 migration 腳本與用途 | Read-only |
| `maintenance_legacy_scan.py` | 掃描 maintenance 遷移候選（虛擬 tenant / room.status） | Read-only |
| `_template_write_migration.py` | write-capable migration 範本，不可直接用於正式遷移 | Review-required |

## Usage

```powershell
py -3 .\scripts\migration\migration_index.py
py -3 .\scripts\migration\maintenance_legacy_scan.py
```

## Rule

- 目前 `scripts/migration/` 僅允許放入 read-only scan 或經 Codex 明確批准的 migration 腳本。
- 若腳本會修改資料，必須在檔頭寫清楚 rollback 與 verification 步驟。

## Naming Convention

- `scan_*`: 只讀盤點，不可寫入
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
