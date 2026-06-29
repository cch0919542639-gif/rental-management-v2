# box

Status: DONE
Last Updated: 2026-06-29

## Current Task

Water Preview Tests & Runbook (Round 01)

- Branch: `codex-phase2-mainline-01`
- Baseline: 50 passed, 15 skipped, 0 failures

## Completed

- [x] Explored water preview route, service, template, existing tests
- [x] Strengthened existing tests: replaced fragile hardcoded `/water/1/preview` with dynamic `water_bill_id`
- [x] Added 2 new tests: GET form render, POST with missing required field
- [x] Verified: `pytest tests/integration -q` → 50 passed (no regression)
- [x] `docs/reports/box-phase3-water-preview-runbook-01.md` — 4 tests + manual verification steps
- [x] `coordination/progress/box.md` — this file
- [x] `coordination/completed/box.md` — archival record

## Test Changes

| File | Change |
|------|--------|
| `tests/integration/test_water_preview.py` | Replaced hardcoded `water/1/preview` with dynamic ID lookup |
| `tests/integration/test_water_preview.py` | Added `test_water_preview_get_renders_form` |
| `tests/integration/test_water_preview.py` | Added `test_water_preview_post_no_monthly_bill` |

## Constraints Honored

- ✅ No allocation rule changes
- ✅ No model/service modifications
- ✅ No schema changes
- ✅ Tests are pure UI/flow coverage, not reimplementing allocation logic
