# Phase 4 — Skipped Tests Review Guard Note

Date: 2026-07-01
Author: reasonix
Branch: `agent/box-phase4-runbook-tests-01`
Baseline: `box-phase4-runbook-tests-01` (66 passed, 15 skipped)
Predecessor: `docs/reports/reasonix-phase4-readiness-01.md`

---

## Executive Summary

Baseline pytest shows **66 passed, 15 skipped, 0 failures**. This note reviews all 15 skipped tests against frozen contracts (status machines, year_month rules, utility algorithm boundaries) and classifies them for Phase 4 action.

| Classification | Count | Action |
|---------------|-------|--------|
| ✅ **Direct — no frozen boundary risk** | 4 | Can be un-skipped and filled immediately |
| ⚠️ **Caution — touches a frozen boundary** | 4 | Can be filled, but must stay within contract |
| ❌ **Covered elsewhere** | 2 | Already tested by `test_maintenance_core_flow`; keep skip or delete stub |
| ⏳ **Deferred — not Phase 4 scope** | 5 | Requires post-Phase 4 algorithm or reconciliation stability |
| **Total** | **15** | |

**Verdict: 8 tests can be filled in Phase 4 (4 direct + 4 with caution). 7 should remain skipped or be dropped.**

---

## 1. Frozen Contracts Reference (Boundaries to Protect)

From `data_contracts/status-machines.md` and Phase 0 ADR:

| Contract | Allowed Values | Guard Rule |
|----------|---------------|------------|
| `Room.status` | `vacant`, `occupied` | No `待修` in status field |
| `Contract.status` | `active`, `expired`, `terminated` | No other values |
| `PaymentRecord.record_status` | `pending`, `verified`, `rejected`, `linked` | Closed state machine |
| `ElectricityBill.status` | `pending`, `calculated` | Closed state machine; no `confirmed` yet |
| `MonthlyBill.paid` | `false`, `true` | Boolean only |
| `year_month` (DB) | `YYYYMM` | Stored as 6-digit string |
| `year_month` (UI) | `YYYY-MM` | Accepted on input, converted by `app/core/year_month.py` |
| Utility algorithms | Electricity calc, water allocation | No changes to formula in test — test must verify existing behavior |

---

## 2. ✅ Direct Items (4 tests — no frozen boundary risk)

These tests can be filled immediately in Phase 4. They touch UI flow logic, date arithmetic, or existing contract rules without crossing any frozen boundary.

### 2.1 `test_billing_edit_conflict` (test_billing_edit_and_contract_list.py:63)

| Field | Value |
|-------|-------|
| Skip reason | "Placeholder: billing edit with conflict detection (TBD)" |
| What it would test | Simultaneous edit detection (optimistic locking or conflict UI) |
| Frozen boundary | None — conflict detection is UI/logic, not a contract |
| **Verdict** | ✅ **Direct** — fill in Phase 4 |
| Implementation hint | Test that editing a bill that was already modified by another session shows appropriate feedback. Relies on existing edit route, no schema change needed. |

### 2.2 `test_billing_toggle_paid_idempotency` (test_billing_edit_and_contract_list.py:68)

| Field | Value |
|-------|-------|
| Skip reason | "Placeholder: toggle-paid idempotency (TBD)" |
| What it would test | Toggling `paid` multiple times produces same result |
| Frozen boundary | `MonthlyBill.paid` is boolean → boolean. Toggle is idempotent by nature. No status machine risk. |
| **Verdict** | ✅ **Direct** — fill in Phase 4 |
| Implementation hint | POST `/billing/<id>/toggle-paid` twice, verify 200 both times and `paid` is `true` then `false`. |

### 2.3 `test_billing_year_month_boundary` (test_billing_year_month_edges.py:77)

| Field | Value |
|-------|-------|
| Skip reason | "Placeholder: cross-year month boundary (TBD)" |
| What it would test | Billing list with `year_month=202612` → expects `202701` in next page, etc. |
| Frozen boundary | No — this tests date arithmetic/ordering, not the format contract. The format is `YYYYMM`; boundary testing is about sequential ordering. |
| **Verdict** | ✅ **Direct** — fill in Phase 4 |
| Implementation hint | Use `to_db_year_month()` / `to_ui_year_month()` helpers for all conversions. Do not call `replace('-', '')` in test. |

