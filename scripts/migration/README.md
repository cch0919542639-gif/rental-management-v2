# migration

資料遷移腳本。需有輸入、輸出、驗證、回滾說明。

## Available Entry Points

| Script | Purpose | Safety |
|--------|---------|--------|
| `migration_index.py` | 列出目前可用 migration 腳本與用途 | Read-only |
| `maintenance_legacy_scan.py` | 掃描 maintenance 遷移候選（虛擬 tenant / room.status） | Read-only |

## Usage

```powershell
py -3 .\scripts\migration\migration_index.py
py -3 .\scripts\migration\maintenance_legacy_scan.py
```

## Rule

- 目前 `scripts/migration/` 僅允許放入 read-only scan 或經 Codex 明確批准的 migration 腳本。
- 若腳本會修改資料，必須在檔頭寫清楚 rollback 與 verification 步驟。
