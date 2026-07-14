# Missing Monthly Bills Backfill — Contract & Risk Guard

Date: 2026-07-14
Author: reasonix
Branch: `agent/reasonix-missing-monthly-bills-guard-01`
Baseline: `codex-phase2-mainline-01`
Scope: 27 missing 202604 bills + 1 missing 202605 bill for existing contracts
Status: **Guard Report** — read before any backfill execution

---

## Executive Summary

This report classifies every field involved in backfilling historical monthly bills from Google Sheet evidence into three tiers:

| Classification | Count | Meaning |
|---------------|-------|---------|
| **DIRECT** — carry from Sheet | 8 | Evidence is unambiguous; field can be populated directly |
| **CAUTION** — stop condition required | 9 | Must be gated by a verifiable condition before proceeding |
| **FORBIDDEN** — never auto-set | 5 | Would violate frozen contracts or cause data corruption |

The backfill must use **only** the old system Google Sheet as evidence (`1WmqQbPo8EsWrbplDInp1Q3rv6bYsCcesh4BE6qYJ-dc`, tabs `202604` and `202605`, exported as `real_import/sheet_202604.csv` and `real_import/sheet_202605.csv`). No other data source is authorized.

---

## 1. Frozen Data Contract (Reaffirmed)

These rules are non-negotiable and must govern every backfill operation:

| Rule | Source | Enforcement |
|------|--------|-------------|
| `year_month` = `YYYYMM` (String(6)) | `data_contracts/billing-contract.md` §format | Validate before insert |
| `contract_id + year_month` UNIQUE | DB `UniqueConstraint` + contract | Check before every insert |
| `total = rent + electricity_amount + public_electricity + water_amount + other_charges + previous_balance` | `MonthlyBill.calculate_total()` | Recalculate; never copy Sheet's 應繳 directly |
| `previous_balance` is signed (±) | Incident `2026-07-12_batch2-monthly-bill-total-reconciliation.md` | Positive = prior unpaid; negative = prior credit |
| `paid` controlled by PaymentRecord reconciliation | `docs/reports/reasonix-phase2-contract-notes-01.md` §1.4 | Never set `paid` from Sheet's 已繳 column |
| No modification of `app/`, `scripts/`, `tests/`, or DB schema | Task constraint | Read-only audit + controlled backfill |

---

## 2. Evidence Registry

### 2.1 Authorized Evidence

| Source | Path | Content | Status |
|--------|------|---------|--------|
| Google Sheet 202604 | `real_import/sheet_202604.csv` | 154 rows, columns: 屋主,地點,房號,姓名,電話,起租,到約,租金,電費,水費,管理費,其他,應繳,已繳,本月差額,轉帳帳號,轉入帳號,入帳時間 | Confirmed |
| Google Sheet 202605 | `real_import/sheet_202605.csv` | 154 rows, columns: 屋主,地點,房號,姓名,電話,起租,到約,租金,電費,水費,管理費,其他,未收款,應繳,已繳,本月差額,轉帳帳號,轉入帳號,入帳時間,通知,帳單,計算,備註 | Confirmed |
| Existing monthly bills | `runtime-real.db` → `monthly_bills` table | Batch 1 (191 bills) + Batch 2 (200 bills) | Confirmed |
| Existing contracts | `runtime-real.db` → `contracts` table | ~80 contracts (batch 1 + batch 2) | Confirmed |
| Prior reconciliation | `coordination/incidents/2026-07-12_batch2-monthly-bill-total-reconciliation.md` | 11 bills reconciled with Sheet evidence | Confirmed precedent |

### 2.2 Prohibited Evidence Sources

| Source | Reason |
|--------|--------|
| Old system `D:\rental\rental.db` | Not authorized for this backfill scope |
| Manual memory / verbal | Not verifiable |
| Any source not listed in §2.1 | Would violate evidence-only constraint |

---

## 3. Field Classification: DIRECT (可直接帶入)

These fields have unambiguous evidence in the Sheet and can be populated directly, after the mandatory gates in §5 are cleared.

### D-01: `contract_id`

**Evidence**: Sheet row → property (地點) + room (房號) → `rooms` table → `contracts` table (active contract for that room).

**Rule**: Match the Sheet row to exactly one active contract in `runtime-real.db`. The mapping chain is:
```
Sheet[地點][房號] → Room.property_id + Room.room_number → Room.id → Contract.room_id (status='active')
```

**Verification**: The contract's `tenant.name` should match Sheet's 姓名. If they differ, flag for manual review but do not block — tenant names may have changed between old and new system.

### D-02: `year_month`

