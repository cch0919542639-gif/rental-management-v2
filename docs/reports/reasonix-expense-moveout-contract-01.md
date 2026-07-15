# R3 PropertyExpense + R6 MoveOutSettlement — Frozen Contract Decision Package

Date: 2026-07-15
Author: reasonix
Branch: `agent/reasonix-expense-moveout-contract-01`
Baseline: `codex-phase2-mainline-01`
Purpose: 凍結 R3 PropertyExpense 與 R6 MoveOutSettlement 的資料契約決策包。不寫程式。
Precursor: `docs/reports/reasonix-reporting-expansion-contract-01.md`

---

## 1. R3 PropertyExpense — Minimum Fields

`PropertyExpense` is a property-level operating-expense ledger. One row = one financial fact.
It must never be stored in `MonthlyBill.other_charges`.

| # | Field | SQLAlchemy Type | Nullable | Default | Index | Note |
|---|-------|----------------|----------|---------|-------|------|
| 1 | `id` | Integer, PK | NO | auto | — | — |
| 2 | `property_id` | Integer, FK→properties.id | NO | — | YES | `ON DELETE RESTRICT` |
| 3 | `transaction_date` | Date | NO | — | YES | `year_month` derived via `to_db_year_month()` from this |
| 4 | `category` | String(30) | NO | — | YES | Controlled set: `management_fee`, `cleaning`, `repair`, `utility`, `tax`, `insurance`, `supplies`, `other` |
| 5 | `amount` | Numeric(10,2) | NO | — | — | Must be > 0 for `posted` rows |
| 6 | `payee` | String(100) | YES | NULL | — | Counterparty name |
| 7 | `reference_no` | String(100) | YES | NULL | — | External receipt/invoice/transfer reference |
| 8 | `notes` | Text | YES | NULL | — | Human explanation only; not a rules field |
| 9 | `record_status` | String(20) | NO | `draft` | YES | See §2 state machine |
| 10 | `created_by_id` | Integer, FK→user.id | YES | NULL | — | `ON DELETE SET NULL` |
| 11 | `voided_at` | DateTime | YES | NULL | — | Mandatory when `record_status='voided'` |
| 12 | `void_reason` | String(200) | YES | NULL | — | Mandatory when `record_status='voided'` |
| 13 | `created_at` | DateTime | NO | func.now() | — | Via TimestampMixin |
| 14 | `updated_at` | DateTime | NO | func.now() onupdate | — | Model-level; TimestampMixin lacks this, add explicitly |

Table name: `property_expenses`

### 1.1 Category Enum

```python
EXPENSE_CATEGORIES = {
    "management_fee",  # 管理費
    "cleaning",        # 清潔費（property-level）
    "repair",          # 維修費（property-level; distinct from tenant-liable repair_fee in R6）
    "utility",         # 公用事業（公共電費、公共水費）
    "tax",             # 稅金（房屋稅、地價稅）
    "insurance",       # 保險（火險、地震險）
    "supplies",        # 耗材/備品
    "other",           # 其他（需在 notes 說明）
}
```

Free-text categories are forbidden. The service layer must reject any value outside this set.

### 1.2 year_month Derivation

`year_month` is derived from `transaction_date` using the shared `to_db_year_month()` helper.
Do not store an independent `year_month` column. Report queries derive the period:
```sql
WHERE strftime('%Y%m', transaction_date) = :year_month
```

---

## 2. R3 PropertyExpense — State Machine

```
         ┌──────────┐
         │  draft   │
         └────┬─────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         │
┌──────┐  ┌───────────┐ │
│posted│  │ cancelled  │◄┘
└──┬───┘  └───────────┘
   │
   ▼
┌──────┐
│voided│
└──────┘
```

| From | To | Allowed | Condition |
|------|----|---------|-----------|
| `draft` | `posted` | ✅ | `amount > 0`, `transaction_date` non-null, `category` valid |
| `draft` | `cancelled` | ✅ | No condition |
| `posted` | `voided` | ✅ | `void_reason` and `voided_at` required |
| `posted` | `draft` | ❌ | Forbidden — no reversal |
| `posted` | `cancelled` | ❌ | Forbidden — use void |
| `voided` | any | ❌ | Forbidden — terminal state |
| `cancelled` | any | ❌ | Forbidden — terminal state |

