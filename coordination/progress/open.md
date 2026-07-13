# open

Status: IN-PROGRESS
Last Updated: 2026-07-13

## Current Task
- Batch 2 legacy monthly_bills total reconciliation (11 bills) — COMPLETE

## Latest Deliverable
- `docs/reports/open-legacy-total-reconciliation-02.md` ✅ (2026-07-13)
  - 11 bills audited across 8 contracts
  - Category A (safe): 3 bills — 170, 819, 831 (already written, verified)
  - Category B (needs owner): 5 bills — 171, 573, 578, 832, 943
  - Category C (needs correction): 3 bills — 172, 567, 833
  - **Blocker**: Bill 567 has negative total (−27,186) — system error

## Deliverables
- `docs/reports/open-utility-policy-mapping-01.md` ✅ (2026-07-03)
- `docs/operations/utility-billing-policy-draft.md` ✅ (2026-07-02, commit 146902a)
- `docs/reports/open-phase4-gap-audit-01.md` ✅ (2026-06-30)
- `docs/operations/real-data-import-gate-checklist.md` ✅
- `docs/reports/open-batch1-utility-whitelist-01.md` ✅ (2026-07-03)
- `docs/reports/open-batch1-real-import-preflight-01.md` ✅ (2026-07-03)
- `docs/reports/open-batch1-real-import-execute-01.md` ✅ (2026-07-03)
- `docs/reports/open-batch2-resolver-candidates-01.md` ✅ (2026-07-03)

## Batch 1 Execute Summary
- **backup_runtime_db.py**: ✅ backup created
- **prepare_target_db.py**: ✅ 15 tables
- **import_csv_to_target.py --execute**: ✅ 308 rows committed
- **verify_import.py**: ✅ expected mismatches (demo vs real data)
- **verify_row_parity**: ✅ 6/6 tables match, 0 leakage
- **health_check.py**: ✅ DB OK, 33 active contracts, 2 expected failures
- **Status: PASS — Batch 1 import complete**

## runtime-real.db Final Counts
- landlords: 4 | properties: 5 | rooms: 36 | tenants: 36 | contracts: 36 | monthly_bills: 191 | total: 308 rows

## Batch 2 Candidates (8 properties, 53 rooms, 44 contracts, 200 bills)

| Group | Electricity | Water | PIDs | Size |
|-------|------------|-------|------|------|
| A | `bill_usage_ratio` | `bill_by_stay_days` | 1–4, 6 | 5 prop, 110 bills |
| B | `bill_usage_ratio_plus_public_share` | `bill_by_stay_days` | 5 | 1 prop, 42 bills |
| C | `bill_usage_ratio` | `free` | 21 | 1 prop, 18 bills |
| D | `fixed_rate` | `bill_by_stay_days` | 22 | 1 prop, 30 bills |

All rooms uniform. No custom module dependencies. Property 20's Room 432 documented as room-level exception.

## Excluded (12 properties)
- **Custom module** (4): PIDs 7–10 — need `single_meter_proportional`, `ct_meter_proportional`, `dual_meter_tou` engines
- **Manual confirm** (8): PIDs 12, 17–20, 23–25 — ambiguous/independent/insufficient data

## Pending
- Codex: implement resolver paths for `bill_usage_ratio`, `bill_usage_ratio_plus_public_share`, `water_bill_by_stay_days`
- Codex: update RatePolicyService gating to allow these paths
- box: Batch 2 preflight + execute
- Manual confirmation for PIDs 12, 17–20, 23–25

## Blocked
- 4 properties need custom calc module (PIDs 7-10)
- 8 properties need manual decision (PIDs 12, 17-20, 23-25)
- User/admin data not imported yet
- `reasonix-utility-schema-guard-01.md` does not exist yet

## Important Caveat
Batch 1 covers only 5 of 25 properties. Batch 2 (8 properties) brings total to 13 of 25, leaving 12 pending.
