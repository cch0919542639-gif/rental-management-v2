# Phase 2 UI Regression 04

Author: mimo
Round: `agent/mimo-ui-regression-04`
Status: completed
Date: 2026-06-29
Base: `codex-phase2-mainline-01`

## Scope

- Focused UI regression on latest mainline branch
- electricity / water / payments / reports / billing / maintenance
- Verify all previous blockers are resolved

## Regression Results

### Pages Checked

| Page | Route | Status | Notes |
|------|-------|--------|-------|
| Electricity Index | /electricity/ | ✅ Normal | property.name with fallback |
| Electricity Bill Detail | /electricity/bills/<id> | ✅ Normal | Chinese headers |
| Water List | /water/ | ✅ Normal | property.name displayed |
| Payments List | /payments/ | ✅ Normal | bank/account/transaction columns |
| Reports Monthly | /reports/monthly | ✅ Normal | public_electricity + other_desc |
| Billing List | /billing/ | ✅ Normal | public_electricity + other_charges |
| Maintenance Index | /maintenance/ | ✅ Normal | Full CRUD + status transitions |
| Maintenance Create | /maintenance/create | ✅ Normal | Form with all fields |
| Maintenance Edit | /maintenance/<id>/edit | ✅ Normal | Form with all fields |
| Maintenance Transition | /maintenance/<id>/transition/<status> | ✅ Normal | Status machine working |

### Templates Verified

| Template | Fields | Status |
|----------|--------|--------|
| `electricity/index.html` | property.name with fallback | ✅ |
| `electricity/bill_detail.html` | 用電量/計算金額/確認金額 | ✅ |
| `water/list.html` | property.name | ✅ |
| `payments/list.html` | bank_name/account_number/transaction_id | ✅ |
| `reports/monthly.html` | public_electricity/other_desc | ✅ |
| `billing/list.html` | public_electricity/other_charges | ✅ |
| `maintenance/index.html` | Full CRUD + status transitions | ✅ |
| `maintenance/form.html` | All maintenance-contract fields | ✅ |

### Backend Verified

| Component | Status | Notes |
|-----------|--------|-------|
| ElectricityMeter.property relationship | ✅ | model has property = db.relationship |
| ElectricityBill.property relationship | ✅ | model has property = db.relationship |
| report_service.monthly_report() | ✅ | Returns public_electricity, other_desc |
| report_repository.monthly_report_rows() | ✅ | Queries public_electricity, other_desc |
| MaintenanceService | ✅ | create, update, transition_status |
| MaintenanceRepository | ✅ | list_all, get_or_404 |
| Maintenance forms | ✅ | All contract fields |

### Navigation Consistency

- [x] Header nav links all functional (13 modules)
- [x] All template titles consistent
- [x] Flash messages use `success`/`error` categories
- [x] No dead routes detected
- [x] All CRUD operations have create/edit buttons

### Field Alignment with Contracts

- [x] `ElectricityMeter.property.name` — ✅ displayed with fallback
- [x] `ElectricityBill.property.name` — ✅ displayed with fallback
- [x] `ElectricityReading.usage/calculated_amount/confirmed_amount` — ✅ Chinese headers
- [x] `WaterBill.property.name` — ✅ displayed
- [x] `PaymentRecord.bank_name/account_number/transaction_id` — ✅ displayed
- [x] `MonthlyBill.public_electricity` — ✅ displayed
- [x] `MonthlyBill.other_desc` — ✅ displayed
- [x] `MonthlyBill.other_charges` — ✅ displayed
- [x] `MaintenanceRequest` all fields — ✅ displayed and editable
- [x] `MaintenanceRequest` status machine — ✅ transitions working

## Previous Blockers — All Resolved

| Blocker | Status | Resolution |
|---------|--------|------------|
| report_service.py missing public_electricity/other_desc | ✅ Resolved | Already in return dict |
| ElectricityMeter/ElectricityBill missing property relationship | ✅ Resolved | Both models have property relationship |
| Maintenance module missing CRUD routes | ✅ Resolved | Full CRUD + status transitions |

## Minor Observations (Non-blocking)

### 1. electricity/index.html — room_id displayed as number

**Observation:** `{{ meter.room_id or '-' }}` and `{{ reading.room_id or '-' }}` display numeric IDs.

**Impact:** Low — room_id is acceptable for internal reference.

**Recommendation:** Could display `room.room_number` instead, but not required for contract alignment.

### 2. maintenance/index.html — English status buttons

**Observation:** Status transition buttons use English text (assigned, in_progress, resolved, closed).

**Impact:** Low — Status values are contract-defined enums.

**Recommendation:** Could add Chinese labels, but English is acceptable for technical status.

## Conclusion

- **All pages verified normal on `codex-phase2-mainline-01`**
- **All previous blockers resolved**
- **No template fixes needed** — all templates are correctly aligned with contracts
- **No backend issues found** — all services and repositories support template expectations
- **No incidents created** — no blockers remaining
