# Phase 2 Migration & Integration Boundary — Guard Report

Date: 2026-06-29
Author: reasonix
Baseline: `codex-phase2-mainline-01` (38 passed, 15 skipped)
Previous: contract-notes-01 / review-02 / migration-guard-03 / followup-04 / phase2b-review-05

---

## 1. Executive Summary

| Area | Direct | Need ADR | Forbidden |
|------|--------|----------|-----------|
| Migration scripts | 7 | 2 | 2 |
| Integration boundary | 2 | 1 | 4 |
| **Total** | **9** | **3** | **6** |

All 6 required inspection areas have been checked. No blocking contradictions found.

---

## 2. Migration: Direct / ADR / Forbidden

### 2.1 Directly Implementable (7 items)

| # | Migration | Script | Rationale |
|---|-----------|--------|-----------|
| M1 | Create `maintenance_requests` DDL | `scripts/migration/001_create_maintenance_requests.sql` | Model exists; no FK ondelete choice yet (RESTRICT recommended) |
| M2 | Virtual tenant scan (C1) | `scripts/migration/maintenance_legacy_scan.py` | Already written and read-only |
| M3 | Virtual tenant → MaintenanceRequest (C2) | New: `002_migrate_virtual_tenants.py` | Creates closed MaintenanceRequest rows; does NOT delete tenants |
| M4 | Room.status normalization (C3) | New: `003_normalize_room_status.py` | Sets `vacant` where contract=terminated + virtual tenant |
| M5 | C4 active-contract detection | New: `004_detect_ambiguous_tenants.py` | Read-only report; flags rows needing manual review |
| M6 | Contract.status expiry repair | New: `005_repair_expired_contracts.py` | Sets `expired` where `end_date < today AND status='active'` |
| M7 | `user` / `users` double-table detection | New: `006_scan_user_tables.py` | Read-only: reports both table row counts |

### 2.2 Needs ADR Before Migration (2 items)

| # | Migration | Why ADR Needed | Risk if Done Now |
|---|-----------|----------------|------------------|
| A1 | `user` / `users` merge + drop | Data loss if merge logic is wrong. Need clear mapping rule for `role` and `landlord_id` between tables. | HIGH: account loss |
| A2 | `year_month` format repair on existing data | Need to confirm whether any historical data uses `YYYY-MM` format vs `YYYYMM`. Read-only scan first, then ADR for repair approach. | MEDIUM: wrong format breaks queries |

### 2.3 Forbidden (2 items)

| # | Migration | Why Forbidden |
|---|-----------|---------------|
| F1 | DELETE virtual tenant rows directly | Data loss risk. Rule C2 says create MaintenanceRequest + leave tenant row. |
| F2 | ALTER `electricity_bills.year_month` to String(6) without backup | Schema change on production data. Must go through formal migration with rollback. |

---

## 3. Integration Boundary: Direct / ADR / Forbidden

### 3.1 Directly Implementable (2 items)

| # | Integration | Scope | Rationale |
|---|-------------|-------|-----------|
| I1 | `app/integrations/__init__.py` + stub README | Directory structure only | Already has README placeholder; no code needed yet |
| I2 | `integrations/base.py` abstract client | Define base class for future OCR/LINE/Sheets clients | No external dependency; pure interface design |

### 3.2 Needs ADR (1 item)

| # | Integration | Why ADR Needed |
|---|-------------|----------------|
| A3 | OCR service client spec | Need to decide: which OCR engine? cloud vs local? expected response schema? `PaymentRecord` fields already exist but OCR integration requires external API key management. |

### 3.3 Forbidden (4 items)

| # | Integration | Why Forbidden |
|---|-------------|---------------|
| F3 | LINE webhook `/callback` | External inbound webhook requires: server deployment, LINE channel secret, message parsing. Phase 3 scope. |
| F4 | Google Sheets import `/sheets/import` | Requires OAuth2, Google API project. Phase 3 scope. |
| F5 | Live OCR `/api/analyze-receipt` | Requires external API key + image upload endpoint. Do not implement until integration ADR is approved. |
| F6 | Auto-post maintenance cost to MonthlyBill | Cross-module coupling. Followup-04 classified as ADR-needed. Do not implement. |

**Current max integration level**: Boundary-only. `app/integrations/` can have stubs + base classes. No external API calls, no webhooks, no OAuth flows.

---

## 4. Safe Script Types for Mainline

These script types can be added without review:

| Type | Example | Max Complexity |
|------|---------|---------------|
| Read-only scan | `maintenance_legacy_scan.py` | SELECT + PRINT only |
| DDL creation | `001_create_table.sql` | CREATE TABLE, CREATE INDEX |
| Data normalization | Room.status repair | UPDATE with WHERE + DRY-RUN mode |
| Detection report | Ambiguous tenant report | PRINT summary + affected rows |
| Contract expiry sync | `expired` status repair | Limited scope, reversible |

All scripts must include:
- `--dry-run` flag that only prints, never writes
- Clear log of affected rows before any write
- Rollback instruction in script header

---

## 5. External Integration Types NOT to Do Now

| Integration | Current Max Level | Phase |
|-------------|------------------|-------|
| LINE webhook | Stub interface only | Phase 3 |
| OCR receipt analysis | Schema fields exist, no client code | Phase 3 |
| Google Sheets import | No code | Phase 3 |
| Email notification | No code | Phase 3 |
| SMS notification | No code | Phase 3 |

**Rule**: If it needs an API key, external credential, or public URL — don't implement in Phase 2.

---

## 6. Priority Recommendation for Codex

| Priority | Work | Effort | Depends On |
|----------|------|--------|------------|
| P0 | M1 + M6 (DDL + contract expiry repair) | 2 scripts | None |
| P1 | M2-M4 (virtual tenant migration — scan, create requests, normalize) | 3 scripts | M1 done |
| P2 | M5 + M7 (detection scripts for ambiguous data) | 2 scripts | None |
| P3 | I1 + I2 (integration stubs) | 2 files | None |
| P4 | A1-A2 ADR (user merge + year_month repair) | 2 ADRs | Requires data analysis first |

---

## Deliverables

- `docs/reports/reasonix-phase2-migration-integration-06.md`
- `coordination/progress/reasonix.md`
- `coordination/completed/reasonix.md`
- Incident file: none needed
