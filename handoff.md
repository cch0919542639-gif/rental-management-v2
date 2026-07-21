# Handoff — 2026-07-22

## Current objective and status

- 2026-04 through 2026-06 Google-source reconciliation is complete in the isolated staging database:
  `staging/runtime-google-rebuild-through-202606-v4.db`.
- July is deliberately excluded; wait for the user to strengthen the July source before building a new staging version.
- `runtime-real.db` was not written. Its SHA-256 remains
  `2e43fa710e4330985a8dca89310f9dea589754be3f0248c331cc59f9b7a3a04c`.

## Changed areas

- Move-out settlement reporting, owner-scoped access, CSV/XLSX export, and integration tests.
- Google-source staging rebuild scripts and the 4–6 month reconciliation record.
- Persistent workflow rules in `AGENTS.md` and this handoff.

## Validation

- `py -3 -m pytest -q tests\integration\test_move_out_settlement_report.py tests\integration\test_move_out_settlements.py tests\integration\test_reporting_expansion.py`
  - `13 passed, 1 warning`.
- `py -3 -m py_compile scripts\rebuild_google_staging_db.py`
  - passed.
- SQLite `PRAGMA integrity_check` for the 4–6 month staging database: `ok`.

## Next step and risks

- Next: receive the strengthened July source, create a July-inclusive staging version, reconcile it, then request separate explicit authorization before any formal-database migration.
- Do not commit `staging/`: it contains local databases and downloaded Google-source data.
- Do not include `.agents/` in project commits; it is local workspace metadata.

## Final updater and Git state

- Final updater: Codex.
- Computer: `技嘉202509`.
- Branch: `agent/box-property-expense-verify-01`.
- Push state: committed locally as `699908a`; GitHub push is pending the user's confirmation that `origin` is an approved private destination for this repository and its evidence files.
