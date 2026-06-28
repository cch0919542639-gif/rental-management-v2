# Phase 1 Review 02 — Compliance Check Against Frozen Contracts

Date: 2026-06-28  
Author: reasonix  
Review Scope: Phase 1 implementation vs. Phase 0 frozen data contracts  
Branch: `agent/reasonix-review-02`  
Baseline: `main` (latest from origin)

---

## Summary

| Module | Status | Risk Level | Key Findings |
|--------|--------|-----------|--------------|
| `payments` | ✅ Compliant | LOW | PaymentRecord state machine fully implemented; dead Payment class removed |
| `electricity` | ✅ Compliant | LOW | No hard-coded meter_id; year_month uses String(6) + helper |
| `water` | ✅ Compliant | LOW | Shared/independent allocation clean; no old reverse-imports |
| `reports` | ✅ Compliant | LOW | No virtual tenant keyword matching; proper Room.status usage |
| `maintenance` | ✅ Boundary OK | LOW | Read-only snapshot; no formal schema; no status contamination |

**Overall: No frozen-contract violations found.** All 5 target areas comply with Phase 0 decisions.

---

## 1. Payments — Full Compliance

### Contract Checkpoints
- `PaymentRecord` is the **sole payment entity** ✅
- `record_status` state machine: `pending → verified → linked`, `pending → rejected` ✅
- No `Payment` class references anywhere in new code ✅
- Reconciliation marks `monthly_bill.paid = True` when amount ≥ total ✅

### Implementation Detail
| Layer | File | Status |
|-------|------|--------|
| Model | `app/models/billing.py` — `PaymentRecord` | ✅ Schema matches contract |
| Service | `app/services/payment_service.py` — `PaymentService` | ✅ State transitions enforced |
| Service | `app/services/payment_reconciliation_service.py` | ✅ Clean threshold check |
| Repository | `app/repositories/payment_repository.py` | ✅ Uses PaymentRecord only |
| Routes | `app/modules/payments/routes.py` | ✅ CRUD + verify/reject/link |
| Forms | `app/modules/payments/forms.py` | ✅ Covers all PaymentRecord fields |

### Observations
- `contract.payments` backref (on Contract model) is named appropriately — no conflict with old `Payment` class.
- `transaction_id` uniqueness enforced at service layer.

---

## 2. Electricity — Full Compliance

### Contract Checkpoints
- No hard-coded `meter_id=1` ✅
- `ElectricityBill.year_month` = `String(6)`, uses `to_db_year_month()` ✅
- Route delegates computation to service layer ✅

### Implementation Detail
| Layer | File | Status |
|-------|------|--------|
| Model | `app/models/electricity.py` | ✅ `year_month` = String(6); clean schema |
| Service | `app/services/electricity_service.py` | ✅ Creates bills, readings, posts to monthly bill |
| Routes | `app/modules/electricity/routes.py` | ✅ Meter/bill/reading CRUD + calculate + post |
| Repository | `app/repositories/electricity_repository.py` | ✅ |

### Observations
- `ElectricityService.post_to_monthly_bill()` writes directly to `monthly_bill.*` fields — this is service→model within acceptable bounds (no repository involved for field mutation).
- Meter creation supports optional room binding; no assumption of single-meter-per-property.

---

## 3. Water — Full Compliance

### Contract Checkpoints
- Shared / independent allocation modes supported ✅
- No old `water_bill.py` reverse import pattern ✅

### Implementation Detail
| Layer | File | Status |
|-------|------|--------|
| Model | `app/models/billing.py` — `WaterBill` | ✅ |
| Service | `app/services/water_service.py` | ✅ Creates/edits water bills, posts to monthly bill |
| Allocation | `app/services/water_allocation_service.py` | ✅ Shared-by-stay-days + independent meter |
| Routes | `app/modules/water/routes.py` | ✅ CRUD + post (shared/independent) |
| Repository | `app/repositories/water_repository.py` | ✅ |

### Observations
- `WaterAllocationService.overlap_days()` correctly handles non-overlapping contracts (returns 0).
- Division-by-zero guarded: `total_days <= 0` raises `DomainValidationError`.

---

## 4. Reports — Full Compliance (Critical Fix Confirmed)

### Contract Checkpoints
- **No virtual tenant name keyword matching** (`待補`/`待修`/`空房`/`倉庫`/`鐵皮`) ✅
- Uses `Room.status` + `Contract.status` for occupancy state ✅
- `year_month` conversion via centralized helpers ✅

