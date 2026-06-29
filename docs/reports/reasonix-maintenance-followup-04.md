# Maintenance Implementation Follow-Up Guard

Date: 2026-06-29
Author: reasonix
Baseline: `codex-phase2-mainline-01` (maintenance core already implemented)
Previous: `reasonix-maintenance-review-02.md`, `reasonix-maintenance-migration-guard-03.md`

---

## Baseline Confirmation

The following maintenance core is **already implemented** on `codex-phase2-mainline-01`:

| Layer | File | Status |
|-------|------|--------|
| Model | `app/models/maintenance.py` — 18 fields, FK→rooms.id, indexes | ✅ |
| Service | `app/services/maintenance_service.py` — 8 transitions enforced | ✅ |
| Repository | `app/repositories/maintenance_repository.py` — CRUD + list_open + list_for_room | ✅ |
| Routes | `app/modules/maintenance/routes.py` — create/edit/transition | ✅ |
| Forms | `app/modules/maintenance/forms.py` — 6 categories, 4 priorities | ✅ |
| Templates | `app/templates/maintenance/` — index + form | ✅ |
| Tests | `tests/integration/test_maintenance_core_flow.py` + readiness | ✅ |

---

## 1. List / Filter Enhancement

### Current State
- `list_all()` — returns all requests ordered by reported_at desc
- `list_open()` — filters to `reported/assigned/in_progress` only
- No status/priority/date-range filter in UI or repository

### Verdict

| Item | Category | Rationale |
|------|----------|-----------|
| Add `list_by_status(status)` to repository | ✅ 可直接實作 | Pure query extension, no schema/contract change |
| Add `list_by_priority(priority)` to repository | ✅ 可直接實作 | Same pattern |
| Add date-range filter to repository | ✅ 可直接實作 | Uses existing `reported_at` column |
| Add filter UI (dropdowns) to template | ✅ 可直接實作 | Template-only, no backend change needed |
| Composite filter (status+priority+date) | ✅ 可直接實作 | Repository method combining existing columns |

**No ADR needed.** These are standard query extensions following existing repository patterns.

---

## 2. Cost Summary / Report Integration

### Current State
- `estimated_cost` and `actual_cost` fields exist on model
- No aggregation logic anywhere
- Reports module has no maintenance cost awareness

### Verdict

| Item | Category | Rationale |
|------|----------|-----------|
| Add `MaintenanceRepository.total_cost_by_status()` | ✅ 可直接實作 | Pure SQL SUM aggregation, no schema change |
| Add `MaintenanceRepository.cost_by_property()` | ✅ 可直接實作 | JOIN room→property, aggregate |
| Expose cost data in `ReportService` | ✅ 可直接實作 | New method on existing service |
| Add cost columns to maintenance list UI | ✅ 可直接實作 | Template display only |
| Auto-post maintenance cost to `MonthlyBill.other_charges` | ⚠️ 需先 ADR | Cross-module boundary — billing contract impact. Needs decision: which cost category, which status triggers posting, manual vs auto. |
| Integrate into landlord yearly summary | ✅ 可直接實作 | New query + template column |

**ADR needed only for cross-module auto-posting** (maintenance cost → MonthlyBill).

---

## 3. Delete / Archive Policy

### Current State
- No delete route exists
- No soft-delete column on model
- FK on `room_id` has no explicit `ondelete` behavior

### Verdict

| Item | Category | Rationale |
|------|----------|-----------|
| Add `deleted_at` nullable DateTime column | ⚠️ 需先 ADR | Schema change — needs data retention policy decision |
| Add hard-delete route | 🚫 禁止 | Phase 1 contract: no hard delete without ADR |
| Add soft-delete route (sets `deleted_at`) | ⚠️ 需先 ADR | Same as above — needs policy |
| Add FK ondelete=RESTRICT (migration) | ⚠️ 需先 ADR | Schema change — affects existing data if rooms are deleted |
| Add `is_archived` boolean + archive route | ⚠️ 需先 ADR | New status semantics — overlaps with `closed`/`cancelled` |
| Admin-only archive button in UI | ⚠️ 需先 ADR | Depends on archive policy decision |

**ADR needed** because any delete/archive mechanism touches data retention, which has no current policy. Recommended approach: soft-delete with `deleted_at`, implemented in Phase 3.

---

## 4. Migration Execution Order

### Current State
- No migration script exists in `scripts/migration/`
- Model is created but not imported in `app/models/__init__.py`
- Legacy `tenant.name` cleaning not started

### Verdict

| Step | Category | Detail |
|------|----------|--------|
| Add `MaintenanceRequest` to `app/models/__init__.py` | ✅ 可直接實作 | One-line import; currently missing |
| Write DB migration (Alembic or raw SQL) | ✅ 可直接實作 | Creates maintenance_requests table |
| Write legacy cleaning script C1-C3 (identify virtual tenants) | ✅ 可直接實作 | Per migration-guard-03 rules |
| Write legacy cleaning C4 (active contracts) | ⚠️ 需手動驗證 | Requires human to resolve contradictory data |
| Run migration on production | 🚫 禁止 | Must go through review gate + dry-run first |

**Recommended order:**
1. Fix `app/models/__init__.py` (add import) — 1 min
2. Generate DDL migration
3. Write `scripts/migration/clean_virtual_tenants.py` (C1-C3)
4. Run dry-run + review
5. Production migration

---

## 5. Reopen / Cancelled Follow-Up Policy

### Current State
- `closed: set()` and `cancelled: set()` — no transitions out
- Per contract: "不可從 closed 回到 in_progress"
- Per contract: "不可從 cancelled 回到 reported"

### Verdict

| Item | Category | Rationale |
|------|----------|-----------|
| Keep current transition table (closed→∅, cancelled→∅) | ✅ 已正確實作 | Matches contract exactly |
| Add `reopened` status value | ⚠️ 需先 ADR | New status = schema change + affects all transitions. Needs: can reopened → in_progress? reopened → resolved? cost accounting rules? |
| Add `on_hold` status value | ⚠️ 需先 ADR | New status — needs SLA semantics |
| Single "reopen" button that creates new request from old | ✅ 可直接實作 | No schema change — clone-and-create pattern in UI only |
| Allow `cancelled→reported` | 🚫 禁止 | Contract explicitly forbids: "若需要重新處理，應建立新 request" |

**ADR needed for any new status value.** The current "create new request" workaround is sufficient for Phase 2.

---

## Summary Table

| Area | ✅ 可直接實作 | ⚠️ 需先 ADR | 🚫 禁止 |
|------|-------------|-------------|---------|
| List/filter | 4 items | 0 | 0 |
| Cost/report | 3 items | 1 (auto-post to billing) | 0 |
| Delete/archive | 0 | 3 | 1 (hard delete) |
| Migration | 3 items | 0 | 1 (prod without review) |
| Reopen policy | 1 item (clone pattern) | 1 (new status) | 1 (cancelled→reported) |
| **Total** | **11** | **5** | **3** |

## Incident Report

None needed — no blockers encountered. All decisions are uniquely derivable from existing contracts, guard notes, and implemented code.

---

## Deliverables

- `docs/reports/reasonix-maintenance-followup-04.md`
- `coordination/progress/reasonix.md`
- `coordination/completed/reasonix.md`