State semantics:
- **draft**: Editable. Not included in expense totals. May be deleted physically.
- **posted**: Immutable financial fact. Included in R3 report totals. Never physically deleted.
- **voided**: Excluded from normal totals. Preserves original amount, date, property, audit trail. `void_reason` and `voided_at` mandatory.
- **cancelled**: An unposted draft abandoned without accounting effect. May be physically deleted.

Classification: **DIRECT**

---

## 3. R3 PropertyExpense — Amount Formulas

| Formula | Rule |
|---------|------|
| R3 report total | `SUM(amount) WHERE record_status = 'posted' AND strftime('%Y%m', transaction_date) IN range` |
| R3 category subtotal | `SUM(amount) WHERE record_status = 'posted' AND category = :cat AND year_month IN range` |

Explicit prohibitions:
- R3 totals are never inferred from `MonthlyBill.other_charges`.
- Route/template must never calculate expense sums directly; they call the repository or service.

Classification: **DIRECT**

---

## 4. R3 PropertyExpense — FK / ON DELETE / Immutability

### FK Rules

| FK Column | ON DELETE | Rationale |
|-----------|-----------|-----------|
| `property_id` | `RESTRICT` | Cannot delete a property that has any expense history |
| `created_by_id` | `SET NULL` | Deleting a user must not erase financial audit trail |

### Cascade Rules
- No cascade delete from `properties`, `landlords`, `rooms`, `contracts`, or `monthly_bills` into `property_expenses`.
- Physical deletion of a `posted` or `voided` expense is forbidden at any layer (DB, ORM, service, UI).
- Only `draft` and `cancelled` rows may be physically deleted.

### Immutability Rules
A `posted` expense row is immutable for these fields:
- `amount`
- `transaction_date`
- `category`
- `property_id`

A correction to a `posted` row must be: void the original + create a new compensating row.
In-place edits to a `posted` row's financial fields must be rejected by the service layer.

Classification: **DIRECT**

---

## 5. R6 MoveOutSettlement — Minimum Fields

`MoveOutSettlement` records one contract's final financial close-out. It is separate from
`Contract`, `MonthlyBill`, and `PaymentRecord` so that final charges and deposit handling
do not mutate historical monthly bill totals.

| # | Field | SQLAlchemy Type | Nullable | Default | Index | Note |
|---|-------|----------------|----------|---------|-------|------|
| 1 | `id` | Integer, PK | NO | auto | — | — |
| 2 | `contract_id` | Integer, FK→contracts.id | NO | — | YES | `ON DELETE RESTRICT`; app-level: one non-voided settlement per contract |
| 3 | `final_monthly_bill_id` | Integer, FK→monthly_bills.id | YES | NULL | — | `ON DELETE RESTRICT` when set; required before finalization if a final bill exists |
| 4 | `move_out_date` | Date | YES | NULL | — | Required for finalization |
| 5 | `finalized_date` | DateTime | YES | NULL | — | Set on transition to `finalized` |
| 6 | `final_rent` | Numeric(10,2) | NO | 0 | — | Non-negative |
| 7 | `electricity_amount` | Numeric(10,2) | NO | 0 | — | Non-negative |
| 8 | `water_amount` | Numeric(10,2) | NO | 0 | — | Non-negative |
| 9 | `management_fee` | Numeric(10,2) | NO | 0 | — | Non-negative; see §9 boundary |
| 10 | `previous_debt` | Numeric(10,2) | NO | 0 | — | Non-negative; unpaid balance carried into settlement |
| 11 | `cleaning_fee` | Numeric(10,2) | NO | 0 | — | Non-negative; tenant-liable cleaning |
| 12 | `repair_fee` | Numeric(10,2) | NO | 0 | — | Non-negative; tenant-liable repair charge |
| 13 | `other_charge` | Numeric(10,2) | NO | 0 | — | Non-negative |
| 14 | `other_desc` | String(200) | YES | NULL | — | Mandatory when `other_charge > 0` |
| 15 | `deposit_held` | Numeric(10,2) | NO | 0 | — | Snapshot of `contract.deposit` at finalization time |
| 16 | `deposit_applied` | Numeric(10,2) | NO | 0 | — | Amount of held deposit applied to charges |
| 17 | `refund_amount` | Numeric(10,2) | NO | 0 | — | Deposit return due; non-negative |
| 18 | `paid_amount` | Numeric(10,2) | NO | 0 | — | Settlement payment; see ADR-R05 |
| 19 | `gross_charges` | Numeric(10,2) | NO | 0 | — | Service-derived (never route-set) |
| 20 | `outstanding_amount` | Numeric(10,2) | NO | 0 | — | Service-derived (never route-set) |
| 21 | `status` | String(20) | NO | `draft` | YES | See §6 state machine |
| 22 | `notes` | Text | YES | NULL | — | Operational explanation |
| 23 | `created_by_id` | Integer, FK→user.id | YES | NULL | — | `ON DELETE SET NULL` |
| 24 | `created_at` | DateTime | NO | func.now() | — | Via TimestampMixin |
| 25 | `updated_at` | DateTime | NO | func.now() onupdate | — | Model-level |

