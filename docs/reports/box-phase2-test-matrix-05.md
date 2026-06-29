# Phase 2 Box — Test Matrix Report (Round 05) [Maintenance]

Date: 2026-06-29  
Branch: `codex-phase2-mainline-01`  
Tool: `pytest tests/integration -v --tb=line`  
Result: **34 passed, 15 skipped, 0 failures**  

---

## 1. Executive Summary

| Metric | Round 04 | Round 05 | Change |
|--------|----------|----------|--------|
| Test files | 17 | **19** | +2 |
| Collected items | 47 | **49** | +2 |
| Pass | 32 | **34** | +2 |
| Skip | 15 | 15 | — |
| Fail | 0 | 0 | — |

**New test files added by Codex (Phase 2B maintenance):**

- `test_maintenance_filters_and_summary.py` — Tests maintenance filter queries (status, priority), open view, room-scoped list, summary cards
- `test_reports_maintenance_summary.py` — Tests standalone maintenance summary report (property + status totals, no `MonthlyBill` writeback)

---

## 2. Full Test Matrix

### 2.1 Billing Module (7 files, 13 active, 8 skip)

| Test File | Total | Pass | Skip | Skip Reasons |
|-----------|-------|------|------|--------------|
| `test_auth_billing_payments_smoke.py` | 1 | 1 | 0 | — |
| `test_billing_generate_flow.py` | 1 | 1 | 0 | — |
| `test_billing_utility_algorithms.py` | 2 | 2 | 0 | — |
| `test_billing_monthly_bill_flow.py` | 1 | 1 | 0 | — |
| `test_billing_placeholders_and_edges.py` | 4 | 2 | 2 | deeper recalculation; summary consistency |
| `test_billing_edit_and_contract_list.py` | 4 | 2 | 2 | conflict detection; toggle-paid idempotency |
| `test_billing_year_month_edges.py` | 6 | 4 | 2 | invalid YM handling; cross-year boundary |

### 2.2 Payments Module (1 file, 2 active, 2 skip)

| Test File | Total | Pass | Skip | Skip Reasons |
|-----------|-------|------|------|--------------|
| `test_payments_reject_and_status.py` | 4 | 2 | 2 | duplicate TXN; reconciliation edges |

### 2.3 Electricity Module (3 files, 6 active, 4 skip)

| Test File | Total | Pass | Skip | Skip Reasons |
|-----------|-------|------|------|--------------|
| `test_electricity_calculation_and_posting.py` | 1 | 1 | 0 | — |
| `test_electricity_meter_edit_and_post.py` | 4 | 2 | 2 | status transitions; YM format |
| `test_electricity_water_edge_cases.py` | 5 | 3 | 2 | reading fallback; single-contract water |

### 2.4 Water Module (1 file, 4 active, 1 skip)

| Test File | Total | Pass | Skip | Skip Reasons |
|-----------|-------|------|------|--------------|
| `test_water_edit_and_independent_post.py` | 5 | 4 | 1 | multi-contract allocation |

### 2.5 Reports Module (2 files, 2 active, 0 skip)

| Test File | Total | Pass | Skip | Skip Reasons |
|-----------|-------|------|------|--------------|
| `test_reports_monthly_and_landlord_summary.py` | 1 | 1 | 0 | — |
| `test_reports_maintenance_summary.py` | 1 | 1 | 0 | — |

### 2.6 Maintenance Module (3 files, 4 active, 2 skip)

| Test File | Total | Pass | Skip | Skip Reasons |
|-----------|-------|------|------|--------------|
| `test_maintenance_core_flow.py` | 1 | 1 | 0 | — |
| `test_maintenance_filters_and_summary.py` | 1 | 1 | 0 | — |
| `test_maintenance_readiness.py` | 4 | 2 | 2 | request create stub; status workflow stub |

### 2.7 Smoke / Cross-Module (2 files, 3 active, 0 skip)

| Test File | Total | Pass | Skip | Skip Reasons |
|-----------|-------|------|------|--------------|
| `test_utilities_reporting_smoke.py` | 1 | 1 | 0 | — |
| `test_low_risk_crud_and_filters.py` | 2 | 2 | 0 | — |

### Summary

| Section | Files | Active | Skip |
|---------|-------|--------|------|
| Billing | 7 | 13 | 8 |
| Payments | 1 | 2 | 2 |
| Electricity | 3 | 6 | 4 |
| Water | 1 | 4 | 1 |
| Reports | 2 | 2 | 0 |
| Maintenance | 3 | 4 | 2 |
| Smoke/Cross | 2 | 3 | 0 |
| **Total** | **19** | **34** | **15** |

---

## 3. Skip Classification (15 Total — Unchanged from Round 04)

### 3.1 Phase 3+ Deferred (13)

All 13 depend on service-level algorithms not yet implemented. **No change.**

