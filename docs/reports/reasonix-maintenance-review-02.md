# Maintenance Contract & Flow Design — Phase 2 Round 2 Review

Date: 2026-06-29  
Author: reasonix  
Branch: `agent/reasonix-maintenance-review-02`  
Review Scope: `maintenance-contract.md` + `maintenance-schema-flow-design-2026-06-29.md` vs. Phase 0 frozen decisions  

---

## Executive Summary

| Dimension | Verdict |
|-----------|---------|
| Frozen contracts compliance | ✅ **Pass** — 0 violations |
| Design soundness | ✅ **Ready for implementation** |
| Items blocking implementation | **None** — all green |
| Items needing ADR before Phase 2B | 2 advisory items |
| Forbidden actions | 3 clear prohibitions |

**Overall: The maintenance contract and flow design are compliant and implementation-ready.** Codex may proceed with Phase 2A implementation (model → repository → service → routes → templates → tests) following the specified boundaries.

---

## 1. Compliance Check Against Frozen Decisions

### 1.1 Room.status Protection

| Rule | Source | Design Compliance |
|------|--------|-------------------|
| Room.status 僅允許 `vacant` / `occupied` | `status-machines.md` | ✅ **Compliant** — maintenance-contract.md explicitly states "maintenance 狀態不得污染 Room.status" |
| 待修不屬於 room status | `status-machines.md` | ✅ **Compliant** — MaintenanceRequest is an independent table |
| 禁止以自由文字塞入 status 欄位 | `status-machines.md` | ✅ **Compliant** — status is a controlled enum |

### 1.2 Tenant.name Protection

| Rule | Source | Design Compliance |
|------|--------|-------------------|
| 不可用虛擬 tenant 名稱表示待修 | Architecture Decision | ✅ **Compliant** — maintenance-contract.md explicitly prohibits this, provides migration guidance |

### 1.3 Contract.status Protection

| Rule | Source | Design Compliance |
|------|--------|-------------------|
| Contract.status 僅 `active` / `expired` / `terminated` | `status-machines.md` | ✅ **Compliant** — design states "不因 maintenance 直接改變" |

### 1.4 Parallel Rebuild Architecture

| Rule | Source | Design Compliance |
|------|--------|-------------------|
| Module boundary: module → service → repository → model | Dependency Map | ✅ **Compliant** — design follows same pattern |
| Module A → Module B (forbidden) | Dependency Map | ✅ **Compliant** — maintenance only depends on Room model |
| No `from app import` reverse coupling | Dependency Map | ✅ **Compliant** — new module, no old coupling |

### 1.5 Phase 0 Scope Boundaries

| Rule | Source | Design Compliance |
|------|--------|-------------------|
| PaymentRecord 為唯一付款實體 | Architecture Decision | ✅ **N/A** — maintenance has no payment fields |
| year_month = YYYYMM | Architecture Decision | ✅ **N/A** — maintenance has no year_month dependency |

---

## 2. Design Review — Implementation Readiness

### 2.1 Green Light Items (可直接施工)

These can proceed to implementation without additional ADR:

| Item | File | Detail | Risk |
|------|------|--------|------|
| ✅ **MaintenanceRequest model** | `app/models/maintenance.py` | Fields matching contract schema; use `BaseModel` + `TimestampMixin` | LOW |
| ✅ **MaintenanceRepository** | `app/repositories/maintenance_repository.py` | CRUD + filter by status/priority/room_id + list_open() | LOW |
| ✅ **MaintenanceService** | `app/services/maintenance_service.py` | State-machine-enforced transitions per contract | LOW |
| ✅ **Maintenance forms** | `app/modules/maintenance/forms.py` | CreateForm / AssignForm / ResolveForm / CloseForm | LOW |
| ✅ **Maintenance routes** | `app/modules/maintenance/routes.py` | list / create / detail / assign / start / resolve / close | LOW |
| ✅ **Maintenance templates** | `app/templates/maintenance/` | Following existing template patterns | LOW |
| ✅ **List + filter UI** | routes + template | By room, status, priority | LOW |
| ✅ **Tests** | `tests/integration/` | Smoke tests for CRUD + state transitions | LOW |

### 2.2 Advisory Items (建議先確認，不 blocking)

| ID | Item | Recommendation | Severity |
|----|------|---------------|----------|
| A01 | **`issue_category` enum** — contract defines 6 categories (`electricity`, `water`, `facility`, `cleaning`, `appliance`, `other`). Should confirm this covers actual business needs before freezing in migration. | Codex can proceed with the proposed list; add a comment that it may expand. | LOW |
| A02 | **`priority` default** — contract defines `low/medium/high/urgent` but no default value specified. Suggest default = `medium` to match common UX patterns. | Not blocking; can be set at model level. | LOW |

