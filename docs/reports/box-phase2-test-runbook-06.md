# Phase 2 Box — Test Matrix & Runbook Report (Round 06)

Date: 2026-06-29  
Branch: `codex-phase2-mainline-01`  
Tool: `pytest tests/integration -v --tb=line`  
Result: **38 passed, 15 skipped, 0 failures** (53 collected)

---

## 1. Executive Summary

| Metric | Round 05 | Round 06 | Change |
|--------|----------|----------|--------|
| Test files | 19 | **22** | +3 |
| Collected items | 49 | **53** | +4 |
| Pass | 34 | **38** | +4 |
| Skip | 15 | 15 | — |
| Fail | 0 | 0 | — |

**New test files added by Codex (electricity property workflows + nested creation):**

| File | Tests | Coverage |
|------|-------|----------|
| `test_electricity_property_detail.py` | 1 | Property detail page (summary, meter count, recent bills) |
| `test_electricity_property_workflows.py` | 1 | Full flow: new-bill → quick-reading → reading-log |
| `test_nested_creation_routes.py` | 2 | Nested landlord→property create; property→room create |

All 4 new tests **pass**. No prior tests regressed.

---

## 2. Full Test Matrix (22 Files)

### 2.1 Billing Module (7 files, 13 active, 8 skip)

| Test File | Total | Pass | Skip | Author |
|-----------|-------|------|------|--------|
| `test_auth_billing_payments_smoke.py` | 1 | 1 | 0 | box R1 |
| `test_billing_edit_and_contract_list.py` | 4 | 2 | 2 | box R2 |
| `test_billing_generate_flow.py` | 1 | 1 | 0 | open |
| `test_billing_monthly_bill_flow.py` | 1 | 1 | 0 | open |
| `test_billing_placeholders_and_edges.py` | 4 | 2 | 2 | box R1 |
| `test_billing_utility_algorithms.py` | 2 | 2 | 0 | open |
| `test_billing_year_month_edges.py` | 6 | 4 | 2 | box R2 |

### 2.2 Payments Module (1 file, 2 active, 2 skip)

| Test File | Total | Pass | Skip | Author |
|-----------|-------|------|------|--------|
| `test_payments_reject_and_status.py` | 4 | 2 | 2 | box R1 |

### 2.3 Electricity Module (5 files, 7 active, 4 skip)

| Test File | Total | Pass | Skip | Author |
|-----------|-------|------|------|--------|
| `test_electricity_calculation_and_posting.py` | 1 | 1 | 0 | mimo |
| `test_electricity_meter_edit_and_post.py` | 4 | 2 | 2 | box R1 |
| `test_electricity_property_detail.py` | 1 | 1 | 0 | **codex (new)** |
| `test_electricity_property_workflows.py` | 1 | 1 | 0 | **codex (new)** |
| `test_electricity_water_edge_cases.py` | 5 | 3 | 2 | box R2 |

### 2.4 Water Module (1 file, 4 active, 1 skip)

| Test File | Total | Pass | Skip | Author |
|-----------|-------|------|------|--------|
| `test_water_edit_and_independent_post.py` | 5 | 4 | 1 | box R1 |

### 2.5 Reports Module (2 files, 2 active, 0 skip)

| Test File | Total | Pass | Skip | Author |
|-----------|-------|------|------|--------|
| `test_reports_maintenance_summary.py` | 1 | 1 | 0 | codex |
| `test_reports_monthly_and_landlord_summary.py` | 1 | 1 | 0 | mimo |

### 2.6 Maintenance Module (3 files, 4 active, 2 skip)

| Test File | Total | Pass | Skip | Author |
|-----------|-------|------|------|--------|
| `test_maintenance_core_flow.py` | 1 | 1 | 0 | codex |
| `test_maintenance_filters_and_summary.py` | 1 | 1 | 0 | codex |
| `test_maintenance_readiness.py` | 4 | 2 | 2 | box R2 |

### 2.7 Nested Creation (1 file, 2 active, 0 skip)

| Test File | Total | Pass | Skip | Author |
|-----------|-------|------|------|--------|
| `test_nested_creation_routes.py` | 2 | 2 | 0 | **codex (new)** |

### 2.8 Smoke / Cross-Module (2 files, 3 active, 0 skip)