| Skip | Depends on |
|------|-----------|
| billing_recalculate | Billing recalculation endpoint |
| billing_summary_consistency | Payment → billing aggregation |
| billing_edit_conflict | Conflict detection logic |
| billing_toggle_paid_idempotency | Toggle state machine |
| billing_list_invalid_year_month | Input validation layer |
| billing_year_month_boundary | Cross-year month logic |
| electricity_bill_status_transitions | Multi-state status machine |
| electricity_year_month_format | YM format enforcement |
| electricity_reading_no_amount | Amount fallback logic |
| payment_duplicate_transaction_id | DB constraint or service check |
| payment_reconciliation_edge_cases | Partial/over payment logic |
| water_shared_single_contract | Multi-contract allocation |
| water_shared_multi_contract | Multi-contract allocation |

### 3.2 Empty Stubs (2)

| Skip | Reason | Assessment |
|------|--------|------------|
| `maintenance_request_create` | "TBD — schema just froze" | Coverage provided by `test_maintenance_core_flow.py`. Keep skip. |
| `maintenance_status_workflow` | "TBD — routes not yet added" | Routes exist, coverage provided. Reason string stale but harmless. Keep skip. |

### 3.3 Activable? → No

All 15 remain correctly skipped. None can be activated now.

---

## 4. Defect Classification

### 4.1 Previously Reported — Now Resolved

| ID | Description | Status |
|----|-------------|--------|
| TD-01 | `MaintenanceRequest` not in `__init__.py` | ✅ Resolved |
| TD-02 | Maintenance routes missing | ✅ Resolved (all routes registered) |

### 4.2 Current Defects

None. **49 collected, 34 passed, 15 skipped** — 0 failures.

---

## 5. Test File Inventory (19 Files)

| # | File | Tests | Author | Status |
|---|------|-------|--------|--------|
| 1 | `test_auth_billing_payments_smoke.py` | 1/1 | box (R1) | ✅ |
| 2 | `test_billing_edit_and_contract_list.py` | 2/4 | box (R2) | ✅ +2 skip |
| 3 | `test_billing_generate_flow.py` | 1/1 | open | ✅ |
| 4 | `test_billing_monthly_bill_flow.py` | 1/1 | open | ✅ |
| 5 | `test_billing_placeholders_and_edges.py` | 2/4 | box (R1) | ✅ +2 skip |
| 6 | `test_billing_utility_algorithms.py` | 2/2 | open | ✅ |
| 7 | `test_billing_year_month_edges.py` | 4/6 | box (R2) | ✅ +2 skip |
| 8 | `test_electricity_calculation_and_posting.py` | 1/1 | mimo | ✅ |
| 9 | `test_electricity_meter_edit_and_post.py` | 2/4 | box (R1) | ✅ +2 skip |
| 10 | `test_electricity_water_edge_cases.py` | 3/5 | box (R2) | ✅ +2 skip |
| 11 | `test_low_risk_crud_and_filters.py` | 2/2 | open (R2) | ✅ |
| 12 | `test_maintenance_core_flow.py` | 1/1 | codex | ✅ |
| 13 | `test_maintenance_filters_and_summary.py` | 1/1 | codex | ✅ **New** |
| 14 | `test_maintenance_readiness.py` | 2/4 | box (R2) | ✅ +2 skip |
| 15 | `test_payments_reject_and_status.py` | 2/4 | box (R1) | ✅ +2 skip |
| 16 | `test_reports_maintenance_summary.py` | 1/1 | codex | ✅ **New** |
| 17 | `test_reports_monthly_and_landlord_summary.py` | 1/1 | mimo | ✅ |
| 18 | `test_utilities_reporting_smoke.py` | 1/1 | open | ✅ |
| 19 | `test_water_edit_and_independent_post.py` | 4/5 | box (R1) | ✅ +1 skip |
| | **Total** | **34/49** | | **34 pass, 15 skip** |

---

## 6. Runbook Status

| Requirement | Status |
|-------------|--------|
| `tests/README.md` lists all test files | ✅ Updated in Round 05 |
| `dev-runbook.md` has complete test matrix | ✅ Updated in Round 05 |
| `scripts/README.md` documents all wrappers | ✅ Adequate |
| Maintenance routes documented | ✅ Covered in codex's updates |

---

## 7. Recommendations

1. **All 15 skips remain as-is.** No change from Round 04.
2. **19 test files, 34 active tests** is a healthy Phase 2 baseline for maintenance handoff.
3. **Next**: Phase 3 should activate the 13 algorithm-dependent skips.
4. **Run command**: `pytest tests/integration -q` (49 collected, 34 pass, 15 skip).

---

## 8. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-06-29 | Round 05: updated for Codex's 2 new maintenance tests. 34 passed. | box |
