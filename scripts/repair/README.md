# repair

資料修復腳本。需對應 incident 或契約文件，不接受一次性匿名腳本。

## Available Scripts

| Script | Purpose | Default Mode |
|--------|---------|--------------|
| `year_month_audit.py` | 稽核 `monthly_bills` / `electricity_bills` 的 `year_month` 長度與異常值 | Read-only |
| `room_status_audit.py` | 稽核 `rooms.status` 是否只含 `vacant` / `occupied` | Read-only |
| `contract_expiry_repair.py` | 檢查並修正已過期但仍為 `active` 的合約 | Dry-run |
| `user_table_audit.py` | 稽核 `user` / `users` 雙表是否同時存在與筆數差異 | Read-only |

## Usage

```powershell
py -3 .\scripts\repair\year_month_audit.py
py -3 .\scripts\repair\room_status_audit.py
py -3 .\scripts\repair\contract_expiry_repair.py
py -3 .\scripts\repair\contract_expiry_repair.py --execute
py -3 .\scripts\repair\user_table_audit.py
```

## Rule

- 預設必須是 read-only 或 dry-run
- 真正寫入的修復腳本必須先列出候選摘要
- 禁止在未審查情況下直接刪除資料

## Write Convention

- 預設模式必須是 dry-run 或 read-only
- 寫入腳本必須支援 `--execute`
- 若涉及日期判定，應支援 `--reference-date YYYY-MM-DD`
- 寫入前必須先印出候選筆數與受影響資料摘要
- 檔頭必須交代 rollback note