Table name: `move_out_settlements`

Property, room, and tenant are obtained by joining `contracts`. Do not add copied
foreign keys (`room_id`, `tenant_id`, `property_id`) to the settlement row.
Duplicate references can drift from the contract's formal relationship.

Classification: **DIRECT** for schema and draft/finalized. **ADR_REQUIRED** for `closed` status.

---

## 6. R6 MoveOutSettlement — State Machine

```
         ┌──────────┐
         │  draft   │
         └────┬─────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         │
┌─────────┐ ┌───────────┐│
│finalized│ │ cancelled │◄┘
└────┬────┘ └───────────┘
     │
     ├──────────┐
     ▼          ▼
  ┌──────┐  ┌──────┐
  │closed│  │voided│
  └──────┘  └──────┘
```

| From | To | Allowed | Condition |
|------|----|---------|-----------|
| `draft` | `finalized` | ✅ | `move_out_date` non-null, all charge components ≥ 0, deposit snapshot captured |
| `draft` | `cancelled` | ✅ | No condition |
| `finalized` | `closed` | ✅ (ADR-gated) | `outstanding_amount = 0`, ADR-R04 and ADR-R05 resolved |
| `finalized` | `voided` | ✅ | `void_reason` required; replacement settlement may exist |
| `finalized` | `draft` | ❌ | Forbidden — no reopening |
| `closed` | any | ❌ | Forbidden — terminal state |
| `voided` | any | ❌ | Forbidden — terminal state |
| `cancelled` | any | ❌ | Forbidden — terminal state |

State semantics:
- **draft**: Components editable. No reporting or collection effect. May be physically deleted.
- **finalized**: Components and deposit snapshot immutable. `outstanding_amount` may still be non-zero. Visible in R6 reports.
- **closed**: `outstanding_amount = 0`. Refund recorded. Terminal.
- **cancelled**: Abandoned draft. May be physically deleted.
- **voided**: Finalized record invalidated. Must have reason and optional replacement reference.

Crucially: creating or finalizing a settlement must not implicitly change `Contract.status`.
Contract termination remains an explicit contracts workflow action.

Classification: **DIRECT** for draft↔finalized. **ADR_REQUIRED** for `closed` transition (blocked by ADR-R04, ADR-R05).

---

## 7. R6 MoveOutSettlement — Amount Formulas

All formulas are enforced by the settlement service. Routes must never calculate these directly.

### 7.1 gross_charges

```
gross_charges = final_rent
              + electricity_amount
              + water_amount
              + management_fee
              + previous_debt
              + cleaning_fee
              + repair_fee
              + other_charge
```

### 7.2 settlement_due

```
settlement_due = gross_charges - deposit_applied
```

### 7.3 outstanding_amount

```
outstanding_amount = max(settlement_due - paid_amount, 0)
```

`outstanding_amount` can never be negative. Overpayment scenarios require manual handling or ADR.

### 7.4 Constraints

