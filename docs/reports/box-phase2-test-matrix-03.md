# Phase 2 Box — Test Matrix Report (Round 03)

Date: 2026-06-29  
Tool: pytest tests/integration -v --tb=line  
Result: **29 passed, 15 skipped, 1 collection-blocked**  

---

## 1. Executive Summary

| Metric | Value |
|--------|-------|
| Test files | 16 |
| Active tests | 29 |
| Skipped (intentional) | 15 |
| Collection errors | 1 (`test_maintenance_core_flow.py`) |
| Blocking other-agent defects | 2 (`__init__.py` missing import; `/maintenance/create` route missing) |
| Pass rate (of collected) | **100%** |

---

## 2. Full Test Matrix

### 2.1 Billing Module

| Test File | Tests | Pass | Skip | Skip reasons | Verdict |
|-----------|-------|------|------|--------------|---------|
| `test_auth_billing_payments_smoke.py` | 1 | 1 | 0 | — | ✅ |
| `test_billing_generate_flow.py` | 1 | 1 | 0 | — | ✅ |
| `test_billing_utility_algorithms.py` | 2 | 2 | 0 | — | ✅ |
| `test_billing_monthly_bill_flow.py` | 1 | 1 | 0 | — | ✅ |
| `test_billing_placeholders_and_edges.py` | 4 | 2 | 2 | Billing recalculation (Phase 3); summary consistency (Phase 3) | ✅ |
| `test_billing_edit_and_contract_list.py` | 4 | 2 | 2 | Edit conflict detection (Phase 3); toggle-paid idempotency (Phase 3) | ✅ |
| `test_billing_year_month_edges.py` | 6 | 4 | 2 | Invalid year_month error handling (Phase 3); cross-year boundary (Phase 3) | ✅ |

### 2.2 Payments Module

| Test File | Tests | Pass | Skip | Skip reasons | Verdict |
|-----------|-------|------|------|--------------|---------|
| `test_payments_reject_and_status.py` | 4 | 2 | 2 | Duplicate TXN handling (needs DB constraint); reconciliation edge cases (Phase 3) | ✅ |

### 2.3 Electricity Module

| Test File | Tests | Pass | Skip | Skip reasons | Verdict |
|-----------|-------|------|------|--------------|---------|
| `test_electricity_calculation_and_posting.py` | 1 | 1 | 0 | — | ✅ |
| `test_electricity_meter_edit_and_post.py` | 4 | 2 | 2 | Status transitions (Phase 3); year_month format consistency (Phase 3) | ✅ |
| `test_electricity_water_edge_cases.py` | 5 | 3 | 2 | Reading amount fallback (Phase 3); single-contract shared water (Phase 3) | ✅ |

### 2.4 Water Module

| Test File | Tests | Pass | Skip | Skip reasons | Verdict |
|-----------|-------|------|------|--------------|---------|
| `test_water_edit_and_independent_post.py` | 5 | 4 | 1 | Multi-contract shared allocation (Phase 3) | ✅ |

### 2.5 Reports Module

| Test File | Tests | Pass | Skip | Skip reasons | Verdict |
|-----------|-------|------|------|--------------|---------|
| `test_reports_monthly_and_landlord_summary.py` | 1 | 1 | 0 | — | ✅ |

### 2.6 Maintenance Module

| Test File | Tests | Pass | Skip | Fail | Notes | Verdict |
|-----------|-------|------|------|------|-------|---------|
| `test_maintenance_core_flow.py` | 1 | 0 | 0 | 1 | ❌ **Collection error**: `MaintenanceRequest` not in `app/models/__init__.py`. Also, POST `/maintenance/create` → 404 (route missing). Model file exists but unregistered; routes not yet added. | 🔴 See incident |
| `test_maintenance_readiness.py` | 4 | 2 | 2 | 0 | Maintenance request create (needs route); status workflow (needs routes). These are correct skips. | ✅ |

### 2.7 Smoke / Cross-Module

| Test File | Tests | Pass | Skip | Skip reasons | Verdict |
|-----------|-------|------|------|--------------|---------|
| `test_utilities_reporting_smoke.py` | 1 | 1 | 0 | — | ✅ |

---

## 3. Skip Analysis — Can Any Be Activated Now?

| Skip reason | Blocked by | Can activate? |
|-------------|-----------|--------------|
| Deeper billing algorithm (recalculate, summary) | `BillingGenerationService` not yet implementing split/aggregation rules | ❌ Phase 3 |
| Duplicate TXN, reconciliation edge cases | `PaymentService` not yet enforcing uniqueness or partial-payment logic | ❌ Phase 3 |
| Electricity status transitions, year_month format | `ElectricityService.calculate_bill()` only flips to "calculated" — no multi-state model | ❌ Phase 3 |
| Electricity reading amount fallback | `ElectricityReading` confirmed_amount fallback logic not yet implemented | ❌ Phase 3 |
| Water multi-contract / single-contract shared allocation | `WaterAllocationService` works with single contract currently | ❌ Phase 3 |
| Billing edit conflict detection | `BillingGenerationService.update_monthly_bill()` conflict check exists but only tested for existing+different ID | ❌ Phase 3+ |
| Billing invalid year_month error handling | Route-level validation not yet implemented | ❌ Phase 3 |
| Cross-year month boundary | Not a current business requirement | ❌ Phase 3 |
| Maintenance create / status workflow | Routes (`/maintenance/create`, `/<id>/transition/...`) not registered | ❌ Blocked by other agent |

**Conclusion: 0 skips can be activated. All 15 are genuine Phase 3 or dependency-blocked placeholders.**

---

## 4. Defect Classification

### 4.1 Trunk Defects (not test issues)

| ID | File | Defect | Severity |
|----|------|--------|----------|
| TD-01 | `app/models/__init__.py` | `MaintenanceRequest` model exists in `app/models/maintenance.py` but is not imported/exported. `test_maintenance_core_flow.py` cannot collect. | 🔴 High — blocks collection of 1 test |
| TD-02 | `app/modules/maintenance/routes.py` | Only `/maintenance/` GET route registered. No `/create`, no `/<id>/transition/...` routes exist. Even if TD-01 is fixed, the test POST → 404. | 🟡 Medium — test expects routes that don't exist |

### 4.2 Stale / Outdated Tests (test itself is out of sync)

| ID | Test | Issue | Severity |
|----|------|-------|----------|
| SO-01 | `test_maintenance_core_flow.py` | Test was written proactively for maintenance core that is only partially landed. References model + routes that don't exist. | 🔴 Test is ahead of trunk — needs the routes to be added before it can pass |

---

## 5. Recommendations

1. **Fix TD-01** — Add `from app.models.maintenance import MaintenanceRequest` and `"MaintenanceRequest"` to `__all__` in `app/models/__init__.py` (1-line fix, non-breaking).
2. **Fix SO-01 / TD-02** — Add `/maintenance/create` POST route and `/<id>/transition/<status>` POST routes to `app/modules/maintenance/routes.py` when maintenance workflow is frozen.
3. **No skip can be activated** — All 15 marked as `@pytest.mark.skip` are correctly placed for Phase 3+ or blocked dependencies.
4. **Run command** — Always use `pytest tests\integration -q --ignore=tests/integration/test_maintenance_core_flow.py` until TD-01 is fixed.

---

## 6. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-06-29 | Initial comprehensive test matrix audit | box |