### 2.4 `test_payment_duplicate_transaction_id` (test_payments_reject_and_status.py:77)

| Field | Value |
|-------|-------|
| Skip reason | "Placeholder: test for duplicate transaction_id rejection" |
| What it would test | Creating two payments with same `transaction_id` → error |
| Frozen boundary | `payments-contract.md` states `transaction_id` must be **UNIQUE if present**. This test directly implements that contract. |
| **Verdict** | ✅ **Direct** — fill in Phase 4 |
| Implementation hint | Create Payment A with `transaction_id="TXN001"`, then create Payment B with same `transaction_id`. Expect 400 or 422. Verify DB has only one row with that ID. |

---

## 3. ⚠️ Caution Items (4 tests — touches frozen boundary, fill with care)

These tests CAN be filled in Phase 4, but must stay strictly within the frozen contract. Test assertions must reference the contract values, not hardcode guesses.

### 3.1 `test_billing_list_invalid_year_month` (test_billing_year_month_edges.py:72)

| Field | Value |
|-------|-------|
| Skip reason | "Placeholder: billing list with invalid year_month (TBD)" |
| What it would test | Passing garbage like `"abc"` or `"13"` as `year_month` → 400 or fallback |
| Frozen boundary | ⚠️ **year_month format contract** — test must use `app/core/year_month.py` helpers for validation, NOT reimplement format logic |
| **Verdict** | ⚠️ **Caution** — OK to fill, but must call existing helpers |
| Guard rule | Test must import `validate_db_year_month()` / `validate_ui_year_month()` and assert those return False for invalid inputs. Do NOT write a parallel validation regex in the test. |

### 3.2 `test_electricity_bill_status_transitions` (test_electricity_meter_edit_and_post.py:169)

| Field | Value |
|-------|-------|
| Skip reason | "Placeholder: verify electricity bill status transitions" |
| What it would test | `pending → calculated → posted` transitions |
| Frozen boundary | ⚠️ **ElectricityBill.status machine** — allowed: `pending`, `calculated`. No `confirmed` yet. `posted` is an action (posting to MonthlyBill), not a status value. |
| **Verdict** | ⚠️ **Caution** — OK to fill, but must not introduce new status values |
| Guard rule | Assert `status=="calculated"` after calculation. Assert `status=="pending"` before. Do NOT assert `"posted"` as a status. The transition to `MonthlyBill.electricity_amount` is a side effect, not a status change. |

### 3.3 `test_electricity_year_month_format` (test_electricity_meter_edit_and_post.py:177)

| Field | Value |
|-------|-------|
| Skip reason | "Placeholder: electricity bill year_month format consistency" |
| What it would test | Bill created with `"2026-06"` (UI) → stored as `"202606"` (DB) |
| Frozen boundary | ⚠️ **year_month format contract** — must test through the helper |
| **Verdict** | ⚠️ **Caution** — OK to fill, but must go through existing year_month converter |
| Guard rule | Create bill via POST with `year_month="2026-06"`, then query DB directly to verify value is `"202606"`. Do NOT assert a regex on the incoming format. |

### 3.4 `test_electricity_reading_no_amount` (test_electricity_water_edge_cases.py:115)

| Field | Value |
|-------|-------|
| Skip reason | "Placeholder: electricity reading amount fallback logic (TBD)" |
| What it would test | Reading without `calculated_amount` — fallback or zero |
| Frozen boundary | ⚠️ **Utility algorithm boundary** — electricity calculation logic is frozen |
| **Verdict** | ⚠️ **Caution** — OK to fill, but must only test existing service behavior |
| Guard rule | Use `ElectricityService` or the route to create a reading with `calculated_amount=None`. Assert the response or DB value matches the current service implementation. Do NOT change the algorithm — if the fallback is zero, assert zero. If the fallback recomputes, assert the recomputed value. |

---

## 4. ❌ Covered Elsewhere (2 tests — keep skip or delete stub)

These stubs are empty and their coverage is already provided by other active tests.

### 4.1 `test_maintenance_request_create` (test_maintenance_readi

### 4.2 `test_maintenance_status_workflow` (test_maintenance_readiness.py:47)

