# Low-Risk CRUD Round 2 — Implementation Report

Author: open
Branch: `agent/open-low-risk-crud-02`
Date: 2026-06-29
Task: `2026-06-29_phase2_open_low-risk-crud-01.md`

---

## Summary

實作 4 個低風險缺口，無 blocking dependency，無 model / data_contract 更動。

| ID | Gap | Route | Risk | Status |
|----|-----|-------|------|--------|
| T3.1 | 刪除房東 | `POST /landlords/<id>/delete` | LOW | ✅ |
| T3.2 | 刪除承租人 | `POST /tenants/<id>/delete` | LOW | ✅ |
| T3.3 | 刪除水費單 | `POST /water/<id>/delete` | LOW | ✅ |
| T5.1 | 依物業篩選電費單 | `GET /electricity/property/<id>/bills` | MEDIUM | ✅ |

---

## Files Changed

### Routes (4 files)
- `app/modules/landlords/routes.py` — added `landlord_delete`
- `app/modules/tenants/routes.py` — added `tenant_delete`
- `app/modules/water/routes.py` — added `water_delete`
- `app/modules/electricity/routes.py` — added `property_bills`

### Services (3 files)
- `app/services/landlord_service.py` — added `delete_landlord` with properties safety check
- `app/services/tenant_service.py` — added `delete_tenant` with contracts safety check
- `app/services/water_service.py` — added `delete_water_bill`

### Repositories (4 files)
- `app/repositories/landlord_repository.py` — added `delete`
- `app/repositories/tenant_repository.py` — added `delete`
- `app/repositories/water_repository.py` — added `delete`
- `app/repositories/electricity_repository.py` — added `list_by_property`

### Templates (4 files)
- `app/templates/landlords/list.html` — added delete button with confirm
- `app/templates/tenants/list.html` — added delete button with confirm
- `app/templates/water/list.html` — added delete button with confirm
- `app/templates/electricity/property_bills.html` — new property filter page

### Tests (1 file)
- `tests/integration/test_low_risk_crud.py` — 5 tests covering all new routes

---

## Design Decisions

1. **Safety checks**: Delete landlord/tenant is blocked if dependent records exist (properties / contracts). Flash error message returned. Delete water bill has no dependent records => direct delete.
2. **Pattern consistency**: Follows existing route pattern (POST-only for mutations, flash + redirect). Delete button uses `<form method="post">` with JS confirm dialog, matching existing `bill_calculate` pattern.
3. **Property filter**: Minimal template showing bills filtered by property_id. Links back to electricity dashboard.
4. **No cascade delete**: Repository delete is hard-delete. Safety is enforced at service layer.

---

## Verification

- `pytest tests/integration/test_low_risk_crud.py -q` → 5 passed
- `pytest tests/integration -q` → 34 passed, 15 skipped (no regressions)
- All routes confirmed via `app.url_map`

---

## Backlog Items Closed

- T3.1 (delete landlord) — route + safety check + template button
- T3.2 (delete tenant) — route + safety check + template button
- T3.3 (delete water bill) — route + template button
- T5.1 (electricity property filter) — route + template

Remaining T3 items: none (all 3 delete CRUD done)
Remaining T5 items: T5.2 (property new-bill), T5.3 (quick-reading), T5.4 (reading-log) — not started