| Test File | Total | Pass | Skip | Author |
|-----------|-------|------|------|--------|
| `test_low_risk_crud_and_filters.py` | 2 | 2 | 0 | open R2 |
| `test_utilities_reporting_smoke.py` | 1 | 1 | 0 | open |

### Summary

| Section | Files | Active | Skip |
|---------|-------|--------|------|
| Billing | 7 | 13 | 8 |
| Payments | 1 | 2 | 2 |
| Electricity | 5 | 7 | 4 |
| Water | 1 | 4 | 1 |
| Reports | 2 | 2 | 0 |
| Maintenance | 3 | 4 | 2 |
| Nested Creation | 1 | 2 | 0 |
| Smoke/Cross | 2 | 3 | 0 |
| **Total** | **22** | **38** | **15** |

---

## 3. Skip Classification — Unchanged (15)

All 15 skips remain correctly deferred. **No change from Round 05.**

- 13 Phase 3+ deferred (algorithm-dependent)
- 2 empty stubs (covered by `test_maintenance_core_flow.py`)

---

## 4. Coverage: Electricity Property Workflows

Codex added the following routes — all covered by new tests:

| Route | Test | Verified |
|-------|------|----------|
| `GET /electricity/property/<id>` | `test_electricity_property_detail.py` | ✅ Renders "電力總覽", "電表數", "最近電費單" |
| `POST /electricity/property/<id>/new-bill` | `test_electricity_property_workflows.py` | ✅ Creates bill, shows "物件電費單已建立" |
| `POST /electricity/property/<id>/quick-reading` | `test_electricity_property_workflows.py` | ✅ Creates reading, shows "物件抄表資料已建立" |
| `GET /electricity/property/<id>/reading-log` | `test_electricity_property_workflows.py` | ✅ Renders "抄表歷史" with reading data |

**Coverage assessment:** Adequate. The new-bill → quick-reading → reading-log workflow is covered end-to-end.

---

## 5. Manual Verification Steps

These steps let a human operator verify the new electricity property pages via browser:

### 5.1 Electricity Property Detail

```powershell
# Start server
py -3 -m flask --app app.wsgi run --debug
```

1. Log in at `http://127.0.0.1:5000/auth/login` (admin / admin123)
2. Navigate to `http://127.0.0.1:5000/electricity/property/1`
3. Verify page shows:
   - "電力總覽" header
   - Property name ("North House")
   - "電表數" count
   - "最近電費單" section with at least one bill

### 5.2 New Bill (Property-Scoped)

1. Navigate to `http://127.0.0.1:5000/electricity/property/1`
2. Click "新增電費單" or POST to `/electricity/property/1/new-bill`
3. Fill in: year_month, period dates, meter, readings, amounts
4. Submit → should redirect back to property detail with success flash

### 5.3 Quick Reading

1. From property detail, click "新增抄表" on an existing bill
2. Or POST to `/electricity/property/1/quick-reading` with bill_id, meter_id, room_id, readings
3. Submit → should show "物件抄表資料已建立"

### 5.4 Reading Log

1. Navigate to `http://127.0.0.1:5000/electricity/property/1/reading-log`
2. Verify page shows:
   - "抄表歷史" header
   - Recent readings with meter, room, readings, amounts

### 5.5 Nested Creation

1. `http://127.0.0.1:5000/properties/landlord/1/create` — Create property under landlord
2. `http://127.0.0.1:5000/rooms/property/1/create` — Create room under property

---

## 6. Runbook Updates Needed

| File | Action |
|------|--------|
| `docs/operations/dev-runbook.md` | ⚠️ Needs update — test table still at Round 05 (19 files). Should be 22 files. |
| `tests/README.md` | ⚠️ Needs update — test table still at Round 05 (19 files). Should be 22 files. |
| `scripts/README.md` | ✅ No change needed |

---

## 7. Recommendations

1. **All 15 skips remain as-is.** No change from Round 05.
2. **22 test files, 38 active tests** is the current baseline.
3. **`test_electricity_property_workflows.py`** provides adequate coverage for the new-bill → quick-reading → reading-log flow. No additional tests needed.
4. **`test_nested_creation_routes.py`** provides adequate coverage for nested property/room creation.
5. **Run command**: `pytest tests/integration -q` (53 collected, 38 pass, 15 skip).

---

## 8. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-06-29 | Round 06: tracked Codex's 3 new test files. Updated matrix to 22 files, 38 passed. Added manual verification steps for electricity property workflows. | box |
