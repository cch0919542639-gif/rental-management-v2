# Phase 2 Gap Audit — Route / Template / Flow Alignment

Author: open
Branch: `agent/open-gap-audit-02`
Date: 2026-06-28 15:40
Baseline: `origin/main` (commit after Codex Phase 1 push)

---

## 1. Overview

比對對象：

- **舊系統 route 矩陣**：`docs/reports/open-route-template-matrix.md` — 基於舊 `app.py`（1783 行）+ `electricity_bp.py` + `water_bill.py` + `landlord_report.py`
- **新版實作**：GitHub `origin/main` 上的 `rebuild/` 目錄（13 modules × 41 routes）

---

## 2. 已完成對應（Ported & Working）

### 2.1 Core / Auth

| Old Route | New Route | Status |
|-----------|-----------|--------|
| `/login` (GET,POST) | `/auth/login` | ✅ |
| `/logout` (GET) | `/auth/logout` | ✅ |
| `/` (dashboard) | `/` (dashboard) | ✅ |

### 2.2 Landlords

| Old Route | New Route | Status |
|-----------|-----------|--------|
| `/landlords` (GET) | `/landlords/` | ✅ |
| `/landlords/create` (GET,POST) | `/landlords/create` | ✅ |
| `/landlords/<int:id>/edit` (GET,POST) | `/landlords/<int:landlord_id>/edit` | ✅ |

### 2.3 Properties

| Old Route | New Route | Status |
|-----------|-----------|--------|
| (inline with app.py) | `/properties/` | ✅ (new) |
| (inline with app.py) | `/properties/create` | ✅ (new) |
| (inline with app.py) | `/properties/<int:property_id>/edit` | ✅ (new) |

### 2.4 Rooms

| Old Route | New Route | Status |
|-----------|-----------|--------|
| `/rooms` (GET) | `/rooms/` | ✅ |
| `/rooms/<int:id>/edit` (GET,POST) | `/rooms/<int:room_id>/edit` | ✅ |

### 2.5 Tenants

| Old Route | New Route | Status |
|-----------|-----------|--------|
| `/tenants` (GET) | `/tenants/` | ✅ |
| `/tenants/create` (GET,POST) | `/tenants/create` | ✅ |
| `/tenants/<int:id>/edit` (GET,POST) | `/tenants/<int:tenant_id>/edit` | ✅ |

### 2.6 Contracts

| Old Route | New Route | Status |
|-----------|-----------|--------|
| `/contracts` (GET) | `/contracts/` | ✅ |
| `/contracts/create` (GET,POST) | `/contracts/create` | ✅ |
| `/contracts/<int:id>/edit` (GET,POST) | `/contracts/<int:contract_id>/edit` | ✅ |
| `/contracts/<int:id>/terminate` (POST) | `/contracts/<int:contract_id>/terminate` | ✅ |

### 2.7 Payments (new PaymentRecord-based)

| Old Route | New Route | Status |
|-----------|-----------|--------|
| `/payments` (PaymentRecord list) | `/payments/` | ✅ |
| — | `/payments/create` | ✅ (new) |
| `/api/payment-records/<int:id>/verify` | `/payments/<int:payment_id>/verify` | ✅ (moved to UI) |
| — | `/payments/<int:payment_id>/reject` | ✅ (new) |
| — | `/payments/<int:payment_id>/link` | ✅ (new) |

### 2.8 Electricity

| Old Route | New Route | Status |
|-----------|-----------|--------|
| `/electricity/` | `/electricity/` | ✅ |
| — | `/electricity/bills/create` | ✅ (new — simplified) |
| — | `/electricity/bills/<int:bill_id>` | ✅ (new — detail) |
| — | `/electricity/bills/<int:bill_id>/calculate` | ✅ (new — calculate) |
| — | `/electricity/bills/<int:bill_id>/post` | ✅ (new — post to monthly) |
| `/electricity/bill/<int:bill_id>/readings` | `/electricity/bills/<int:bill_id>/readings/create` | 🟡 (renamed, partial) |
| — | `/electricity/meters/create` | ✅ (new — meters CRUD) |
| — | `/electricity/meters/<int:meter_id>/edit` | ✅ (new — meters CRUD) |

### 2.9 Water

