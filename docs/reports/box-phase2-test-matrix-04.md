# Phase 2 Box — Test Matrix Report (Round 04)

Date: 2026-06-29  
Branch: `codex-phase2-mainline-01`  
Tool: `pytest tests/integration -v --tb=line`  
Result: **32 passed, 15 skipped, 0 failures**  

---

## 1. Executive Summary

| Metric | Round 03 (origin/main) | Round 04 (codex-phase2-mainline-01) | Change |
|--------|----------------------|--------------------------------------|--------|
| Test files | 16 | 17 | +1 (`test_low_risk_crud_and_filters.py`) |
| Pass | 29 | 32 | +3 |
| Skip | 15 | 15 | — |
| Fail | 1 (`test_maintenance_core_flow.py` → 404) | **0** | ✅ Resolved |
| Collection errors | 1 | **0** | ✅ Resolved |

**Key wins on this branch:**

- `test_maintenance_core_flow.py` **now passes** — maintenance routes (`/maintenance/create`, `/<id>/transition/*`) have been added by codex
- `test_low_risk_crud_and_filters.py` added (replaces old broken `test_low_risk_crud.py`) — 2/2 pass
- `app/models/__init__.py` now correctly exports `MaintenanceRequest` — import error gone
- **100% of collected tests pass**: 32/32 active, 15/15 skips intentional

---

## 2. Full Test Matrix

### 2.1 Billing Module

| Test File | Total | Pass | Skip | Skip Reasons | Verdict |
|-----------|-------|------|------|--------------|---------|
| `test_auth_billing_payments_smoke.py` | 1 | 1 | 0 | — | ✅ |
| `test_billing_generate_flow.py` | 1 | 1 | 0 | — | ✅ |
| `test_billing_utility_algorithms.py` | 2 | 2 | 0 | — | ✅ |
| `test_billing_monthly_bill_flow.py` | 1 | 1 | 0 | — | ✅ |
| `test_billing_placeholders_and_edges.py` | 4 | 2 | 2 | deeper recalculation; summary consistency | ✅ |
| `test_billing_edit_and_contract_list.py` | 4 | 2 | 2 | conflict detection; toggle-paid idempotency | ✅ |
| `test_billing_year_month_edges.py` | 6 | 4 | 2 | invalid YM error handling; cross-year boundary | ✅ |

### 2.2 Payments Module

| Test File | Total | Pass | Skip | Skip Reasons | Verdict |
|-----------|-------|------|------|--------------|---------|
| `test_payments_reject_and_status.py` | 4 | 2 | 2 | duplicate TXN; reconciliation edges | ✅ |

### 2.3 Electricity Module

| Test File | Total | Pass | Skip | Skip Reasons | Verdict |
|-----------|-------|------|------|--------------|---------|
| `test_electricity_calculation_and_posting.py` | 1 | 1 | 0 | — | ✅ |
| `test_electricity_meter_edit_and_post.py` | 4 | 2 | 2 | status transitions; YM format | ✅ |
| `test_electricity_water_edge_cases.py` | 5 | 3 | 2 | reading amount fallback; single-contract water | ✅ |

### 2.4 Water Module

| Test File | Total | Pass | Skip | Skip Reasons | Verdict |
|-----------|-------|------|------|--------------|---------|
| `test_water_edit_and_independent_post.py` | 5 | 4 | 1 | multi-contract shared allocation | ✅ |

### 2.5 Reports Module

| Test File | Total | Pass | Skip | Skip Reasons | Verdict |
|-----------|-------|------|------|--------------|---------|
| `test_reports_monthly_and_landlord_summary.py` | 1 | 1 | 0 | — | ✅ |

### 2.6 Maintenance Module

| Test File | Total | Pass | Skip | Skip Reasons | Verdict |
|-----------|-------|------|------|--------------|---------|
| `test_maintenance_core_flow.py` | 1 | 1 | 0 | — | ✅ **Now passing** |
| `test_maintenance_readiness.py` | 4 | 2 | 2 | request create stub; status workflow stub | ✅ (stubs) |

### 2.7 Smoke / Cross-Module

| Test File | Total | Pass | Skip | Skip Reasons | Verdict |
|-----------|-------|------|------|--------------|---------|
| `test_utilities_reporting_smoke.py` | 1 | 1 | 0 | — | ✅ |
| `test_low_risk_crud_and_filters.py` | 2 | 2 | 0 | — | ✅ **New** |

---

## 3. Skip Classification (15 Total)

### 3.1 Temporarily Reasonable — Deferred to Phase 3+ (13)

These depend on service-level algorithms, rate logic, or error-handling paths not yet implemented:

