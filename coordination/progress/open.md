# open

Status: DONE
Last Updated: 2026-07-14

## Current Task
- Missing monthly bills audit for 202604/202605 backfill candidates

## Deliverables
- `docs/reports/open-missing-monthly-bills-audit-01.md`

## Summary
- Audited 34 missing bills (33 x 202604 + 1 x 202605) across old system, new system, and Google Sheet CSVs
- Classified: SAFE=25, CAUTION=6, BLOCKED=3
- 3 blockers identified (contract 21 negative due, contracts 81/83 zero due with active rent)
- Contracts matched by (tenant_id, room_id) — both systems share tenant/room entities

## Next Step
- Codex can generate backfill script from the report's column spec
- Resolve 3 BLOCKED items before bulk execution