**Evidence**: Fixed to `"202604"` or `"202605"` per scope.

**Rule**: Always use `YYYYMM` format. Apply `to_db_year_month()` if the input comes from UI (`YYYY-MM`).

### D-03: `rent`

**Evidence**: Sheet's 租金 column.

**Rule**: Cross-verify against `contract.rent`. If they match (±0), use the contract value. If they differ, **divert to CAUTION** — the contract rent may have changed mid-cycle.

### D-04: `electricity_amount`

**Evidence**: Sheet's 電費 column.

**Rule**: Direct carry. The old system already calculated the final electricity charge per room. Note that `electricity_prev`, `electricity_curr`, and `electricity_usage` may NOT be recoverable from the Sheet — set them to `0` and document in `notes`.

### D-05: `water_amount`

**Evidence**: Sheet's 水費 column.

**Rule**: Same as electricity — direct carry; `water_prev`, `water_curr`, `water_usage` set to `0` unless separately evidenced.

### D-06: `other_charges`

**Evidence**: Sheet's 管理費 + 其他 columns, summed.

**Rule**: `other_charges = 管理費 + 其他`. If 其他 is non-numeric or text, set `other_charges` to just 管理費 and put the text in `other_desc`.

### D-07: `other_desc`

**Evidence**: Sheet's 其他 column when it contains descriptive text.

**Rule**: Truncate to 200 characters (DB column limit). Empty string → `None`.

### D-08: `notes`

**Evidence**: N/A (synthetic).

**Rule**: Always set to `"歷史回填 — Google Sheet 202604"` or `"歷史回填 — Google Sheet 202605"` plus the Sheet row number for traceability. Example: `"歷史回填 — Google Sheet 202604 row 5"`.

---

## 4. Field Classification: CAUTION (需 stop condition)

These fields require a specific gate to pass before they can be populated. If the gate fails, the executor must **stop** and flag for manual resolution.

### C-01: `previous_balance` (HIGH RISK)

**Evidence for 202605**: Sheet's 未收款 column (present in 202605 tab header).