| Old Route | New Route | Status |
|-----------|-----------|--------|
| `/water/bills` | `/water/` | ✅ |
| `/water/bills/new` | `/water/create` | ✅ |
| — | `/water/<int:water_bill_id>/edit` | ✅ (new) |
| — | `/water/<int:water_bill_id>/post` | ✅ (new — post to monthly) |

### 2.10 Reports

| Old Route | New Route | Status |
|-----------|-----------|--------|
| `/reports/monthly` | `/reports/monthly` | ✅ |
| — | `/reports/` | ✅ (new — index) |
| — | `/reports/yearly` | ✅ (new) |
| `/reports/summary` (GET) | `/reports/landlord-summary` (GET,POST) | 🟡 (renamed, not identical) |
| `/reports/landlord-report` (never registered) | — | ❌ (old blueprint never worked) |

### 2.11 Maintenance

| Old Route | New Route | Status |
|-----------|-----------|--------|
| (none) | `/maintenance/` | ✅ (placeholder) |

### 2.12 Health & Utility

| Old Route | New Route | Status |
|-----------|-----------|--------|
| (none) | `/healthz` | ✅ (new) |

---

## 3. 尚未完成的 Route / Page / Flow

### 3.1 Delete Endpoints (P2 — no delete UI)

| Missing Route | Old Pattern | Risk | Note |
|--------------|-------------|------|------|
| `landlords/<id>/delete` | POST → redirect | Low | All CRUD except delete; may be intentional |
| `tenants/<id>/delete` | POST → redirect | Low | Same pattern |
| `water/bills/<id>/delete` | POST → redirect | Low | Water bill deletion |

### 3.2 Nested Creation Routes (P2 — UX gap)

| Missing Route | Old Pattern | Risk | Note |
|--------------|-------------|------|------|
| `landlords/<lid>/properties/create` | GET,POST → room/property_form.html | Medium | UI shortcut, business flow exists |
| `properties/<pid>/rooms/create` | GET,POST → room/form.html | Medium | Same — parent-context creation |

### 3.3 Contract Billing (P1 — major billing flow gap)

| Missing Route | Old Pattern | Risk | Note |
|--------------|-------------|------|------|
| `contracts/<cid>/bills` | GET → bill/list.html | **High** | Per-contract bill listing |
| `contracts/<cid>/bills/create` | GET,POST → bill/form.html | **High** | Per-contract bill creation |

### 3.4 Batch / Generate Billing (P0 — core billing gap)

| Missing Route | Old Pattern | Risk | Note |
|--------------|-------------|------|------|
| `bill/batch_entry` | GET,POST → bill/batch_entry.html | **High** | Multi-contract batch operation |
| `bills/generate` | POST → redirect | **High** | Batch generate monthly bills |
| `bills/<id>/toggle_paid` | POST → redirect | **High** | Manual paid toggle |
| `bills/<id>/edit` (implied) | — | **High** | Monthly bill editing |

Current `billing/` module only has `billing_list()` — no create, no edit, no batch, no generate. This is the single largest Phase 1 gap.

### 3.5 Electricity Property-specific Routes (P2 — UX detail)

| Missing Route | Old Pattern | Risk | Note |
|--------------|-------------|------|------|
| `electricity/property/<id>/bills` | GET → electricity/property_bills.html | Medium | Filter by property |
| `electricity/property/<id>/new-bill` | GET,POST → electricity/new_bill.html | Medium | Property-specific bill creation |
| `electricity/property/<id>/quick-reading` | GET,POST → electricity/quick_reading.html | Low | Fast meter reading |
| `electricity/property/<id>/reading-log` | GET → electricity/reading_log.html | Low | Reading history |

### 3.6 Water Preview (P2)

| Missing Route | Old Pattern | Risk | Note |
|--------------|-------------|------|------|
| `water/preview` | POST → water/bill_result.html | Low | Water bill preview |

### 3.7 Integrations (P2 — infra gap, no code at all)