### Implementation Detail
| Layer | File | Status |
|-------|------|--------|
| Service | `app/services/report_service.py` | ✅ Uses `to_db_year_month` / `to_ui_year_month` |
| Repository | `app/repositories/report_repository.py` | ✅ Clean SQL joins through Contract→Room→Property→Landlord |
| Routes | `app/modules/reports/routes.py` | ✅ Monthly / landlord-summary / yearly |

### Critical Fix Verified
The old system's `report_monthly()` determined vacancy by checking if `tenant.name` contained keywords like `"空房"`, `"待修"`, etc. The new system **completely removes this pattern**:
- Monthly report joins `MonthlyBill → Contract → Room → Property → Landlord + Tenant`
- No `tenant.name` filtering logic exists
- Occupancy is derived from `Room.status` and `Contract.status`, not from tenant name

---

## 5. Maintenance — Boundary Correct (Schema Not Frozen)

### Contract Checkpoints
- No formal maintenance schema introduced ✅
- Does not modify `Room.status` or `tenant.name` ✅
- Module entry + boundary page only ✅

### Implementation Detail
| Layer | File | Status |
|-------|------|--------|
| Routes | `app/modules/maintenance/routes.py` | ✅ Single GET `/` endpoint |
| Service | `app/services/maintenance_service.py` | ✅ Read-only `room_snapshot()` |

### Observations
- No `maintenance` model/schema defined — matches Phase 1 scope ("尚未凍結").
- `room_snapshot()` returns existing `Room` data only; no writes.
- Safe foundation for Phase 2 when formal schema is designed.

---

## Cross-Cutting Compliance Checks

### `year_month` Format Centralization
| Check | Result |
|-------|--------|
| `MonthlyBill.year_month` = `String(6)` (was String(7) in old system) | ✅ Fixed |
| `ElectricityBill.year_month` = `String(6)` (was String(7) in old system) | ✅ Fixed |
| All conversions use `core/year_month.py` helpers | ✅ |
| No `replace('-', '')` scattered in routes/services | ✅ |
| `year_month.py` provides `to_db`, `to_ui`, `validate_db`, `validate_ui` | ✅ |

### Dependency Boundary Compliance
| Rule | Status |
|------|--------|
| Module → Repository → Model | ✅ |
| Module → Service → Repository → Model | ✅ |
| Module A → Module B (forbidden) | ✅ No cross-module imports |
| No `from app import` reverse coupling | ✅ New structure is self-contained |

### Room.status / Contract.status / Tenant.name
| Check | Result |
|-------|--------|
| `Room.status` = `vacant`/`occupied` only | ✅ |
| `Contract.status` = `active`/`expired`/`terminated` | ✅ |
| No virtual tenant names in tenants table | ✅ (new code doesn't create them) |
| `ContractService.terminate_contract()` sets room to `vacant` | ✅ |
| `ContractService.create_contract()` sets room to `occupied` | ✅ |

---

## Risk Register

| ID | Module | Risk | Severity | Recommendation |
|----|--------|------|----------|---------------|
| R01 | electricity | `ElectricityService.create_bill()` accepts `meter_id` from form without validating it belongs to the specified property | LOW | Add `ElectricityMeterRepository.verify_meter_belongs_to_property(meter_id, property_id)` |
| R02 | water | `WaterService.post_shared_to_monthly_bill()` uses `water_bill.property_id` to find active contracts — no cross-property guard | LOW | Add validation that `monthly_bill.contract.room.property_id == water_bill.property_id` |
| R03 | reports | `ReportRepository.monthly_report_rows()` does an INNER JOIN on Tenant — bills without a valid tenant_id will be silently excluded | LOW | Consider LEFT JOIN or add seed data validation |
| R04 | payments | `PaymentService.create_payment_record()` accepts `OCR` fields but no OCR integration module exists yet | LOW | Expected — Phase 2 scope |
| R05 | maintenance | No formal schema or state machine defined; entering Phase 2 without a design ADR could cause rework | INFO | Schedule maintenance ADR before Phase 2 |

---

## Decision Log

| Decision | Rationale |
|----------|-----------|
| No code changes needed in main trunk | All 5 modules comply with frozen contracts; no small fixes required |
| Maintenance schema remains unfrozen | Per Phase 1 scope; Phase 2 will design formal schema |
| Reports pass without modification | The critical virtual-tenant-name pattern has been eliminated |

---

## Deliverables

- ✅ `docs/reports/reasonix-phase1-review-02.md` (this file)
- ✅ `coordination/progress/reasonix.md` (updated)
- ⬜ `coordination/completed/reasonix.md` (updated — pending handoff)

---

## Next Steps for Reasonix

1. ~Hand off to `codex` for awareness of review results~
2. ~Hand off to `open` for route-matrix alignment~
3. ~Schedule maintenance ADR before Phase 2~
