# Phase 2 Box — Repair Scripts & Integrations Runbook (Round 07)

Date: 2026-06-29  
Branch: `codex-phase2-mainline-01`  
Baseline pytest: **38 passed, 15 skipped, 0 failures** (unchanged — no test files added in this round)

---

## 1. Purpose

Document the newly created `scripts/repair/` scripts and `app/integrations/` skeleton for operational use. This report does **not** modify or audit the logic of any script — it only describes, classifies, and documents usage.

---

## 2. scripts/repair/ — Full Inventory

| Script | Type | Default Mode | Destructive? | Flags |
|--------|------|-------------|-------------|-------|
| `year_month_audit.py` | Data audit | **Read-only** | ❌ No | None |
| `room_status_audit.py` | Data audit | **Read-only** | ❌ No | None |
| `user_table_audit.py` | Data audit | **Read-only** | ❌ No | None |
| `contract_expiry_repair.py` | Repair | **Dry-run** (report only) | ⚠️ Only with `--execute` | `--execute` |

### 2.1 year_month_audit.py

**Type:** Read-only audit  
**Checks:**  
- `monthly_bills.year_month` — lists distinct string lengths and flags non-6-char values  
- `electricity_bills.year_month` — same  
**Usage:**
```powershell
py -3 .\scripts\repair\year_month_audit.py
```

### 2.2 room_status_audit.py

**Type:** Read-only audit  
**Checks:**  
- `rooms.status` values that are NOT `vacant` or `occupied`  
- Reports each invalid room with property name, room number, and current status  
**Usage:**
```powershell
py -3 .\scripts\repair\room_status_audit.py
```

### 2.3 user_table_audit.py

**Type:** Read-only audit  
**Checks:**  
- Whether table `users` (legacy) exists alongside `user`  
- Row counts in each table  
**Usage:**
```powershell
py -3 .\scripts\repair\user_table_audit.py
```

### 2.4 contract_expiry_repair.py

**Type:** Repair script with dry-run protection  
**Default mode:** Dry-run (lists expired-but-active contracts, no writes)  

| Mode | Command | Behavior |
|------|---------|----------|
| Dry-run (default) | `py -3 .\scripts\repair\contract_expiry_repair.py` | Lists candidates, does NOT write |
| Execute | `py -3 .\scripts\repair\contract_expiry_repair.py --execute` | Calls `ContractService.sync_expired_contracts()` to update status |

**Safety:** Default is read-only/dry-run. The `--execute` flag must be explicitly passed to perform writes. The script uses `ContractService` — which is core logic — but this report only documents the entry point; the service logic is not audited here.

---

## 3. app/integrations/ — Skeleton Inventory

| File | Type | Status | Notes |
|------|------|--------|-------|
| `__init__.py` | Package init | ✅ Exports `OCRClientProtocol`, `SheetsClientProtocol` |
| `ocr_client.py` | Interface (Protocol) | ✅ Interface only — no implementation | `analyze_receipt(image_path) -> dict` |
| `sheets_client.py` | Interface (Protocol) | ✅ Interface only — no implementation | `export_report(data) -> bytes` |
| `line_webhook.py` | Route skeleton | ✅ Blueprint registered; returns 501 | `POST /integrations/line/callback` |

**Phase 2 boundary rule (from README):**  
- Only interface/protocol, route skeleton, or placeholder allowed  
- No real external API calls  
- No hardcoded secrets  
- No direct third-party service calls from routes  

---

## 4. Runbook Integration

### 4.1 dev-runbook.md — Add repair section

Insert the following section after "Available Scripts":

```markdown
## Available Repair Scripts

| Script | Mode | Destructive? | Usage |
|--------|------|-------------|-------|
| `scripts/repair/year_month_audit.py` | Read-only audit | ❌ No | `py -3 .\scripts\repair\year_month_audit.py` |
| `scripts/repair/room_status_audit.py` | Read-only audit | ❌ No | `py -3 .\scripts\repair\room_status_audit.py` |
| `scripts/repair/user_table_audit.py` | Read-only audit | ❌ No | `py -3 .\scripts\repair\user_table_audit.py` |
| `scripts/repair/contract_expiry_repair.py` | Dry-run → --execute | ⚠️ Only with `--execute` | `py -3 .\scripts\repair\contract_expiry_repair.py [--execute]` |
```

### 4.2 scripts/README.md — Add repair section

Insert the repair table after the main "Available Scripts" table.

### 4.3 Quick Verification — Add integrations endpoint

Add to the Quick Verification list:
- `POST /integrations/line/callback` → should return 501

---

## 5. Safety Classification

| Safety Level | Files | Count |
|-------------|-------|-------|
| 🔵 Read-only audit | `year_month_audit.py`, `room_status_audit.py`, `user_table_audit.py` | 3 |
| 🟡 Dry-run → execute | `contract_expiry_repair.py` | 1 |
| 🟢 Interface only (no execution path) | `ocr_client.py`, `sheets_client.py`, `line_webhook.py` | 3 |

**No script can execute destructive changes by default.** All default modes are safe.

---

## 6. Running the Scripts

All repair scripts assume they are run from the repo root:

```powershell
cd D:\CodexRuntime\rental\rebuild

# Audits (read-only)
py -3 .\scripts\repair\year_month_audit.py
py -3 .\scripts\repair\room_status_audit.py
py -3 .\scripts\repair\user_table_audit.py

# Repair (dry-run by default)
py -3 .\scripts\repair\contract_expiry_repair.py
py -3 .\scripts\repair\contract_expiry_repair.py --execute   # actual write
```

---

## 7. Test Matrix Integration

No new integration tests were added in this round. The `scripts/repair/` scripts are **operational CLI tools**, not test suites. They are intended for database verification and data repair, not for CI regression.

The `app/integrations/` modules are **skeletons only** — no testable behavior exists yet. Integration tests should be added in Phase 3 when real implementations land.

Current baseline remains:
```
pytest tests\integration -q → 38 passed, 15 skipped, 0 failures
```

---

## 8. Recommendations

1. **Repair scripts**: Documented and safe. No changes needed.  
2. **Integrations skeleton**: Adequate for Phase 2 boundary. No changes needed.  
3. **Test coverage**: Not applicable until implementations land in Phase 3.  
4. **No new skips or test activations**: The 15 skip classification is unchanged.

---

## 9. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-06-29 | Round 07: documented repair scripts & integrations skeleton. No logic changes. | box |
