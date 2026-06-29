# box Completed Log — Round 01 (Water Preview)

Completed Time: 2026-06-29  
Branch: `codex-phase2-mainline-01`  
Author: box (tests / runbook / scripts agent)

---

## Summary

Added water preview edge-case tests and produced manual verification runbook. No logic changes.

**pytest: 50 passed, 15 skipped, 0 failures** (was 46; +4 from water preview tests)

---

## Deliverables

| File | Action | Description |
|------|--------|-------------|
| `docs/reports/box-phase3-water-preview-runbook-01.md` | Created | Water preview runbook with shared/independent verification steps |
| `tests/integration/test_water_preview.py` | Updated | +2 tests (GET form, POST missing field); improved robustness |

## Test Changes Detail

| Change | Reason |
|--------|--------|
| `/water/1/preview` → dynamic `water_bill_id` | Hardcoded ID was fragile across test ordering |
| `test_water_preview_get_renders_form` (new) | GET renders form, no preview result |
| `test_water_preview_post_no_monthly_bill` (new) | Missing required field → form re-renders gracefully |

## Coverage Gap Acknowledged

- Multi-contract shared preview: not tested (requires 2+ contracts — allocation logic, not test gap)
- Preview vs. actual post consistency: not tested (cross-service comparison — Phase 3)

## Constraints Honored

- ✅ No allocation rules changed
- ✅ No model/service modifications
- ✅ No schema changes