**Evidence for 202604**: The 202604 Sheet tab does NOT have a 未收款 column. The 本月差額 column is `應繳 − 已繳` (this month's difference), NOT the carried-forward previous_balance.

**Stop conditions**:

| Condition | Action |
|-----------|--------|
| **202605 backfill**: 未收款 column exists | ✅ DIRECT carry as signed value. Positive = prior unpaid, negative = prior credit/overpayment. |
| **202604 backfill**: No 未收款 column in sheet | ⛔ **STOP** — `previous_balance` for 202604 must be sourced from 202603 (or earlier) data. If no 202603 bill exists in `runtime-real.db`, set `previous_balance = 0` and document in notes: `"前期差額無證據，設為0"`. If evidence exists, manually verify. |
| Any: `previous_balance` is negative | ⚠️ **CAUTION** — Negative previous_balance means a credit/overpayment carried forward. Verify sign convention: the Sheet's 未收款 negative means the tenant overpaid. Must match the signed convention in `calculate_total()`. |
| Any: `previous_balance` does not reconcile with prior month's 本月差額 | ⛔ **STOP** — Chain verification: 202605.未收款 should ≈ 202604.本月差額 for the same contract. If they differ by >10, flag for manual investigation. |

**Precedent**: The 2026-07-12 incident confirmed signed `previous_balance` with both positive (欠款) and negative (溢繳) values, all verified against the Sheet.

### C-02: `total` (MUST BE CALCULATED)

**Evidence**: The Sheet's 應繳 column is **reference only**, not authoritative.

**Rule**: After populating all component fields, recalculate:
```
total = rent + electricity_amount + public_electricity + water_amount + other_charges + previous_balance
```
using `MonthlyBill.calculate_total()`.

**Stop conditions**:

| Condition | Action |
|-----------|--------|
| Calculated `total` == Sheet's 應繳 (±0) | ✅ Pass — proceed |
| Calculated `total` ≠ Sheet's 應繳 (diff ≤ 10) | ⚠️ **CAUTION** — Small rounding difference. Accept calculated total, document diff in notes. |
| Calculated `total` ≠ Sheet's 應繳 (diff > 10) | ⛔ **STOP** — Material discrepancy. The component breakdown may be wrong, or the Sheet may have hidden charges. Flag for manual investigation. Do NOT overwrite with Sheet value. |

### C-03: `electricity_prev`, `electricity_curr`, `electricity_usage`

**Evidence**: NOT in the Sheet. The Sheet only provides the final 電費 amount.

**Stop conditions**:

| Condition | Action |
|-----------|--------|
| Old system has meter readings for this contract+month | ⚠️ **CAUTION** — If `electricity_readings` exist in old system, manually transcribe. Otherwise set all three to `0`. |
| No meter data available | ✅ Set to `0`, document in notes: `"僅有電費總額，無電表讀數"`. |

**Rationale**: The data contract audit (`reasonix-data-contract-audit.md`) confirms that `electricity_prev`/`electricity_curr`/`electricity_usage` are optional detail fields. The authoritative field is `electricity_amount`.

### C-04: `water_prev`, `water_curr`, `water_usage`

**Same rule as C-03** — set to `0` if no meter evidence, document in notes.

### C-05: `public_electricity`

**Evidence**: The Sheet may bundle public area electricity into the 電費 column. No separate column exists in the Sheet.

**Stop conditions**:

| Condition | Action |
|-----------|--------|
| Property has known `public_amount` in old system `electricity_bills` | ⚠️ **CAUTION** — Cross-reference old system. If found, split from electricity_amount. |
| No evidence of separate public electricity | ✅ Set `public_electricity = 0`. The bundled amount stays in `electricity_amount`. |

**Precedent**: PID 5 (宣化62號4樓) has `public_amount` of 31–32 in old system `electricity_bills`. For properties without such evidence, keep `public_electricity = 0`.

### C-06: Duplicate Check (contract_id + year_month)

**Rule**: Before every insert, check `BillingRepository.find_by_contract_and_month(contract_id, year_month)`.

**Stop conditions**:

| Condition | Action |
|-----------|--------|
| No existing bill | ✅ Proceed |
| Existing bill found | ⛔ **STOP** — Skip this row. A bill for (contract_id, year_month) already exists. Do NOT overwrite unless explicitly authorized with evidence that the existing bill is wrong. |

### C-07: Contract Status Gate

**Rule**: Only backfill bills for contracts with `status = 'active'` (or that were active during the target month).

**Stop conditions**:

| Condition | Action |
|-----------|--------|
| Contract is `active` and `start_date ≤ month_end AND end_date ≥ month_start` | ✅ Proceed |
| Contract is `terminated` | ⛔ **STOP** — Do not create bills for terminated contracts unless they were active during the target month. |
| Contract has `rent = 0` | ⚠️ **CAUTION** — May be a placeholder contract for a vacant room. Verify tenant exists and is not a virtual tenant (待修, 空房, 倉庫). |

### C-08: Vacant / Virtual Tenant Filter

**Evidence**: The Sheet contains rows for vacant rooms and rooms under repair (待修, 空房, 倉庫, 鐵皮, 浴室). These rows typically have 應繳 = 0 or only management fees.

**Stop conditions**:

| Condition | Action |
|-----------|--------|
| Sheet's 姓名 is empty OR contains 待修/空房/倉庫/鐵皮/浴室 | ⛔ **STOP** — Skip this row. These are not real tenant bills. |
| Sheet's 姓名 is a real name AND 應繳 > 0 | ✅ Proceed |
| Sheet's 姓名 is a real name AND 應繳 = 0 AND 租金 = 0 | ⚠️ **CAUTION** — May be an electricity-only placeholder. Check old system for context. |

### C-09: Rent Mismatch Between Sheet and Contract

**Stop conditions**:

| Condition | Action |
|-----------|--------|
| Sheet's 租金 == contract.rent | ✅ Use contract.rent |
| Sheet's 租金 ≠ contract.rent (diff ≤ 100) | ⚠️ **CAUTION** — Small variance may be rounding or rate adjustment. Use contract.rent, note diff. |
| Sheet's 租金 ≠ contract.rent (diff > 100) | ⛔ **STOP** — Material difference. The contract may have been updated since the Sheet was created, or the Sheet row maps to the wrong contract. Flag for manual verification. |

---

## 5. Field Classification: FORBIDDEN (禁止自動處理)

These fields must **never** be set during backfill. Violating any of these is a contract breach.

### F-01: `paid` (BOOLEAN)

**Reason**: The `paid` flag must be controlled by payment reconciliation through `PaymentRecord`, not derived from the Sheet's 已繳 column.

**Sheet evidence**: The 已繳 column shows how much was paid, but this does NOT mean `paid = True`. A bill can have partial payment (已繳 < 應繳) or overpayment (已繳 > 應繳).

**Correct approach**: After creating the MonthlyBill, if 已繳 > 0 in the Sheet, create a separate `PaymentRecord` (see §7). The `paid` flag should be set to `True` only when linked PaymentRecords cover the total.

**Precedent**: The 2026-07-12 incident created 11 PaymentRecords separately from the bills. Bills 170, 171, 578, 831, 832 remain with `paid=False` despite having payments, because payment coverage is partial.

### F-02: `paid_date`

**Reason**: Can only be set when `paid` transitions to `True`. Must be derived from PaymentRecord's `transaction_date`, not the Sheet's 入帳時間.

### F-03: Direct `total` Overwrite

**Reason**: The `total` field must be calculated by `BillingService.calculate_total()`. Never copy the Sheet's 應繳 value directly into `total`. The formula is the single source of truth.

### F-04: `id` Override

**Reason**: Let SQLite auto-increment. Never specify `id` manually.

### F-05: Any Schema or Code Change

**Reason**: Task constraint. Modifying `app/`, `scripts/`, `tests/`, or any database schema is strictly prohibited. The backfill is a data-only operation.

---

## 6. PaymentRecord Separation Protocol

When the Sheet shows 已繳 > 0, a `PaymentRecord` must be created as a **separate, independent** step after the `MonthlyBill` is created. The two entities must never be conflated.

### 6.1 PaymentRecord Creation Rules

| Field | Source | Rule |
|-------|--------|------|
| `contract_id` | Same as MonthlyBill | Direct |
| `monthly_bill_id` | The newly created bill's `id` | Link after both exist |
| `amount` | Sheet's 已繳 | Direct (signed positive) |
| `payer_name` | Sheet's 姓名 | Direct |
| `transaction_date` | Sheet's 入帳時間 | Parse from Sheet; `NULL` if empty or unparseable |
| `bank_name` | Sheet's 轉入帳號 (inferred) | Set to `NULL` if no bank evidence |
| `account_number` | Sheet's 轉帳帳號 | Direct |
| `record_status` | Fixed: `'linked'` | Already linked to a bill |
| `transaction_id` | Synthetic: `legacy-sheet-YYYYMM-rowN-billID` | Idempotency key — prevents duplicate PaymentRecords on re-run |
| `notes` | `"歷史回填 — Google Sheet YYYYMM row N"` | Traceability |

### 6.2 Idempotency Gate

Before creating a PaymentRecord, check:
```python
PaymentRecord.query.filter_by(transaction_id=f"legacy-sheet-{year_month}-row{row_n}-{bill_id}").first()
```
If found, skip — the PaymentRecord already exists.

**Precedent**: The 2026-07-12 incident used `legacy-sheet-YYYYMM-rowN-billID` format and confirmed idempotency on re-run.

### 6.3 Partial Payment Handling

If `已繳 < total`, the bill remains `paid = False`. The PaymentRecord captures the partial amount. The remaining balance is carried forward via `previous_balance` in the next month's bill (already handled by the Sheet's 未收款 column for 202605; for 202604, see C-01).

