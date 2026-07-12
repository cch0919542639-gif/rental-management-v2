# Real Import Operators

These scripts operate only on an explicitly selected target database. They do
not query or change `D:\rental\rental.db`.

## Batch 2 policy assignment

After the eight approved Batch 2 properties have passed import parity, assign
their resolver policies with a dry-run first:

```powershell
py -3 .\scripts\real_import\apply_batch2_utility_policies.py `
  --database-url sqlite:///D:\CodexRuntime\rental\rebuild\runtime-real.db
py -3 .\scripts\real_import\apply_batch2_utility_policies.py `
  --database-url sqlite:///D:\CodexRuntime\rental\rebuild\runtime-real.db --execute
```

The script only permits property IDs `1, 2, 3, 4, 5, 6, 21, 22`. It stops if
one is absent or already has a conflicting policy value. Take a target database
backup before `--execute`.