| Field | Value |
|-------|-------|
| Skip reason | "Placeholder: maintenance status workflow (TBD — routes not yet added)" |
| Actual state | Routes exist, `MaintenanceService.transition_status()` exists with 5-state machine |
| Coverage | ✅ **Covered by** `test_maintenance_core_flow.test_maintenance_create_and_transition_flow` (transitions through `reported → assigned → in_progress → resolved → closed`) |
| **Verdict** | ❌ **Covered** — keep skip with updated reason, or delete empty stub. The skip reason is stale. |

---

## 5. ⏳ Deferred Items (5 tests — not Phase 4 scope)

These tests depend on features or algorithm stability that is not yet guaranteed in Phase 4.

### 5.1 `test_billing_recalculate` (test_billing_placeholders_and_edges.py:36)

| Field | Value |
|-------|-------|
| Skip reason | "deeper billing recalculation — Phase 3" |
| Why deferred | Recalculation touches utility amounts (electricity + water) that depend on algorithm stability. Phase 4 should not change utility algorithms. Defer to Phase 5 when reconciliation is solid. |
| **Verdict** | ⏳ **Defer** — keep skip, re-evaluate in Phase 5 |

### 5.2 `test_billing_summary_consistency` (test_billing_placeholders_and_edges.py:44)

| Field | Value |
|-------|-------|
| Skip reason | "billing summarisation / aggregation — month_collected / month_unpaid totals" |
| Why deferred | `month_collected` vs `month_unpaid` requires payment reconciliation service stability. Reconciliation involves `PaymentRecord.record_status` transitions (`verified → linked`) and is not yet frozen. |
| **Verdict** | ⏳ **Defer** — keep skip, re-evaluate in Phase 5 |

### 5.3 `test_water_shared_single_contract` (test_electricity_water_edge_cases.py:120)

| Field | Value |
|-------|-------|
| Skip reason | "single-contract shared water allocation (TBD)" |
| Why deferred | Water allocation algorithm is not yet stable enough for regression test hardening. The existing `test_billing_utility_algorithms` covers basic allocation, but deeper edge cases belong post-Phase 4. |
| **Verdict** | ⏳ **Defer** — keep skip, re-evaluate in Phase 5 |

### 5.4 `test_water_shared_multi_contract` (test_water_edit_and_independent_post.py:143)

| Field | Value |
|-------|-------|
| Skip reason | "shared_by_stay_days water allocation with multiple active contracts" |
| Why deferred | Same reasoning as 5.3 — multi-contract allocation is a utility algorithm edge case. Defer until water allocation algorithm is frozen for production. |
| **Verdict** | ⏳ **Defer** — keep skip, re-evaluate in Phase 5 |

### 5.5 `test_payment_reconciliation_edge_cases` (test_payments_reject_and_status.py:86)

| Field | Value |
|-------|-------|
| Skip reason | "payment reconciliation edge cases — partial payments, overpayments, multi-record" |
| Why deferred | Payment reconciliation is a Phase 5 feature. The current `PaymentRecord` status machine only defines `pending → verified → linked` but the reconciliation service (matching payments to bills, handling overpayments) is not yet built. |
| **Verdict** | ⏳ **Defer** — keep skip, re-evaluate in Phase 5 |

---

## 6. Quick-Reference Table