---

## 7. Duplicate Prevention Protocol

### 7.1 Pre-Insert Check

For every candidate (contract_id, year_month):
```
existing = BillingRepository.find_by_contract_and_month(contract_id, year_month)
if existing:
    skip with log: "SKIP: bill {existing.id} already exists for contract {contract_id} month {year_month}"
```

### 7.2 Idempotency Design

The entire backfill operation must be idempotent:
- Running it twice must produce zero new rows
- The duplicate check (§7.1) is the primary gate
- For PaymentRecords, the `transaction_id` synthetic key (§6.2) provides secondary idempotency

---

## 8. Verification Checklist (Post-Backfill)

Before declaring the backfill complete, verify every item:

| # | Check | Method | Expected |
|---|-------|--------|----------|
| V1 | No duplicate (contract_id, year_month) | `SELECT contract_id, year_month, COUNT(*) FROM monthly_bills GROUP BY 1,2 HAVING COUNT(*) > 1` | 0 rows |
| V2 | Every new bill's `total` matches formula | Recalculate each bill with `calculate_total()` | All match within ±1 |
| V3 | `year_month` format is `YYYYMM` | `SELECT DISTINCT length(year_month) FROM monthly_bills WHERE year_month IN ('202604','202605')` | All = 6 |
| V4 | No `previous_balance` gaps for 202605 | For each 202605 bill, verify `previous_balance` ≈ prior month's `本月差額` from Sheet | Within ±10 |
| V5 | No `paid = True` without PaymentRecord coverage | `SELECT id FROM monthly_bills WHERE paid=1 AND year_month IN ('202604','202605') AND id NOT IN (SELECT monthly_bill_id FROM payment_records)` | 0 rows |
| V6 | PaymentRecord `transaction_id` uniqueness | `SELECT transaction_id, COUNT(*) FROM payment_records WHERE transaction_id LIKE 'legacy-sheet-%' GROUP BY 1 HAVING COUNT(*) > 1` | 0 rows |
| V7 | No bills for vacant/virtual-tenant rooms | Spot-check: every new bill's contract has a real tenant (name ≠ 待修/空房/倉庫) | All pass |
| V8 | Row count matches scope | Count new bills created | 27 for 202604, 1 for 202605 |
| V9 | All tests still pass | `pytest tests/integration -q` | 110+ passed |
| V10 | No app/scripts/tests/DB schema modified | `git diff --stat` | Only `docs/` and `coordination/` changed |

