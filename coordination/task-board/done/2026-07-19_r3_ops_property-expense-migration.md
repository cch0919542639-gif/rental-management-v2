# Title

R3 Property Expense Production Migration

## Owner

Database Operator / Owner

## Phase

R3 Production Readiness

## Goal

Safely record `20260717_000005_property_expenses` on the approved runtime database.

## Allowed Files

- `backups/*`
- `evidence/*`
- `docs/reports/*`
- `coordination/*`

## Do Not Touch

- Existing `MonthlyBill`, `PaymentRecord`, and `Contract` data
- Non-R3 migrations

## Acceptance

- [x] Recovery backup created.
- [x] Read-only preflight selected `runtime.db`; `runtime-real.db` was rejected because base tables are absent.
- [x] Existing R3 table and indexes verified before execution.
- [x] Migration recorded as applied.
- [x] Read-only rerun reports `already applied`.
- [x] Evidence recorded in `evidence/r3-property-expense-migration-2026-07-19.md`.

## Dependencies

- `40c2090 feat: add property expense ledger`
- Owner authorization received 2026-07-19.

## Status

DONE
