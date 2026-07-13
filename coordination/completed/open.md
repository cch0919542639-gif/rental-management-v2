# open — Completed Tasks

## 2026-06-30
- **Phase 4 gap audit**: `docs/reports/open-phase4-gap-audit-01.md`
  - Baseline: `codex-phase2-mainline-01`
  - 22 項缺口盤點（P0:6, P1:9, P2:7）
  - 互補 reasonix phase4-readiness-01 報告

## 2026-07-02
- **Gate checklist 文件補強**: `docs/operations/real-data-import-gate-checklist.md`
  - 補全 Gate A~G 的 dependency declarations
  - 補全每個 gate 專屬 stop conditions
  - 新增 Gate G 6 項 go/no-go conditions (GG-1~GG-6)
  - 新增 G8 (Maintenance) 驗證標準 6 項 (M1-M6)
  - 新增 G10 (Landlord Summary) 驗證標準 6 項 (L1-L6)
  - 保留原 6 條全局 Stop Conditions
  - 來源依據：mimo-real-data-regression-checklist-01、reasonix-phase5-db-bridge-guard-01、real-data-manual-fields-checklist

## 2026-07-03
- **Utility billing policy mapping**: `docs/reports/open-utility-policy-mapping-01.md`
  - Read old system DB (`D:\rental\rental.db`): 25 properties, ~200 contracts, all monthly_bills with utility data, all electricity_bills + electricity_readings + water_bills + calc_methods
  - Verified per-property `amount/usage` ratios across all monthly bills to distinguish `fixed_rate` from `bill_usage_ratio` from custom modules
  - Classification results:
    - `electricity_fixed_rate` (rate=5): 6 properties (11, 13-16, 22)
    - `electricity_bill_usage_ratio`: 6 properties (1-4, 6, 21)
    - `electricity_bill_usage_ratio_plus_public_share`: 1 property (5)
    - Custom module needed (not mappable): 4 properties (7 single_meter, 8 CT_meter, 9-10 dual_meter_TOU)
    - Manual confirmation needed: 8 properties (12, 17-20, 23-25)
    - `water_bill_by_stay_days`: 12 properties (1-10, 20, 22)
    - `water_free`: 13 properties (11-19, 21, 23-25)
  - Found 1 minority room exception: property 20 room 432
  - Found 0 contract-level overrides (all `electricity_rate=NULL`)
  - Updated coordination files

## 2026-07-03
- **Batch 1 real data import preflight**: `docs/reports/open-batch1-real-import-preflight-01.md`
  - Extracted whitelist data (PIDs 11,13,14,15,16) from `D:\rental\rental.db`
  - Filtered to target schema (`contracts` 59→14 cols, `monthly_bills` column reorder)
  - Audit: 191 bills, 100% fixed_rate(5) + 100% water_free = 0 violations
  - Export: 308 rows across 7 tables → `real_import/*.csv`
  - `prepare_target_db.py` → fresh `runtime-real.db` with 15 tables
  - `import_csv_to_target.py` dry-run → 308 rows, 0 FK errors, 0 failures
  - Preflight verification: all row counts match old system data
  - **Result: PASS — ready for --execute**

- **Batch 1 --execute**: `docs/reports/open-batch1-real-import-execute-01.md`
  - backup_runtime_db → backup saved
  - prepare_target_db → 15 tables created
  - import_csv_to_target.py --execute → **308 rows committed** (landlords 4, properties 5, rooms 36, tenants 36, contracts 36, monthly_bills 191)
  - verify_import: expected mismatches (demo vs real data)
  - verify_row_parity: **6/6 tables match old system whitelist data, zero leakage**
  - health_check: DB healthy, 33 active contracts, 2 expected failures (admin user out of scope, SECRET_KEY pre-existing)
  - **Result: PASS — Batch 1 import complete**
  - Caveat: only 5 of 25 properties imported; remaining 20 need policy resolvers, custom modules, or manual decisions

- **Batch 1 utility whitelist**: `docs/reports/open-batch1-utility-whitelist-01.md`
  - 5 properties confirmed for Round 1 import:
    - PID 11 自立路122巷17F — `electricity_fixed_rate`(5) + `water_free` — Low risk
    - PID 13 中正路204號 — `electricity_fixed_rate`(5) + `water_free` — Low risk
    - PID 14 和平街26號 — `electricity_fixed_rate`(5) + `water_free` — Low risk
    - PID 15 武成街33巷 — `electricity_fixed_rate`(5) + `water_free` — Low risk
    - PID 16 永平路43巷 — `electricity_fixed_rate`(5) + `water_free` — Low risk
  - Excluded 20 properties with rationale per group:
    - 7 properties need policy resolver (bill_usage_ratio group)
    - 4 properties need custom calc module
    - 8 properties need manual confirmation
    - 1 property (PID 22) excluded because water is not free
  - Property 20 / Room 432 documented as special exclusion
  - `reasonix-utility-schema-guard-01.md` noted as non-existent (may need creation)
  - Updated coordination files

## 2026-07-13
- **Batch 2 legacy total reconciliation**: `docs/reports/open-legacy-total-reconciliation-02.md`
  - 11 legacy monthly_bills with total discrepancies audited
  - Method: formula (rent + elec + pub + water + other) vs legacy total, cross-checked with unpaid chain
  - Results:
    - Category A (safe, already written): 3 bills (170, 819, 831)
    - Category B (needs owner confirmation): 5 bills (171, 573, 578, 832, 943)
    - Category C (needs correction): 3 bills (172, 567, 833)
  - Blocker: Bill 567 has negative total (−27,186) — system error requiring correction
  - Anomalies: paid non-boolean (170), created_at=NULL (943), negative diffs (172, 833, 943)
  - Chain verification: Contract 15 (170→831) and Contract 3 (819) chains verified with no double-counting

## 2026-07-03
- **Batch 2 resolver candidates**: `docs/reports/open-batch2-resolver-candidates-01.md`
  - Live-audited old system DB for 8 candidate properties: 53 rooms, 44 contracts, 200 bills
  - Classification by resolver path:
    - Group A (`bill_usage_ratio` + `bill_by_stay_days`): PIDs 1–4, 6 (5 prop, 110 bills)
    - Group B (`bill_usage_ratio_plus_public_share` + `bill_by_stay_days`): PID 5 (1 prop, 42 bills)
    - Group C (`bill_usage_ratio` + `water_free`): PID 21 (1 prop, 18 bills)
    - Group D (`fixed_rate` + `bill_by_stay_days`): PID 22 (1 prop, 30 bills)
  - Confirmed all 8 properties have uniform room-level strategy (no overrides)
  - Documented PID 20 / Room 432 as room-level exception for manual handling
  - Exclusions reaffirmed: PIDs 7–10 (custom module), PIDs 12/17–20/23–25 (manual pending)
  - Estimated Batch 2 data volume: 200 monthly bills (~2.1× Batch 1)
  - Updated coordination files