| Skip | Depends on |
|------|-----------|
| billing_recalculate | Billing recalculation endpoint (Phase 3) |
| billing_summary_consistency | Payment → billing aggregation (Phase 3) |
| billing_edit_conflict | Conflict detection on duplicate contract+month (Phase 3) |
| billing_toggle_paid_idempotency | Toggle state machine (Phase 3) |
| billing_list_invalid_year_month | Input validation layer (Phase 3) |
| billing_year_month_boundary | Cross-year month logic (Phase 3) |
| electricity_bill_status_transitions | Multi-state status machine (Phase 3) |
| electricity_year_month_format | YM format consistency enforcement (Phase 3) |
| electricity_reading_no_amount | Amount fallback logic (Phase 3) |
| payment_duplicate_transaction_id | DB unique constraint or service check (Phase 3) |
| payment_reconciliation_edge_cases | Partial/over payment logic (Phase 3) |
| water_shared_single_contract | Multi-contract allocation (Phase 3) |
| water_shared_multi_contract | Multi-contract allocation (Phase 3) |

**Recommendation: Keep all 13 as `@pytest.mark.skip`. They document future test points.**

### 3.2 Stale Skip Reason — But Still Correct to Skip (2)

| Skip | Reason String | Assessment | Recommendation |
|------|--------------|------------|---------------|
| `maintenance_request_create` | "TBD — schema just froze" | Schema is frozen; `test_maintenance_core_flow.py` creates requests successfully. But this test is an empty stub (`...`). | Keep skip. No point activating an empty stub. Reason string is slightly stale but harmless. |
| `maintenance_status_workflow` | "TBD — routes not yet added" | Routes ARE added — `test_maintenance_core_flow.py` transitions through all 5 states. But this test is an empty stub. | Keep skip. Routes exist but test body is empty. Reason string should be updated to "covered by test_maintenance_core_flow". Cosmetic only. |

### 3.3 Can Any Skip Be Activated Now?

| Skip | Can activate? | Reason |
|------|--------------|--------|
| Any of the 15 | **No** | 13 depend on Phase 3+ features; 2 are empty stubs whose coverage is already provided by `test_maintenance_core_flow.py` |

---

## 4. Defect Classification

### 4.1 Previously Reported — Now Resolved

| ID | Description | Status |
|----|-------------|--------|
| TD-01 | `MaintenanceRequest` not in `app/models/__init__.py` | ✅ Fixed — model is now correctly exported |
| TD-02 | `/maintenance/create` and transition routes missing | ✅ Fixed — all 5 transition routes are now registered |

### 4.2 Current Defects

None. All collected tests pass (32/32).

---

## 5. Test File Inventory

| # | File | Tests | Status |
|---|------|-------|--------|
| 1 | `test_auth_billing_payments_smoke.py` (box R1) | 1/1 | ✅ |
| 2 | `test_billing_edit_and_contract_list.py` (box R2) | 2/4 | ✅ +2 skip |
| 3 | `test_billing_generate_flow.py` (open) | 1/1 | ✅ |
| 4 | `test_billing_monthly_bill_flow.py` (open) | 1/1 | ✅ |
| 5 | `test_billing_placeholders_and_edges.py` (box R1) | 2/4 | ✅ +2 skip |
| 6 | `test_billing_utility_algorithms.py` (open) | 2/2 | ✅ |
| 7 | `test_billing_year_month_edges.py` (box R2) | 4/6 | ✅ +2 skip |
| 8 | `test_electricity_calculation_and_posting.py` (mimo) | 1/1 | ✅ |
| 9 | `test_electricity_meter_edit_and_post.py` (box R1) | 2/4 | ✅ +2 skip |
| 10 | `test_electricity_water_edge_cases.py` (box R2) | 3/5 | ✅ +2 skip |
| 11 | `test_low_risk_crud_and_filters.py` (open R2) | 2/2 | ✅ |
| 12 | `test_maintenance_core_flow.py` (codex) | 1/1 | ✅ **Newly passing** |
| 13 | `test_maintenance_readiness.py` (box R2) | 2/4 | ✅ +2 skip |
| 14 | `test_payments_reject_and_status.py` (box R1) | 2/4 | ✅ +2 skip |
| 15 | `test_reports_monthly_and_landlord_summary.py` (mimo) | 1/1 | ✅ |
| 16 | `test_utilities_reporting_smoke.py` (open) | 1/1 | ✅ |
| 17 | `test_water_edit_and_independent_post.py` (box R1) | 4/5 | ✅ +1 skip |
| | **Total** | **32/47** | **32 pass, 15 skip** |

---

## 6. Recommendations

1. **All 15 skips should remain as-is.** None are activatable now. The 2 stubs with stale reasons are harmless — they document future test points.
2. **No new tests needed** at this point for Phase 2 exit. The 32 active tests provide adequate smoke/regression coverage across all modules.
3. **Next test push** should be Phase 3, activating the 13 algorithm-dependent skips as the corresponding services are implemented.

---

## 7. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-06-29 | Round 04: full re-verification on `codex-phase2-mainline-01`. 3 previously-failing tests now pass. 0 failures. | box |
