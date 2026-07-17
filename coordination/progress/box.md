# box

Status: IN_PROGRESS
Last Updated: 2026-07-17

## Current Task

R3 PropertyExpense Test Plan & Acceptance Spec

- Branch: `agent/box-property-expense-test-plan-01`
- Baseline: `codex-phase2-mainline-01`
- Scope: Test plan for PropertyExpense CRUD, state machine, filters, export, constraints

## Completed

- [x] Read Reasonix contract (`reasonix-reporting-expansion-contract-01.md`): PropertyExpense minimum fields, state machine, invariants, FK rules
- [x] Read Open gap audit (`open-reporting-expansion-gap-audit-01.md`): R3 blocked by data contract
- [x] Read existing integration tests for conventions (`test_low_risk_crud_and_filters.py`)
- [x] Created `docs/reports/box-property-expense-test-plan-01.md`

## Deliverables

| File | Action | Description |
|------|--------|-------------|
| `docs/reports/box-property-expense-test-plan-01.md` | Created | 40 test cases across 9 areas: CRUD, state transitions, amount/category validation, property scoping, filters, export, mobile table, forbidden ops |

## Test Count

**40 test cases** in `tests/integration/test_property_expense_crud_states.py` (file not yet created)

| Area | Cases |
|------|-------|
| CRUD | 12 |
| State transitions & guards | 11 |
| Category validation | 2 |
| Property scoping | 2 |
| Date/category filters | 5 |
| CSV/XLSX export | 4 |
| Invariant guards (totals) | 3 |
| FK/cascade rules | 1 |

## Constraints Honored (Per Contract)

- ✅ No `PropertyExpense` data stored in `MonthlyBill.other_charges`
- ✅ Only `posted` records contribute to expense totals
- ✅ `amount > 0` for every record
- ✅ `category` is controlled enum (8 values)
- ✅ Hard delete of `posted`/`voided` records is blocked
- ✅ `property_id` uses `ON DELETE RESTRICT`
- ✅ `year_month` derived from `transaction_date`, not stored independently
- ✅ State machine: `draft → posted → voided`, `draft → cancelled`