| Constraint | Enforcement |
|------------|-------------|
| All charge components ≥ 0 | Service on save/finalize |
| `0 ≤ deposit_applied ≤ deposit_held` | Service on save/finalize |
| `deposit_applied ≤ gross_charges` | Service on finalize |
| `refund_amount ≥ 0` | Service on save/finalize |
| `refund_amount ≤ deposit_held - deposit_applied` | Service (unless Owner-approved external refund policy exists) |
| `other_charge > 0 → other_desc` mandatory | Service on save |
| `gross_charges`, `outstanding_amount` never set by route | Architecture rule |
| Finalized settlement does not mutate `MonthlyBill.total` | Architecture rule |
| Finalized settlement does not mutate `PaymentRecord.amount` | Architecture rule |
| Finalized settlement does not mutate `Contract.rent` or `Contract.deposit` | Architecture rule |
| Finalized settlement does not mutate `Contract.status` | Architecture rule |

### 7.5 Rounding

All amounts follow the system's existing whole-dollar rounding policy (`ROUND_HALF_UP` to integer).
The settlement service must use the same `Decimal` quantization as `MonthlyBill.calculate_total()`.

Classification: **DIRECT** for formulas and constraints. **ADR_REQUIRED** for `paid_amount` derivation (ADR-R05).

---

## 8. R6 MoveOutSettlement — FK / ON DELETE / Immutability

### FK Rules

| FK Column | ON DELETE | Rationale |
|-----------|-----------|-----------|
| `contract_id` | `RESTRICT` | Financial close-out must survive any attempted contract cleanup |
| `final_monthly_bill_id` | `RESTRICT` | Cannot delete a bill linked by a finalized/closed settlement (when non-null) |
| `created_by_id` | `SET NULL` | Deleting a user must not erase financial history |

### Cascade Rules
- No cascade deletion from `contracts`, `rooms`, `tenants`, `properties`, `monthly_bills`, or `payment_records` into `move_out_settlements`.
- Physical deletion of a `finalized`, `closed`, or `voided` settlement is forbidden at every layer.
- Only `draft` and `cancelled` settlements may be physically deleted.

### Immutability Rules
A `finalized` settlement is immutable for these fields:
- All charge components (`final_rent`, `electricity_amount`, `water_amount`, `management_fee`, `previous_debt`, `cleaning_fee`, `repair_fee`, `other_charge`)
- `deposit_held`, `deposit_applied`
- `gross_charges`, `outstanding_amount`
- `move_out_date`
- `contract_id`

A correction after finalization = void + new settlement row.

Classification: **DIRECT**

---

## 9. Boundary Definitions

Explicit ownership for each financial concept crossing R3 and R6:

| Concept | Primary Home | Can Also Appear In | Forbidden Home |
|---------|-------------|-------------------|----------------|
| Management fee | `MoveOutSettlement.management_fee` (tenant charge) | `PropertyExpense.category='management_fee'` (owner-side tracking) per ADR-R08 | `MonthlyBill.other_charges` |
| Cleaning fee (property) | `PropertyExpense.category='cleaning'` (owner operating expense) | — | `MonthlyBill.other_charges` |
| Cleaning fee (tenant-liable) | `MoveOutSettlement.cleaning_fee` | — | `MonthlyBill.other_charges`, `Room.status` |
| Repair cost (property) | `PropertyExpense.category='repair'` | `MaintenanceRequest.actual_cost` (operational record) | One receipt must not be double-counted across both |
| Repair fee (tenant-liable) | `MoveOutSettlement.repair_fee` | — | Must not be inferred from `MaintenanceRequest.actual_cost` without Owner rule |
| Arrears / previous debt | `MoveOutSettlement.previous_debt` | Derived from unpaid `MonthlyBill` rows verified against `PaymentRecord` linkage | `MonthlyBill.paid=false` alone is insufficient |
| Deposit offset | `MoveOutSettlement.deposit_applied` | — | Never silently deducted from `MonthlyBill` |
| Deposit refund | `MoveOutSettlement.refund_amount` | — | Never a negative `PaymentRecord` or negative settlement charge |
| Settlement payment | `MoveOutSettlement.paid_amount` | — | Requires ADR-R05 for `PaymentRecord` linkage |

---

## 10. Owner Must-Answer Decisions (ADR-R01 ~ ADR-R08)