---

## 9. Execution Order (Mandatory Sequence)

The executor must follow this exact order. Each step gates on the previous:

```
1. BACKUP: Copy runtime-real.db to backups/runtime_YYYYMMDD_HHMMSS.db
2. IDENTIFY: Map all 28 Sheet rows to contract_ids (see Appx A)
3. GATE: For each candidate, run all CAUTION stop conditions (§4)
4. RESOLVE: Any STOP → flag, document, skip. Any CAUTION → resolve or escalate.
5. INSERT: Create MonthlyBill rows for all cleared candidates
6. RECALCULATE: Run calculate_total() on every new bill
7. PAYMENT: Create PaymentRecord rows for 已繳 > 0 entries (§6)
8. VERIFY: Run all 10 checks in §8
9. REPORT: Update coordination files with results
10. COMMIT: git add, commit, push
```

---

## 10. Blocker Summary

| Blocker | Severity | Condition |
|---------|----------|-----------|
| B1: Missing previous_balance evidence for 202604 | HIGH | No 未收款 column in sheet_202604.csv. Must resolve per C-01 before proceeding. |
| B2: Rent mismatch >100 | MEDIUM | Any contract where Sheet rent ≠ DB rent by >100 must be manually verified. |
| B3: Total reconciliation failure | HIGH | Any bill where calculated total ≠ Sheet 應繳 by >10 must be investigated. |
| B4: Duplicate bill exists | LOW | Skip the row; no action needed. |
| B5: Contract not found for Sheet row | HIGH | The Sheet row cannot be mapped to any active contract in runtime-real.db. |
| B6: Virtual tenant in Sheet row | LOW | Skip; these are not real bills. |

---

## Appendix A: Sheet Column Mapping Reference

### sheet_202604.csv
| Sheet Column | MonthlyBill Field | Classification |
|-------------|-------------------|----------------|
| 屋主 (landlord) | — (for mapping only) | — |
| 地點 (property) | → Room → Contract | Mapping key |
| 房號 (room) | → Room → Contract | Mapping key |
| 姓名 (tenant) | — (cross-verify only) | CAUTION |
| 租金 | `rent` | DIRECT (cross-verify with contract) |
| 電費 | `electricity_amount` | DIRECT |
| 水費 | `water_amount` | DIRECT |
| 管理費 | `other_charges` (+) | DIRECT |
| 其他 | `other_charges` (+) / `other_desc` | DIRECT |
| 應繳 | — (reference for total verification) | CAUTION |
| 已繳 | — (→ PaymentRecord) | FORBIDDEN for paid flag |
| 本月差額 | — (NOT previous_balance; this is (應繳−已繳)) | CAUTION |
| 入帳時間 | — (→ PaymentRecord.transaction_date) | FORBIDDEN for paid_date |

### sheet_202605.csv
| Sheet Column | MonthlyBill Field | Classification |
|-------------|-------------------|----------------|
| (all columns same as 202604, plus:) | | |
| 未收款 | `previous_balance` | DIRECT (signed) |

## Appendix B: `calculate_total` Reference

From `app/models/billing.py:32-44`:
```python
@staticmethod
def calculate_total(*, rent=0, electricity_amount=0, public_electricity=0,
                    water_amount=0, other_charges=0, previous_balance=0):
    total = (
        Decimal(str(rent or 0))
        + Decimal(str(electricity_amount or 0))
        + Decimal(str(public_electricity or 0))
        + Decimal(str(water_amount or 0))
        + Decimal(str(other_charges or 0))
        + Decimal(str(previous_balance or 0))
    )
    return total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
---

## Deliverables Checklist

- ✅ This file: `docs/reports/reasonix-missing-monthly-bills-guard-01.md`
- ⬜ `coordination/progress/reasonix.md` — updated with current task
- ⬜ `coordination/completed/reasonix.md` — updated with completion entry
