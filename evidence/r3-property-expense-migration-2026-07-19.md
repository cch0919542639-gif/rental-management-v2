# R3 PropertyExpense Migration Evidence

Date: 2026-07-19

## Target

- Database: `D:\CodexRuntime\rental\rebuild-main\runtime.db`
- Migration: `20260717_000005_property_expenses`

## Recovery Point

- Backup: `backups/runtime_before_r3_property_expenses_20260719_001.db`
- Size: `139264` bytes

## Preflight

- `runtime-real.db` was rejected: required `properties` and `user` tables are absent.
- `runtime.db` already contained `property_expenses` and its indexes for `property_id`, `transaction_date`, `category`, `record_status`, and `created_by_id`.
- The migration was pending only because its ID had not been recorded in `schema_migration_log`.

## Execution

Command:

```powershell
$env:DATABASE_URL='sqlite:///D:/CodexRuntime/rental/rebuild-main/runtime.db'
py -3 scripts\migration\run_migrations.py --execute --id 20260717_000005_property_expenses
```

Result:

```text
Note property_expenses already exists
Applied and recorded.
```

## Post-Execution Verification

- `--list --id 20260717_000005_property_expenses` reports `applied`.
- A subsequent dry-run reports `Skip ...: already applied`.
- No existing `MonthlyBill`, `PaymentRecord`, or `Contract` rows were modified.

## Follow-up

The R3 real-data acceptance task remains ready. This operation did not create expense entries; it only recorded the already-present schema migration.