| ID | Decision | Safe Default | Alternative | Consequence of Default | Consequence of Delay |
|----|----------|-------------|-------------|----------------------|---------------------|
| **ADR-R01** | Cash vs accrued basis for `PropertyExpense` | **Cash basis**: `transaction_date` = payment date | Accrued: `transaction_date` = incurred date, separate payment date | Simpler; single date per row works for all reports | Dual-date reporting blocked; acceptable for v1 |
| **ADR-R02** | Expense approval workflow | **Single-step post**: draft → posted (no reviewer) | Two-step: draft → pending → posted (reviewer required) | Simpler and lower friction; irreversible once posted | If reviewer is needed later, all posted rows lack reviewer audit |
| **ADR-R03** | Cross-property expense allocation | **No allocation**: one expense = one property; split manually | Automatic split by room count or area | Simpler; multi-property receipts entered as separate rows | Multi-property receipts slightly more manual work |
| **ADR-R04** | Deposit refund evidence | **Manual entry**: `refund_amount` + `notes`/`reference_no` only | Linked refund `PaymentRecord` or separate refund table | Quick to implement; no PaymentRecord dependency | ⚠️ **BLOCKS R6 `closed`** — cannot certify refund without evidence rule |
| **ADR-R05** | Settlement payment allocation | **Manual `paid_amount`**: entered directly, no PaymentRecord linkage | Extend `PaymentRecord` with `settlement_id` FK | Quick to implement; settlement payment tracked independently | ⚠️ **BLOCKS R6 `closed`** — cannot reconcile settlement payment without allocation rule |
| **ADR-R06** | Finalize before contract termination | **Allowed**: settlement can finalize while contract is `active` | Forbidden: must terminate contract first | Flexible; supports pre-move-out preparation | Delay blocks move-out workflow for pre-termination cases |
| **ADR-R07** | Historical display snapshots | **Live join**: always show current names/room labels | Snapshot at finalization: denormalize names into settlement row | Simpler schema; display may drift if names change after finalization | Snapshot fields not added; acceptable risk for v1 |
| **ADR-R08** | Management fee policy | **Tenant charge only**: `management_fee` in `MoveOutSettlement` only | Dual: also a `PropertyExpense` category for owner-side tracking | Simpler; management fee appears only on settlement, not on property P&L | Property-level management fee tracking blocked |

### Blocking Status

- **ADR-R04** and **ADR-R05** are the **only two** decisions that block R6 `closed` status.
- All other ADRs can be deferred: R3 and R6 draft/finalized work can proceed with the safe defaults.
- R3 `PropertyExpense` has **zero blocking ADRs**: all DIRECT items are immediately implementable.

---

## 11. DIRECT / ADR_REQUIRED / FORBIDDEN Classification

### DIRECT — Implementable Immediately After Contract Acceptance

| Item | Domain |
|------|--------|
| `PropertyExpense` model, table `property_expenses`, all 14 columns | R3 |
| `PropertyExpense` state machine: draft → posted → voided, draft → cancelled | R3 |
| `PropertyExpense` category enum validation | R3 |
| `PropertyExpense` amount > 0 for posted rows | R3 |
| `PropertyExpense` year_month derivation from `transaction_date` | R3 |
| `PropertyExpense` FK rules (RESTRICT, SET NULL) | R3 |
| `PropertyExpense` immutability: posted rows cannot be mutated or hard-deleted | R3 |
| `PropertyExpense` repository: CRUD + list_by_property + list_by_month | R3 |
| `PropertyExpense` service: create, update (draft only), post, void, cancel | R3 |
| `PropertyExpense` report: R3 property expense detail (read-only query) | R3 |
| `MoveOutSettlement` model, table `move_out_settlements`, all 25 columns | R6 |
| `MoveOutSettlement` state machine: draft → finalized, draft → cancelled, finalized → voided | R6 |
| `MoveOutSettlement` gross_charges formula (service-enforced) | R6 |
| `MoveOutSettlement` deposit_applied constraint: 0 ≤ applied ≤ held ≤ gross | R6 |
| `MoveOutSettlement` outstanding_amount formula: max(due - paid, 0) | R6 |
| `MoveOutSettlement` other_desc mandatory when other_charge > 0 | R6 |
| `MoveOutSettlement` FK rules (RESTRICT, SET NULL) | R6 |
| `MoveOutSettlement` immutability: finalized rows cannot be mutated or hard-deleted | R6 |
| `MoveOutSettlement` repository: CRUD + list_by_contract | R6 |
| `MoveOutSettlement` service: create, update (draft only), finalize, void, cancel | R6 |
| `MoveOutSettlement` report: R6 draft/finalized display (read-only query) | R6 |
| All FORBIDDEN rules enforced via code review gate | Cross |

