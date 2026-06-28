# box

Status: DONE
Last Updated: 2026-06-29

## Current Task

Phase 2 — Tests / Runbook / Script 補強

- Branch: `agent/box-phase2-tests-runbook-01`
- Base: `origin/main`

## Scope

- 擴充 6 支 integration tests（含 2 支既有），focus on billing / payments / electricity / water / reports
- 補低風險 wrapper / check 類腳本
- 更新 runbook 與文件
- 不碰核心 business logic
- 不修改資料契約

## Completed So Far

### Tests (4 new files, 15 active tests + 7 placeholders)

- [x] `test_billing_placeholders_and_edges.py` — billing edge cases (no-data month, default month) + 2 placeholders
- [x] `test_payments_reject_and_status.py` — payment reject flow, list rendering + 2 placeholders
- [x] `test_electricity_meter_edit_and_post.py` — meter edit, bill+reading→calculate→post to monthly bill + 2 placeholders
- [x] `test_water_edit_and_independent_post.py` — water bill edit, independent mode post, landlord summary, yearly overview + 1 placeholder

### Scripts (3 new)

- [x] `scripts/check_db_demo_state.py` — read-only demo data consistency checker (8 checks)
- [x] `scripts/reset_demo_data.bat` — wrapper: drop + re-seed in one step
- [x] `scripts/run_tests.bat` — batch wrapper for `pytest tests\integration -q`

### Documentation Updates

- [x] `docs/operations/dev-runbook.md` — added Python version warning, new scripts table, new test coverage table, `py -3` usage
- [x] `tests/README.md` — added Phase 2 test table with coverage descriptions
- [x] `scripts/README.md` — added new scripts table and usage examples

### Verification

- [x] `pytest tests\integration -q` — 15 passed, 7 skipped
- [x] `py -3 scripts/seed_demo_data.py` — seed complete
- [x] `py -3 scripts/check_db_demo_state.py` — all checks passed

## Output Files

```
tests/integration/test_billing_placeholders_and_edges.py
tests/integration/test_payments_reject_and_status.py
tests/integration/test_electricity_meter_edit_and_post.py
tests/integration/test_water_edit_and_independent_post.py
scripts/check_db_demo_state.py
scripts/reset_demo_data.bat
scripts/run_tests.bat
```

## Risks / Blockers

- 無 — 所有測試與腳本均通過驗證
