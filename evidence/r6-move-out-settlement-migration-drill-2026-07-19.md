# R6 Move-Out Settlement Migration Drill

Date: 2026-07-19 14:34 (Asia/Taipei)

## Scope

The accepted R6 migration rehearsal was executed only against the copied populated
SQLite database `backups/runtime_20260719_143424.db`. Its source was
`D:/CodexRuntime/rental/rebuild/runtime-real.db`; that source was not modified.

## Prerequisite Finding

The initially inspected path, `D:/CodexRuntime/rental/rebuild-main/runtime-real.db`,
contains only `schema_migration_log`; it is not the populated imported-data runtime.
The populated imported-data runtime is instead
`D:/CodexRuntime/rental/rebuild/runtime-real.db`.

## Procedure And Result

1. Created the rehearsal copy from the populated source with:
   `DATABASE_URL=sqlite:///D:/CodexRuntime/rental/rebuild/runtime-real.db python scripts/backup_runtime_db.py`
2. Recorded baseline counts on the copy: `properties=13`, `contracts=80`,
   `monthly_bills=421`, `payment_records=175`, `rooms=89`, `tenants=80`, and `user=1`.
3. Executed only `20260719_000006_move_out_settlements` against the copy.
4. Confirmed the new tables exist:
   - `move_out_settlements`
   - `move_out_settlement_allocations`
5. Confirmed the migration log contains `20260719_000006_move_out_settlements`.
6. Confirmed all baseline core-table counts remained unchanged and both R6 tables are empty.
7. Re-ran the migration: the runner reported it as already applied, confirming
   idempotent retry behavior.

## Foreign-Key Check

- `move_out_settlements` references `contracts`, `monthly_bills`, and `user`.
- `move_out_settlement_allocations` references `move_out_settlements` and `user`.

## Result And Limitation

Populated-data schema migration rehearsal: **passed**.

The prior empty-schema rehearsal copy (`runtime_20260719_141457.db`) is superseded
and must not be used as production-readiness evidence.