### ADR_REQUIRED — Blocked Until Owner Decision

| Item | Blocking ADR | What Is Blocked |
|------|-------------|-----------------|
| `MoveOutSettlement` `closed` transition | ADR-R04, ADR-R05 | R6 payment-complete workflow |
| `paid_amount` derivation and PaymentRecord linkage | ADR-R05 | Reconciled settlement payment |
| Deposit refund evidence workflow | ADR-R04 | Certified refund proof |
| Management fee as PropertyExpense category | ADR-R08 | Owner-side P&L tracking of management fees |
| Cross-property expense allocation | ADR-R03 | Automatic multi-property receipt splitting |
| Expense approval reviewer state | ADR-R02 | Two-step approval workflow |
| Dual-date expense tracking (incurred vs paid) | ADR-R01 | Accrual-based reporting |
| Pre-termination settlement finalization | ADR-R06 | Scheduled move-out workflow |
| Historical display snapshots | ADR-R07 | Name/room label stability in finalized settlements |

### FORBIDDEN — Never, Regardless of ADR Outcome

| # | Forbidden Action | Rationale |
|---|-----------------|-----------|
| F1 | Store property operating expenses in `MonthlyBill.other_charges` | `other_charges` is a per-contract tenant charge, not a property expense ledger |
| F2 | Add `expense_status`, `settlement_status`, `cleaning_status`, `repair_status`, or `deposit_status` to `Room.status`, `Contract.status`, or `Tenant.name` | Status fields are sealed contracts; see `data_contracts/status-machines.md` |
| F3 | Mutate a `posted` expense in place (any of: amount, date, category, property_id) | Immutability is the foundation of financial audit |
| F4 | Mutate a `finalized` settlement in place (charge components, deposit, formulas) | Same audit requirement |
| F5 | Physically delete a `posted`/`voided` expense or `finalized`/`closed`/`voided` settlement | Financial history must never be erased |
| F6 | Cascade-delete expenses or settlements when a parent entity is removed | `ON DELETE RESTRICT` is the minimum; soft-archive is the maximum |
| F7 | Derive R6 payment completion from `MonthlyBill.paid=true` alone | `paid` is a boolean flag, not a reconciliation record |
| F8 | Derive R6 payment completion from free-text notes or raw OCR output | Notes and OCR are unstructured; settlement close requires structured evidence |
| F9 | Record a tenant refund as a negative `PaymentRecord` or negative settlement charge | Refunds are positive `refund_amount`, not negative amounts in other columns |
| F10 | Alter `MonthlyBill.total` during R3 or R6 generation | Reports are read-only presenters; bills are historical facts |
| F11 | Create a runtime Google Sheets dependency for settlement calculations | All calculations must be server-side, auditable, and testable |
| F12 | Allow routes to directly set `gross_charges` or `outstanding_amount` | These are service-derived fields; routes write only component fields |

---

## 12. Pre-Implementation Gate

Before any model, migration, repository, service, route, or test code is written for R3 or R6:

1. [ ] This contract document (`reasonix-expense-moveout-contract-01.md`) is reviewed and accepted by Owner/Codex.
2. [ ] ADR-R04 and ADR-R05 are resolved (required only if R6 `closed` is in the implementation scope).
3. [ ] `runtime-real.db` is backed up: `copy runtime-real.db backups\runtime_before_r3r6_YYYYMMDD_HHMMSS.db`.
4. [ ] Existing test suite passes: `pytest tests/integration -q` → 128+ passed, ≤15 skipped.
5. [ ] New migration is additive only: `CREATE TABLE property_expenses (...)` and `CREATE TABLE move_out_settlements (...)`. No column drops, no existing-table renames, no data migration of existing rows.
6. [ ] Dry-run migration executed against a copy of `runtime-real.db` and verified: `alembic upgrade head --sql` reviewed; `alembic upgrade head` on a copy succeeds.
7. [ ] Codex has read and acknowledged all 12 FORBIDDEN items (F1–F12).
8. [ ] Preliminary integration test skeleton exists (even if skipped/pending) proving the model import path works.

---

