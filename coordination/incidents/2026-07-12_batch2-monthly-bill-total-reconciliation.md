# Batch 2 Monthly Bill Total Reconciliation

Status: OPEN - manual business decision required
Detected: 2026-07-12
Scope: `runtime-real.db`, Batch 2 whitelist import

## Safe Import Outcome

- Backup created before migration/import: `backups/runtime_20260712_163020.db`
- Utility policy migration `20260703_000003_utility_policy_codes` applied successfully.
- Batch 2 import committed: 403 rows.
- Eight approved property policy pairs were assigned.
- `paid=NULL` normalization completed: 39 rows changed to `paid=0`.

## Reconciliation Finding

Eleven imported `monthly_bills` initially did not satisfy the formula that was
available before the carry-forward balance field was introduced.

```text
total = rent + electricity_amount + public_electricity + water_amount + other_charges
```

Every one of the 11 rows was compared field-for-field to `D:\rental\rental.db`.
All 11 values match the legacy source exactly. This is legacy data quality, not
an exporter or importer mapping fault.

### Resolved Entry

Bill `819` is resolved by the confirmed business explanation: current charges
are rent `4,465` plus other charge `198`, and `25,047` is a prior unpaid
balance. It is now stored as `previous_balance=25047`; the total remains
`29,710` and the expanded formula reconciles.

| Property ID | Bill IDs | Months | Observation |
| --- | --- | --- | --- |
| 3 | 170, 171, 172, 831, 832, 833 | 202605-202606 | Several totals appear copied from a property aggregate or a different-room result. |
| 5 | 567 | 202606 | `total=-27186`; requires explicit source-business verification. |
| 6 | 573, 578 | 202606 | Imported total differs from the stored fee components. |
| 22 | 943 | 202605 | Difference is 40, equal to `public_electricity`; legacy total may have excluded public electricity. |

## Forbidden Automatic Actions

- Do not overwrite the remaining 10 `total` values from the formula without Owner approval.
- Do not delete and re-import the Batch 2 bundle.
- Do not run bulk recalculation across Batch 2, because the historical values
  may carry old-system exceptions that need evidence.

## Required Decision

For each remaining affected row or an approved category, choose one:

1. Preserve legacy `total` and mark it reviewed.
2. Replace `total` with the frozen five-component formula.
3. Correct the individual component fields from source evidence, then recalculate.

Until resolved, Batch 2 is usable for navigation and policy configuration but
is not financially reconciled for the remaining 10 bill rows.
