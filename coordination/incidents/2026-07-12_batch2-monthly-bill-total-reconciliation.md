# Batch 2 Monthly Bill Total Reconciliation

Status: RESOLVED - Google Sheet evidence applied
Detected: 2026-07-12
Scope: `runtime-real.db`, Batch 2 whitelist import

## Safe Import Outcome

- Backup created before migration/import: `backups/runtime_20260712_163020.db`
- Utility policy migration `20260703_000003_utility_policy_codes` applied successfully.
- Batch 2 import committed: 403 rows.
- Eight approved property policy pairs were assigned.
- `paid=NULL` normalization completed: 39 rows changed to `paid=0`.

## Reconciliation Finding

The Owner provided the monthly Google Sheet as the final business evidence:
`1WmqQbPo8EsWrbplDInp1Q3rv6bYsCcesh4BE6qYJ-dc`, tabs `202605` and `202606`.
All 11 affected rows now satisfy the expanded historical formula:

```text
total = rent + electricity_amount + public_electricity + water_amount + other_charges + previous_balance
```

`previous_balance` is signed. A positive value is prior unpaid money; a
negative value is a prior credit/overpayment, matching the legacy Sheet's
signed "未收款" column.

| Bill | Sheet month | Sheet previous balance | Applied action | Verified total |
| --- | --- | ---: | --- | ---: |
| 170 | 202605 | 17,615 | `previous_balance=17615` | 22,654 |
| 171 | 202605 | 78 | `previous_balance=78` | 4,520 |
| 172 | 202605 | -55 | `previous_balance=-55` | 5,089 |
| 567 | 202606 | -33,646 | `previous_balance=-33646` | -27,186 |
| 573 | 202606 | 5,663 | `previous_balance=5663` | 11,860 |
| 578 | 202606 | 213 | `previous_balance=213` | 5,244 |
| 819 | 202606 | 25,047 | `previous_balance=25047` | 29,710 |
| 831 | 202606 | 18,154 | `previous_balance=18154` | 22,654 |
| 832 | 202606 | 20 | `previous_balance=20` | 4,220 |
| 833 | 202606 | -11 | `previous_balance=-11` | 4,789 |
| 943 | 202605 | 0 | corrected `public_electricity: 40 -> 0` | 6,807 |

## Verification

- Direct database query confirmed all 11 rows satisfy the expanded formula.
- `pytest tests\integration -q`: `110 passed, 0 failed, 15 skipped`.
- No legacy `total` value was overwritten. All changes are source-evidence
  component or carry-forward balance corrections.

## Follow-up: Historical Payments

The 11 reconciled Sheet rows now have one verified, linked `PaymentRecord`
each. Stable IDs in the form `legacy-sheet-YYYYMM-rowN-billID` make the import
idempotent; a re-run skips all 11 existing records.

Partial payments remain correctly open: bills `170`, `171`, `578`, `831`, and
`832`. Full or overpaid entries are marked paid through linked-payment totals.
The importer preserves an empty transaction date when the Sheet provides no
date evidence. This completes payment reconciliation only for the 11 reviewed
rows; wider historical-payment import remains a separate controlled batch.