## 13. Acceptance Criteria

### 13.1 R3 PropertyExpense

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| R3-01 | `property_expenses` table exists with exactly 14 columns matching §1 | `alembic upgrade head` + schema inspect |
| R3-02 | `property_id` FK RESTRICT: deleting a property with expenses raises IntegrityError | Integration test |
| R3-03 | `created_by_id` FK SET NULL: deleting a user nullifies the FK, preserves the row | Integration test |
| R3-04 | `amount > 0` enforced at service layer for post transition | Unit test on service |
| R3-05 | `category` rejects values outside the 8-value controlled set | Unit test on service |
| R3-06 | State transitions: draft→posted, draft→cancelled, posted→voided all succeed | Integration test |
| R3-07 | Forbidden transitions: posted→draft, voided→anything, cancelled→anything all raise error | Integration test |
| R3-08 | Posted expense amount/date/category/property_id cannot be mutated in place | Integration test |
| R3-09 | Voided expense preserves original amount, date, property_id, and requires void_reason | Integration test |
| R3-10 | Physical delete of a posted or voided expense is rejected at service layer | Integration test |
| R3-11 | Physical delete of a draft or cancelled expense succeeds | Integration test |
| R3-12 | R3 report total = `SUM(amount) WHERE record_status='posted' AND strftime('%Y%m', transaction_date) IN range` | Integration test with known seed data |
| R3-13 | `pytest tests/integration -q` still passes at previous count | CI run |

### 13.2 R6 MoveOutSettlement

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| R6-01 | `move_out_settlements` table exists with exactly 25 columns matching §5 | `alembic upgrade head` + schema inspect |
| R6-02 | `contract_id` FK RESTRICT: deleting a contract with a settlement raises IntegrityError | Integration test |
| R6-03 | `final_monthly_bill_id` FK RESTRICT: deleting a linked bill raises IntegrityError | Integration test |
| R6-04 | `created_by_id` FK SET NULL: deleting a user nullifies the FK, preserves the row | Integration test |
| R6-05 | `gross_charges` = sum of all 8 charge components (service-enforced, route cannot set) | Unit test on service |
| R6-06 | `0 ≤ deposit_applied ≤ deposit_held` enforced | Unit test on service |
| R6-07 | `deposit_applied ≤ gross_charges` enforced at finalize | Unit test on service |
| R6-08 | `outstanding_amount = max(settlement_due - paid_amount, 0)`, never negative | Unit test on service |
| R6-09 | `other_charge > 0` requires `other_desc` | Unit test on service |
| R6-10 | State transitions: draft→finalized, draft→cancelled, finalized→voided all succeed | Integration test |
| R6-11 | Forbidden transitions: finalized→draft, closed→anything, voided→anything all raise error | Integration test |
| R6-12 | Finalized settlement charge components, deposit snapshot cannot be mutated in place | Integration test |
| R6-13 | Physical delete of a finalized/closed/voided settlement is rejected | Integration test |
| R6-14 | Physical delete of a draft/cancelled settlement succeeds | Integration test |
| R6-15 | Settlement operations never mutate `Contract.status` | Integration test |
| R6-16 | Settlement operations never mutate `MonthlyBill.total` or `PaymentRecord.amount` | Integration test |
| R6-17 | `closed` transition requires `outstanding_amount = 0` (if implemented) | Integration test |
| R6-18 | `pytest tests/integration -q` still passes at previous count | CI run |

---

## 14. References

- Precursor: `docs/reports/reasonix-reporting-expansion-contract-01.md`
- Status machines: `data_contracts/status-machines.md`
- Core entities: `data_contracts/core-entities.md`
- Billing contract: `data_contracts/billing-contract.md`
- Payments contract: `data_contracts/payments-contract.md`
- Reports contract: `data_contracts/reports-contract.md`
- Reporting expansion roadmap: `docs/architecture/reporting-expansion-roadmap.md`
- Phase 2 contract notes: `docs/reports/reasonix-phase2-contract-notes-01.md`
- Codex progress: `coordination/progress/codex.md`
- Existing model patterns: `app/models/billing.py` (`MonthlyBill`, `PaymentRecord`), `app/models/maintenance.py` (`MaintenanceRequest`), `app/core/db/mixins.py` (`TimestampMixin`)