### 2.3 Must-ADR Items (必須再 ADR)

| ID | Item | Why | When |
|----|------|-----|------|
| — | **None identified** | All design decisions align with frozen contracts | — |

### 2.4 Forbidden Items (禁止事項)

| ID | Action | Why |
|----|--------|-----|
| F01 | ❌ 在 `Room` table 加 `maintenance_status` 或 `maintenance_flag` | 違反 Phase 0 隔離原則，污染 Room 語義 |
| F02 | ❌ 在 `Tenant.name` 塞入「待修」等關鍵字 | 回歸舊系統模式，違反已修正的契約 |
| F03 | ❌ 改 `Room.status` 允許值（新增 `under_maintenance` 等） | 違反 `status-machines.md` 凍結定義 |

---

## 3. Detailed Schema Review

### 3.1 MaintenanceRequest Fields

| Field | Contract Spec | Assessment | Verdict |
|-------|--------------|------------|---------|
| `id` | int PK | Standard | ✅ |
| `room_id` | FK → rooms.id, NOT NULL | Correct — maintenance belongs to a room. **Recommend adding `ondelete="RESTRICT"`** to prevent deleting a room with active maintenance requests. | ✅ with note |
| `status` | varchar(20), NOT NULL, controlled enum | Correct | ✅ |
| `issue_category` | varchar(20), nullable | OK for Phase 2A | ✅ |
| `priority` | varchar(20), nullable, default? | **Recommend default = `medium`** | ✅ with note |
| `title` | varchar(200), NOT NULL | Correct | ✅ |
| `description` | text, nullable | OK | ✅ |
| `reported_by_name` | varchar(100) | Simple string — no User FK, OK for Phase 1 | ✅ |
| `reported_at` | datetime, default=now | Correct | ✅ |
| `assigned_to_name` | varchar(100) | Simple string — no User FK, OK for Phase 1 | ✅ |
| `started_at` | datetime, nullable | Written when status→in_progress | ✅ |
| `resolved_at` | datetime, nullable | Written when status→resolved | ✅ |
| `closed_at` | datetime, nullable | Written when status→closed | ✅ |
| `estimated_cost` | numeric(10,2), nullable, >=0 | Contract says non-negative | ✅ |
| `actual_cost` | numeric(10,2), nullable, >=0 | Contract says non-negative | ✅ |
| `notes` | text, nullable | OK | ✅ |
| `created_at` | datetime (TimestampMixin) | Standard | ✅ |
| `updated_at` | datetime (TimestampMixin) | Standard | ✅ |

### 3.2 Recommended Indexes

| Index | Contract Says | Assessment |
|-------|--------------|------------|
| `idx_maintenance_room_id` | ✅ | Important for per-room queries |
| `idx_maintenance_status` | ✅ | Important for open-request filtering |
| `idx_maintenance_priority` | ✅ | Useful for triage UI |
| `idx_maintenance_reported_at` | ✅ | Useful for sort-by-date |

All indexes are reasonable for Phase 2A.

### 3.3 Missing But Optional

| Item | Recommendation | Blocking? |
|------|---------------|-----------|
| `ondelete` behavior on `room_id` FK | Recommend `RESTRICT` to prevent orphan requests | No — can be added post-launch |
| `updated_by` (who last changed status) | Not in contract scope; defer to Phase 3 | No |
| Composite index `(status, priority)` | Optional performance optimization | No |

---

## 4. State Machine Review

### 4.1 Proposed State Machine

```text
reported ──→ assigned ──→ in_progress ──→ resolved ──→ closed
    │                                            │
    └──→ cancelled                                └──→ (terminal)
assigned ──→ cancelled
```

### 4.2 Compliance Check

| Rule | Frozen Contract | Design | Verdict |
|------|----------------|--------|---------|
| Status values not conflicting with Room/Contract/others | `status-machines.md` | All values are unique to maintenance | ✅ |
| Transitions are controlled | Architecture pattern | Service layer enforces transitions | ✅ |
| Terminal states don't allow re-entry | Contract | `closed` / `cancelled` are terminal | ✅ |

### 4.3 Suggested Service API

