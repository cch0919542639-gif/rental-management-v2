# box

Status: DONE
Last Updated: 2026-07-14

## Current Task

Missing Monthly Bills Backfill — Dry-Run & Script (Round 02)

- Branch: `agent/box-safe-monthly-backfill-01`
- Baseline: `codex-phase2-mainline-01`
- Scope: 24 safe 202604 candidates + 1 safe 202605 candidate

## Completed

- [x] Read guard report `docs/reports/reasonix-missing-monthly-bills-guard-01.md`
- [x] Read audit/CSV/DB schema for contract→room→property mapping
- [x] Created `scripts/repair/backfill_missing_monthly_bills.py` with 9 stop conditions
- [x] Dry-run on runtime-real.db: 202604 → 24 SAFE, 129 SKIP, 0 STOP
- [x] Dry-run on runtime-real.db: 202605 → 1 SAFE, 152 SKIP, 0 STOP
- [x] Integration tests: 10 tests covering dry-run/execute/skip/stop conditions
- [x] `pytest tests/integration -q` → 60 passed (was 50; +10 new tests)
- [x] Updated `scripts/repair/README.md`, `coordination/progress/box.md`, `coordination/completed/box.md`
- [x] Branch, commit, push

## Test Changes

| File | Change |
|------|--------|
| `tests/integration/test_backfill_missing_monthly_bills.py` | Created (10 tests) |
| `scripts/repair/backfill_missing_monthly_bills.py` | Created |
| `scripts/repair/README.md` | Updated with new script |

## Constraints Honored

- ✅ No schema, model, service, route, or template modifications
- ✅ Dry-run by default; `--execute` required to persist
- ✅ `paid=False`, `paid_date=None` on all created bills
- ✅ `total` recalculated via `MonthlyBill.calculate_total()`
- ✅ 202604: `previous_balance=0`, notes includes "前期差額無證據，設為0"
- ✅ 202605: `previous_balance` from Sheet 未收款 column
- ✅ Stop conditions: rent diff >100, total diff >10, virtual tenant, stop-list, duplicate, no contract, rent=0
- ✅ No PaymentRecord creation
- ✅ All stop-list tenants skipped: 張硯傑, 張啟中, 邱聖霖, 高富國, 侯家敏, 李政諺, 何佾洋, 鄭博仁, 田美麗