| # | Test | File | Phase 4? | Classification | Reason |
|---|------|------|----------|---------------|--------|
| 1 | `test_billing_edit_conflict` | `test_billing_edit_and_contract_list.py` | ✅ Yes | ✅ Direct | Conflict detection, no frozen boundary |
| 2 | `test_billing_toggle_paid_idempotency` | same file | ✅ Yes | ✅ Direct | Boolean toggle, idempotent by design |
| 3 | `test_billing_recalculate` | `test_billing_placeholders_and_edges.py` | ❌ No | ⏳ Defer | Depends on utility algorithm stability |
| 4 | `test_billing_summary_consistency` | same file | ❌ No | ⏳ Defer | Depends on payment reconciliation |
| 5 | `test_billing_list_invalid_year_month` | `test_billing_year_month_edges.py` | ✅ Yes | ⚠️ Caution | Must use `year_month` helper |
| 6 | `test_billing_year_month_boundary` | same file | ✅ Yes | ✅ Direct | Date arithmetic, not format contract |
| 7 | `test_electricity_bill_status_transitions` | `test_electricity_meter_edit_and_post.py` | ✅ Yes | ⚠️ Caution | Must not introduce new status values |
| 8 | `test_electricity_year_month_format` | same file | ✅ Yes | ⚠️ Caution | Must use `year_month` helper |
| 9 | `test_electricity_reading_no_amount` | `test_electricity_water_edge_cases.py` | ✅ Yes | ⚠️ Caution | Must test existing service, not change algorithm |
| 10 | `test_water_shared_single_contract` | same file | ❌ No | ⏳ Defer | Water algorithm not yet frozen |
| 11 | `test_maintenance_request_create` | `test_maintenance_readiness.py` | ❌ No | ❌ Covered | Covered by `test_maintenance_core_flow` |
| 12 | `test_maintenance_status_workflow` | same file | ❌ No | ❌ Covered | Covered by `test_maintenance_core_flow` |
| 13 | `test_payment_duplicate_transaction_id` | `test_payments_reject_and_status.py` | ✅ Yes | ✅ Direct | Implements UNIQUE contract rule |
| 14 | `test_payment_reconciliation_edge_cases` | same file | ❌ No | ⏳ Defer | Reconciliation is Phase 5 scope |
| 15 | `test_water_shared_multi_contract` | `test_water_edit_and_independent_post.py` | ❌ No | ⏳ Defer | Multi-contract allocation deferred |

---

## 7. Guard Rules Summary

### Do (for Phase 4 test fillers)

1. ✅ Import `app/core/year_month.py` helpers — call `validate_db_year_month()`, `to_db_year_month()`, etc. Never regex or `replace('-', '')` in test.
2. ✅ Assert `ElectricityBill.status` against frozen set `{"pending", "calculated"}` only.
3. ✅ Assert `PaymentRecord.record_status` against frozen set `{"pending", "verified", "rejected", "linked"}` only.
4. ✅ Use `seeded_data` fixtures for test data — do not create raw models in test body unless unavoidable.
5. ✅ Verify DB state after POST operations with `app.app_context()` query.

### Do NOT (Phase 4)

6. ❌ Do not change utility calculation formulas (electricity rate, water allocation) in test assertions — assert the current behavior.
7. ❌ Do not assert "posted" as an ElectricityBill status value — `posted` is a side effect (MonthlyBill update), not a status.
8. ❌ Do not reimplement year_month validation — always delegate to `app/core/year_month.py`.
9. ❌ Do not test payment reconciliation (partial payments, overpayments) — that's Phase 5 scope.
10. ❌ Do not add new status values to any status machine — even if the skip reason suggests it.

---

## 8. Recommended Action Order

```
Phase 4 fill order (by risk):
1. test_payment_duplicate_transaction_id     ✅ Direct — quick win, enforces contract
2. test_billing_toggle_paid_idempotency      ✅ Direct — simple idempotency
3. test_billing_edit_conflict                ✅ Direct — conflict detection UI
4. test_billing_year_month_boundary          ✅ Direct — date arithmetic
5. test_electricity_year_month_format        ⚠️ Caution — use helpers, safe
6. test_billing_list_invalid_year_month      ⚠️ Caution — use helpers, safe
7. test_electricity_bill_status_transitions  ⚠️ Caution — status machine guard
8. test_electricity_reading_no_amount        ⚠️ Caution — algorithm boundary guard
```

---

## Appendices

### A. Current Test Summary

```
pytest tests/integration -q
→ 66 passed, 15 skipped, 0 failures
```

After filling 8 Phase 4 candidates:
```
→ Expected: 74 passed, 7 skipped, 0 failures
```

### B. Frozen Contract Files

- `data_contracts/status-machines.md` — all status machines
- `app/core/year_month.py` — year_month format helpers
- `docs/reports/reasonix-architecture-decision.md` — Phase 0 ADR

### C. Related Guard Notes

- `docs/reports/reasonix-phase4-readiness-01.md` — Phase 4 pre-launch guard (B1-B4 blockers)
- `docs/reports/reasonix-phase4-db-migration-guard-01.md` — DB migration policy (Phase 4 companion)

---

*End of Phase 4 Skipped Tests Guard Note*