| Missing Route | Old Pattern | Risk | Note |
|--------------|-------------|------|------|
| `/api/analyze-receipt` | POST → JSON | Medium | OCR receipt analysis |
| `/api/payment-records` (GET,POST) | GET,POST → JSON | Low | API variant (UI exists) |
| `/api/payment-records/<id>/analyze` | POST → JSON | Low | OCR + payment analysis |
| `/api/electricity/create-from-ocr` | POST → JSON | Low | OCR electricity bill |
| `/callback` | POST → text | Low | LINE Bot Webhook |
| `/sheets/import` | GET,POST → sheets/import.html | Low | Google Sheets import |

### 3.8 Error Page Templates (P3 — cosmetic)

| Missing | Old Template | Risk | Note |
|---------|-------------|------|------|
| HTML error pages | `error/404.html`, `error/500.html` | Low | Current = JSON/text only |

---

## 4. 可進入 Phase 2 的缺口清單（Prioritized）

### Tier 1 — Core Billing Flow (P0)

| Priority | Gap | Rationale |
|----------|-----|-----------|
| 1 | `bills/generate` (batch monthly bill generation) | Core monthly workflow blocked |
| 2 | `billing/` create + edit routes | Current `billing/` module is read-only |
| 3 | `bill/batch_entry` (multi-contract batch) | Operational necessity |
| 4 | `contracts/<cid>/bills` (per-contract bill view) | UX blocker for tenant billing lookup |

### Tier 2 — Delete & Nested CRUD (P2)

| Priority | Gap | Rationale |
|----------|-----|-----------|
| 5 | `landlords/<id>/delete` | Admin completeness |
| 6 | `tenants/<id>/delete` | Admin completeness |
| 7 | `water/bills/<id>/delete` | Admin completeness |
| 8 | `landlords/<lid>/properties/create` | Navigation UX |
| 9 | `properties/<pid>/rooms/create` | Navigation UX |

### Tier 3 — Electricity Detail (P2)

| Priority | Gap | Rationale |
|----------|-----|-----------|
| 10 | `electricity/property/<id>/bills` | Property drill-down |
| 11 | `electricity/property/<id>/new-bill` | Property-specific creation |

### Tier 4 — Integrations (P2)

| Priority | Gap | Rationale |
|----------|-----|-----------|
| 12 | `/callback` (LINE webhook) | External integration — rebuild needed |
| 13 | `/api/analyze-receipt` (OCR) | Receipt analysis feature |
| 14 | `/sheets/import` | Data import pipeline |

### Tier 5 — Polish (P3)

| Priority | Gap | Rationale |
|----------|-----|-----------|
| 15 | Error page templates (404/500 HTML) | User experience |
| 16 | `water/preview` | UX convenience |

---

## 5. Phase 2 Gap Summary Statistics

| Category | Count | Notes |
|----------|-------|-------|
| ✅ Route fully ported | 27 | Core CRUD + auth + dashboard |
| 🟡 Route partially ported / renamed | 3 | electricity readings, landlord-summary, bills |
| ❌ Route not ported (needed) | 22 | See section 3 |
| 💀 Route not ported (intentional) | 5 | Old `Payment` class dead code |
| ✨ New route (no old equivalent) | 14 | meters CRUD, healthz, payment review flow, etc. |

| Metric | Value |
|--------|-------|
| Total modules | 13 |
| Total routes registered | 41 |
| Templates written | 32 |
| Services | 15 |
| Repositories | 12 |
| Integration code | **0 files** |
| Migration scripts | **0 files** |
| P0 gap count | 4 (tier 1 billing) |
| P2 gap count | 15 |

---

## 6. Recommendations

1. **Phase 2 應優先補完 billing module 的 create/generate/batch 流程** — 這是目前 Phase 1 最大缺口。`billing/` 模組目前只有 list 功能，無法建立月帳單。
2. **Integrations 目錄保持現狀** — LINE/OCR/Sheets 可等 core billing 穩定後再處理。`app/integrations/` 已有 README 佔位。
3. **Error handler 補 HTML template** — 低風險、高 UX 改善比。可在 Phase 2 尾聲一次性加入。
4. **Delete endpoints 評估是否真的需要** — 若 data_contract 設計為 soft-delete / archived，則可確認此缺口不存在。
5. **billing gap 可能影響 electricity/water 的 post-to-monthly flow** — 確認 electricity bill post、water bill post 目前是否能正常寫入 monthly_bills。若無法，這會是 blocking issue。
