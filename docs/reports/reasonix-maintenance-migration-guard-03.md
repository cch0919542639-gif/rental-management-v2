# Phase 2B — Maintenance Migration Guard Note

Date: 2026-06-29
Author: reasonix
Branch: `agent/reasonix-maintenance-migration-guard-03`
Purpose: Define migration-safe boundaries for MaintenanceRequest schema, legacy data cleaning, and ondelete/transition rules.

---

## 1. Summary

| Category | Count |
|----------|-------|
| Fields safe for direct migration | 18 |
| Conditional fields (need pre-check) | 2 |
| Fields requiring ADR before migration | 0 |
| Legacy cleaning rules (directly implementable) | 3 |
| Legacy cleaning requiring manual verification | 1 |
| Status transitions safe to implement | 8 |
| Transitions requiring ADR | 2 |
| Delete/ondelete rules (directly implementable) | 2 |
| Delete rules needing ADR | 0 |

---

## 2. Field-Level Migration Safety

### 2.1 Safe to Migrate Directly (18 fields)

All 18 fields from `maintenance-contract.md` can go directly into migration DDL:

| Field | Type | Rationale |
|-------|------|-----------|
| `id` | int PK | Standard |
| `room_id` | FK→rooms.id | Contract-specified, NOT NULL |
| `status` | varchar(20) | 6 controlled values |
| `issue_category` | varchar(20) | Nullable, safe |
| `priority` | varchar(20) | Nullable, safe |
| `title` | varchar(200) | NOT NULL per contract |
| `description` | text | Nullable |
| `reported_by_name` | varchar(100) | Free text |
| `reported_at` | datetime | Default now |
| `assigned_to_name` | varchar(100) | Nullable |
| `started_at` | datetime | Written on transition |
| `resolved_at` | datetime | Written on transition |
| `closed_at` | datetime | Written on transition |
| `estimated_cost` | numeric(10,2) | >=0 validation |
| `actual_cost` | numeric(10,2) | >=0 validation |
| `notes` | text | Nullable |
| `created_at` | datetime | TimestampMixin |
| `updated_at` | datetime | TimestampMixin |

### 2.2 Conditional Fields

| Field | Pre-check | Action |
|-------|-----------|--------|
| `issue_category` default | Confirm `other` is acceptable | Set default='other' or keep nullable |
| `priority` default | Recommend `medium` | Set default='medium' at model level |

Non-blocking — both nullable.

---

## 3. Legacy Data Cleaning Rules

### 3.1 Directly Implementable (3 rules)

**Rule C1 — Identify virtual tenant rows**
SQL: SELECT t.id, t.name, c.room_id FROM tenants t JOIN contracts c ON c.tenant_id = t.id WHERE t.name IN ('空房','待修','待補','倉庫','鐵皮') OR t.name LIKE '%待修%'
Script: `scripts/migration/clean_virtual_tenants.py` — log findings, do NOT auto-delete.

**Rule C2 — Create historical MaintenanceRequest**
For each virtual tenant with `待修`/`待補`: create MaintenanceRequest with status='closed', title=f"Legacy: {tenant.name}", description with original tenant_id. Do NOT delete tenant row.

**Rule C3 — Normalize Room.status for affected rooms**
UPDATE rooms SET status='vacant' WHERE room_id IN (SELECT ... FROM contracts + tenants) AND contract.status='terminated'. Only where contract is terminated.

### 3.2 Manual Verification Required

**Rule C4 — Active contracts with virtual tenant names**
If any virtual tenant has `active` contract: data is contradictory. Log as incident, manual resolution needed.

---

## 4. Status Transition Implementation Rules

### 4.1 Safe to Implement (8 transitions)

| From | To | Method | Validation |
|------|----|--------|------------|
| reported | assigned | assign_request() | assigned_to_name non-empty |
| assigned | in_progress | start_work() | Sets started_at=now |
| in_progress | resolved | resolve_request() | Sets resolved_at=now |
| resolved | closed | close_request() | Sets closed_at=now |
| reported | cancelled | cancel_request() | — |
| assigned | cancelled | cancel_request() | — |
| (any) | list_open | list_open() | Status IN ('reported','assigned','in_progress') |
| (any) | list_for_room | list_for_room() | Filter by room_id |

Pattern: mirror PaymentService._validate_transition().

### 4.2 Transitions Requiring ADR (deferred to Phase 3)

closed→in_progress (reopen): needs business rules.
cancelled→reported: needs workflow gap decision.

---

## 5. Delete / Cascade Rules

### 5.1 Directly Implementable

**D1 — FK ondelete=RESTRICT**
room_id = db.Column(db.Integer, db.ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False)

**D2 — Soft delete pattern**
No hard DELETE route. Add deleted_at nullable datetime if needed.

### 5.2 No ADR Needed

RESTRICT + soft-delete is standard.

---

## 6. ADR Trigger Conditions

Open ADR if any occur:
- New field added to MaintenanceRequest
- New status value needed
- Transition rule changed
- Cross-module dependency (e.g., auto-post to billing)
- Room.status value changed
- Hard delete endpoint implemented

---

## 7. Migration Order

1. Model + DDL (ondelete=RESTRICT, 4 indexes)
2. Repository + Service (state machine enforcement)
3. Routes + Forms + Templates (7+ endpoints)
4. Legacy cleaning script (Rules C1-C3)
5. Integration tests

---

## 8. Risk Register

| ID | Risk | Sev | Mitigation |
|----|------|-----|------------|
| R01 | Legacy tenant.name has unexpected patterns | MED | C4 pauses, incident file |
| R02 | FK RESTRICT blocks room deletion | LOW | Resolve/close first |
| R03 | Migration script without dry-run | MED | --dry-run flag required |

---

## 9. Decision Log

| Decision | Rationale |
|----------|-----------|
| All 18 fields safe for Phase 2B | Contract-specified |
| Legacy: create MaintenanceRequest, don't delete | Audit trail |
| FK ondelete=RESTRICT | No orphans |
| Soft-delete preferred | Data retention |
| 8 transitions safe, 2 deferred | Contract scope |

---

## Deliverables

- docs/reports/reasonix-maintenance-migration-guard-03.md
- coordination/progress/reasonix.md (updated)
- coordination/completed/reasonix.md (updated)
- Incident file: none (no blockers)