```python
class MaintenanceService:
    @staticmethod
    def create_request(room_id, title, description, ...) -> MaintenanceRequest
    @staticmethod
    def assign_request(request, assigned_to_name) -> MaintenanceRequest
    @staticmethod
    def start_work(request) -> MaintenanceRequest
    @staticmethod
    def resolve_request(request, actual_cost=None) -> MaintenanceRequest
    @staticmethod
    def close_request(request) -> MaintenanceRequest
    @staticmethod
    def cancel_request(request) -> MaintenanceRequest
    
    # Query helpers
    @staticmethod
    def list_open() -> list[MaintenanceRequest]
    @staticmethod
    def list_for_room(room_id) -> list[MaintenanceRequest]
```

State transition enforcement should mirror `PaymentService._validate_transition()` pattern.

---

## 5. Migration Note

### 5.1 Legacy Data Risk

The contract's migration guidance is correct but should be highlighted:

> 舊資料若有 `tenant.name = 待修`，不得直接搬成 tenant。需在 migration 階段轉成：正常 `Room.status` + 獨立 `MaintenanceRequest`。

This means a pre-Phase-2 migration script must:
1. Query `tenants` for rows where `name` contains `待修` / `待補`
2. For each, find the associated `Room` via `Contract`
3. Create a `MaintenanceRequest` with `status='resolved'` or `'closed'` (historical)
4. Mark the tenant row as migrated (or delete if confirmed safe)

**This is not a Phase 2A blocking task** — the migration can wait until Phase 2B or Phase 3 when legacy data is formally imported. But the risk should be documented.

---

## 6. Risk Register

| ID | Risk | Severity | Mitigation |
|----|------|----------|------------|
| R01 | `room_id` FK without `ondelete` — deleting a room could orphan maintenance requests | LOW | Add `ondelete="RESTRICT"` at model creation time |
| R02 | No explicit `updated_by` tracking — audit trail for status changes is implicit | LOW | Acceptable for Phase 2A; add in Phase 3 if needed |
| R03 | Migration from legacy `tenant.name = 待修` not yet scripted | MEDIUM | Document as Phase 2B/3 follow-up; do not attempt in Phase 2A |
| R04 | Template/UI not yet designed — may need iteration after user feedback | LOW | Phase 2B scope; Phase 2A can ship with basic CRUD UI |

---

## 7. Implementation Order Recommendation

### Phase 2A (This Round — Codex)

| Step | Action | Est. Files |
|------|--------|-----------|
| 1 | Create `app/models/maintenance.py` — MaintenanceRequest model | 1 |
| 2 | Add to `app/models/__init__.py` | 0 |
| 3 | Create `app/repositories/maintenance_repository.py` | 1 |
| 4 | Create `app/services/maintenance_service.py` — with state machine | 1 |
| 5 | Create `app/modules/maintenance/forms.py` — CreateForm / AssignForm / ResolveForm / CloseForm | 1 |
| 6 | Update `app/modules/maintenance/routes.py` — full CRUD + status transitions | 1 |
| 7 | Create templates: list.html, detail.html, form.html | 3-4 |
| 8 | Create `tests/integration/test_maintenance_flow.py` | 1 |
| 9 | Update old `room_snapshot()` or replace with MaintenanceRequest-based view | 1 |

**Total: ~10-12 files, all new or replacement**

### Phase 2B (Next Round)

| Step | Action |
|------|--------|
| 1 | Add filter UI (status, priority, date range) |
| 2 | Add cost summary to reports module |
| 3 | Review and adjust templates based on feedback |
| 4 | Migration script for legacy `tenant.name = 待修` data |

---

## 8. Decision Log

| Decision | Rationale |
|----------|-----------|
| MaintenanceRequest 採獨立表 + room_id FK | 符合 Phase 0 隔離原則 |
| 狀態機採 6 值（reported/assigned/in_progress/resolved/closed/cancelled） | 涵蓋最小維修 lifecycle，無冗餘 |
| issue_category 和 priority 先用 contract 建議值 | 可擴充，不阻礙 Phase 2A |
| FK 建議加 `ondelete="RESTRICT"` | 避免孤兒資料 |
| Migration from legacy 待修資料暫緩 | 不阻礙 Phase 2A 施工 |

---

## 9. Summary

| Category | Count |
|----------|-------|
| ✅ Directly implementable items | 8 (model → repository → service → routes → forms → templates → tests) |
| ⚠️ Advisory items (non-blocking) | 2 (issue_category confirmation, priority default) |
| ❌ Must-ADR items | 0 |
| 🚫 Forbidden actions | 3 (Room.status corruption, Tenant.name pollution, Contract.status pollution) |
| 🔴 Blocking risks | 0 |
| 🟡 Documented risks | 4 |

**Final verdict**: Ready for Phase 2A implementation. Codex may proceed.
