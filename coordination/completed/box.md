# box Completed Log

Completed Time: 2026-06-29

## Completed Items

### Phase 2 — Tests / Runbook / Script 補強

#### Tests (4 new files, +8 active tests)

| File | Active Tests | Placeholders | Coverage |
|------|-------------|-------------|----------|
| `tests/integration/test_billing_placeholders_and_edges.py` | 2 | 2 | Billing edge cases (no-data month, default month); placeholders for deeper billing algorithm tests |
| `tests/integration/test_payments_reject_and_status.py` | 2 | 2 | Payment reject flow (create → reject → verify `record_status`); list rendering; placeholders for duplicate TXN & reconciliation |
| `tests/integration/test_electricity_meter_edit_and_post.py` | 2 | 2 | Meter create+edit verify; bill+reading→calculate→post to monthly bill (verify `electricity_amount > 0`); placeholders for status transitions & format |
| `tests/integration/test_water_edit_and_independent_post.py` | 4 | 1 | Water bill create+edit; independent mode post (verify `water_amount`); landlord summary; yearly overview; placeholder for shared allocation |

Total: 15 active (up from 7) + 8 placeholders (up from 0)

#### Scripts (3 new)

| Script | Description |
|--------|-------------|
| `scripts/check_db_demo_state.py` | Read-only demo DB state checker — verifies 8 consistency rules (users, landlords, properties, rooms, tenants, contracts, monthly bills, relationships) |
| `scripts/reset_demo_data.bat` | One-step wrapper: runs `seed_demo_data.py` from any directory |
| `scripts/run_tests.bat` | Batch wrapper for `pytest tests\integration -q` |

#### Documentation Updates

- `docs/operations/dev-runbook.md` — Python version warning, scripts table, test coverage table, `py -3` usage throughout
- `tests/README.md` — Phase 2 test matrix with coverage descriptions
- `scripts/README.md` — Available scripts table with descriptions and destructive flags

#### Validation

- `pytest tests\integration -q` → **15 passed, 7 skipped** ✅
- `py -3 scripts/seed_demo_data.py` → **Seed complete** ✅
- `py -3 scripts/check_db_demo_state.py` → **All checks passed** ✅

#### Constraints Honored

- ✅ No data contract modifications
- ✅ No maintenance schema additions
- ✅ No core/service rule rewrites
- ✅ No destructive reset/migration operations
- ✅ No core billing logic changes
- ✅ Placeholder tests are clearly marked `@pytest.mark.skip(reason="...")`
- ✅ Only minimal test fixture fixes (form mode values, missing relationship access)

#### Minor Fixes Made (test-required)

1. `test_electricity_meter_edit_and_post.py`: Changed `bill.readings` (no relationship) → `ElectricityReadingRepository.list_for_bill(bill_id)` — repository access, not model change.
2. `test_water_edit_and_independent_post.py`: Changed `mode: "independent"` → `mode: "independent_meter"` — the form's valid choice value is `"independent_meter"`, not the descriptive label.

## Output Files

```
tests/integration/test_billing_placeholders_and_edges.py
tests/integration/test_payments_reject_and_status.py
tests/integration/test_electricity_meter_edit_and_post.py
tests/integration/test_water_edit_and_independent_post.py
scripts/check_db_demo_state.py
scripts/reset_demo_data.bat
scripts/run_tests.bat
docs/operations/dev-runbook.md (updated)
tests/README.md (updated)
scripts/README.md (updated)
coordination/progress/box.md (updated)
coordination/completed/box.md (this file)
```
