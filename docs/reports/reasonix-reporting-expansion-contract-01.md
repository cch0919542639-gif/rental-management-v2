# Reasonix Reporting Expansion Contract Review 01

## Scope And Verdict

Reviewed inputs:

- `docs/architecture/reporting-expansion-roadmap.md`
- `data_contracts/core-entities.md`
- `data_contracts/billing-contract.md`
- `data_contracts/payments-contract.md`
- `data_contracts/reports-contract.md`
- `data_contracts/status-machines.md`
- `data_contracts/migration-and-compatibility.md`

The roadmap correctly separates Phase R1 derived reports from Phase R2 financial
write domains. R1 (`Property Rent Collection Detail`, selected-property summary,
new tenant detail, annual property statistics) can be implemented as read-only
queries. R3 `PropertyExpense` and R6 `MoveOutSettlement` require new, separate
contracts before models, migrations, or write routes are started.

**Verdict:** R1 is directly implementable. R3 and R6 are implementable after the
direct contract items below are adopted; their identified Owner decisions must be
resolved before financial finalization or production migration.

## Confirmed Existing Boundaries

1. `MonthlyBill.total` is the authoritative tenant charge and is calculated by the
   billing service as rent + electricity + public electricity + water + other
   charges + previous balance, rounded with `ROUND_HALF_UP` to whole dollars.
2. `MonthlyBill` is unique per `(contract_id, year_month)`. A report must display
   its stored total, not calculate a competing total.
3. `PaymentRecord` is the only formal payment record. Its usable reconciliation
   state is `record_status=linked` with a linked `monthly_bill_id`.
4. `Contract.status` remains `active`, `expired`, or `terminated`; settlement and
   expense workflow states must not be added to that field.
5. `Room.status` remains only `vacant` or `occupied`; finance workflow must not
   alter it.
6. R1 reports are read-only presenters. They must neither create payment records
   nor update bills, contracts, rooms, or tenants.

## Direct Items: PropertyExpense Minimum Contract

### Purpose And Ownership

`PropertyExpense` is a property-level operating-expense ledger. It records one
financial fact per row. It is not a substitute for tenant charges and must never
be stored in `MonthlyBill.other_charges`, which remains a charge to one contract.

### Minimum Fields

| Field | Rule |
| --- | --- |
| `id` | Primary key. |
| `property_id` | Required FK to `properties.id`. |
| `transaction_date` | Required accounting date. Report month is derived from this date, not separately typed by UI code. |
| `category` | Required controlled value: `management_fee`, `utility`, `cleaning`, `repair`, `tax`, `insurance`, `supplies`, `other`. |
| `amount` | Required positive monetary amount, stored precisely and displayed rounded under the system policy. |
| `payee` | Optional counterparty name. |
| `reference_no` | Optional external receipt, invoice, or transfer reference. |
| `notes` | Optional human explanation; not a rules or status field. |
| `record_status` | Required controlled state defined below. |
| `created_at`, `updated_at` | Audit timestamps. |
| `created_by_id` | Recommended nullable FK to `user.id` for audit attribution. |
| `voided_at`, `void_reason` | Required when the record is voided. |

`year_month` must be derived through the shared year-month helper from
`transaction_date`. Do not store an independent month unless a later ADR establishes
an accounting-period concept and its reconciliation rule.

### State Machine

```text
draft -> posted -> voided
draft -> cancelled
```

- `draft`: editable and not included in expense totals.
- `posted`: immutable financial fact and included in report totals.
- `voided`: excluded from normal totals; requires `void_reason` and audit time.
- `cancelled`: an unposted draft abandoned without accounting effect.

Allowed transitions are only those shown. A correction to a `posted` record must
be a new compensating row or a void plus replacement, never an in-place amount edit.

### PropertyExpense Invariants

1. `amount > 0` for every `posted` row.
2. `transaction_date` is non-null for every `posted` row.
3. `category` is one of the formal values; free-text categories are forbidden.
4. Only `posted` records contribute to R3 and later net-income calculations.
5. A voided record preserves its original amount, date, property, and audit trail.
6. R3 totals are the sum of posted ledger rows in the selected date range; they are
   never inferred from `MonthlyBill.other_charges`.

### FK And Delete Rules

- `property_id` uses `ON DELETE RESTRICT`; a property with any expense history
  cannot be hard-deleted.
- `created_by_id`, if implemented, uses `ON DELETE SET NULL`; deleting a user must
  not erase financial history.
- There is no cascade delete from property, landlord, room, contract, or bill into
  an expense record.
- Physical deletion of a posted or voided expense is forbidden. The UI must expose
  only state-controlled cancellation/void actions.

## Direct Items: MoveOutSettlement Minimum Contract

### Purpose And Ownership

`MoveOutSettlement` records one contract's final financial close-out. It is separate
from `Contract`, `MonthlyBill`, and `PaymentRecord` so that final charges and deposit
handling do not mutate historical monthly bill totals.

### Minimum Fields

| Field | Rule |
| --- | --- |
| `id` | Primary key. |
| `contract_id` | Required FK to `contracts.id`; one non-voided settlement per contract. |
| `final_monthly_bill_id` | Nullable FK to the final `MonthlyBill`; required before finalization if a final monthly bill exists. |
| `move_out_date` | Required for finalization. |
| `finalized_date` | Null until finalized. |
| `final_rent` | Non-negative final-period rent charge. |
| `electricity_amount` | Non-negative final electricity charge. |
| `water_amount` | Non-negative final water charge. |
| `management_fee` | Non-negative, independent settlement component. |
| `previous_debt` | Non-negative balance carried into settlement. |
| `cleaning_fee` | Non-negative final cleaning charge. |
| `repair_fee` | Non-negative tenant-liable repair charge. |
| `other_charge`, `other_desc` | Non-negative exceptional charge and required explanation when non-zero. |
| `deposit_held` | Snapshot of the relevant contract deposit when finalized. |
| `deposit_applied` | Amount of held deposit applied to charges. |
| `refund_amount` | Actual deposit return due or paid. |
| `paid_amount` | Settlement payment amount under the Owner-approved reconciliation policy. |
| `gross_charges` | Service-derived sum of all charge components. |
| `outstanding_amount` | Service-derived unpaid settlement balance. |
| `status` | Required controlled state defined below. |
| `notes` | Optional operational explanation. |
| `created_at`, `updated_at`, `created_by_id` | Audit metadata. |

Property, room, and tenant are obtained by joining the contract. Do not add copied
foreign keys to the initial settlement row; duplicate references can drift away from
the contract's formal relationship. Historical display-name snapshots are an ADR item.

### State Machine

```text
draft -> finalized -> closed
draft -> cancelled
finalized -> voided
```

- `draft`: components may be edited; it has no reporting or collection effect.
- `finalized`: components and deposit snapshot are immutable; an outstanding amount
  may still remain.
- `closed`: finalized settlement whose outstanding balance is zero and whose required
  refund record, if any, has been recorded under the approved policy.
- `cancelled`: abandoned draft with no financial effect.
- `voided`: finalized record invalidated with a mandatory reason and replacement
  reference where applicable.

No reopening transition is allowed. A correction after finalization is a void plus a
new settlement. Creating or finalizing a settlement must not implicitly change
`Contract.status`; contract termination remains an explicit contracts workflow.

### MoveOutSettlement Invariants

1. Every charge component is non-negative.
2. `gross_charges` is calculated only by the settlement service:

   `final_rent + electricity_amount + water_amount + management_fee + previous_debt + cleaning_fee + repair_fee + other_charge`

3. `0 <= deposit_applied <= deposit_held` and `deposit_applied <= gross_charges`.
4. `settlement_due = gross_charges - deposit_applied`.
5. `outstanding_amount = max(settlement_due - paid_amount, 0)`; it cannot be
   negative.
6. `refund_amount` cannot be negative and cannot exceed `deposit_held -
   deposit_applied` without an Owner-approved external-refund policy.
7. A `closed` settlement requires `outstanding_amount = 0` and documented treatment
   of any `refund_amount`.
8. A final settlement must not mutate historical `MonthlyBill.total`, linked
   `PaymentRecord.amount`, contract rent, or deposit.
9. If `other_charge > 0`, `other_desc` is mandatory. Repair and cleaning evidence
   references are recommended but must not be silently encoded in a status field.

### FK And Delete Rules

- `contract_id` uses `ON DELETE RESTRICT`; financial close-out must survive any
  attempted contract cleanup.
- `final_monthly_bill_id`, if set, uses `ON DELETE RESTRICT`; deleting a bill linked
  by a finalized/closed settlement is forbidden.
- `created_by_id`, if present, uses `ON DELETE SET NULL`.
- There is no cascade deletion from contracts, rooms, tenants, properties, or bills
  into a settlement.
- A finalized, closed, or voided settlement is never physically deleted.

## Payment And Deposit Boundary

The current `PaymentRecord` contract only formally links payment to a monthly bill or
contract. It does not allocate a payment to individual move-out components or record a
deposit-refund transfer. Therefore `paid_amount` cannot be advertised as fully
reconciled until an Owner-approved allocation rule exists.

Directly safe interim behavior:

- show R6 draft/finalized component calculations;
- derive final-month collection from linked `PaymentRecord` records when a final bill
  is linked;
- retain deposit and final-payment evidence in notes/reference fields without
  inventing a second payment model.

Not safe without an ADR:

- marking a settlement `closed` solely because `MonthlyBill.paid=true`;
- treating an unlinked payment record as settlement payment;
- recording a tenant refund as a negative `PaymentRecord` or negative settlement
  charge.

## Owner Decisions Required Before Finalized R2 Writes

| ID | Decision | Why It Blocks Final Financial Meaning |
| --- | --- | --- |
| ADR-R01 | Cash basis versus accrued basis for `PropertyExpense` | Determines whether transaction date means incurred, paid, or both. |
| ADR-R02 | Expense approval and correction authority | Determines whether `posted` needs a reviewer/approval state. |
| ADR-R03 | Cross-property/shared expense allocation | A single receipt cannot be duplicated across properties without an allocation rule. |
| ADR-R04 | Deposit handling evidence | Must define how refund payment proof and deposit deductions are recorded. |
| ADR-R05 | Settlement payment allocation | Must define whether existing `PaymentRecord` is extended, linked by a ledger, or only reconciles the final monthly bill. |
| ADR-R06 | Eligibility to finalize before contract termination | Define whether a scheduled move-out can be finalized while contract status is still `active`. |
| ADR-R07 | Historical display snapshots | Decide whether a finalized settlement keeps names/room labels at finalization time or joins current master data. |
| ADR-R08 | Management fee policy | Define whether it is a tenant settlement charge, property expense, or both under distinct source documents. |

## Forbidden Implementations

1. Do not store property operating expenses in `MonthlyBill.other_charges` or use
   them to reduce a tenant's `MonthlyBill.total`.
2. Do not add expense, settlement, cleaning, repair, or deposit states to
   `Room.status`, `Contract.status`, or `Tenant.name`.
3. Do not mutate a posted expense or finalized settlement in place.
4. Do not hard-delete posted expense/settlement financial history or cascade-delete it
   when a parent entity is removed.
5. Do not derive R6 payment completion from free-text notes, raw OCR output, or a
   boolean monthly-bill flag alone.
6. Do not create a runtime Google Sheets dependency or copy spreadsheet formulas into
   routes/templates.
7. Do not alter `MonthlyBill.total` while generating R3 or R6 reports.

## Direct Implementation Sequence

1. Implement R1 derived report DTO/query/export paths with server-side visible-property
   filtering and whole-dollar formatting.
2. Implement R2 aggregation strictly from R1 totals, with a property grand total.
3. Implement R4 and R5 as read-only queries with the same property authorization
   boundary and CSV/XLSX export support.
4. Approve this contract plus ADR-R01 through ADR-R08 as applicable.
5. Add `PropertyExpense` model, migration, repository, service, write flow, report,
   and integration tests as one vertical slice.
6. Add `MoveOutSettlement` only after the payment/deposit ADRs are resolved; use a
   separate migration and a finalization service that enforces every invariant.

## Required Acceptance Checks

- R1 rows aggregate exactly into R2 for identical month/property filters.
- R2's selected single-property month matches the corresponding R5 cell.
- Reports accept only properties visible to the authenticated user and reject foreign
  property IDs server-side.
- Report output never changes a bill, payment, contract, room, tenant, expense, or
  settlement.
- Posted expenses and finalized settlements have tests for forbidden in-place edits,
  invalid status transitions, restricted parent deletes, and every money invariant.
- CSV/XLSX totals match HTML totals after the shared whole-dollar rounding policy.

## Blocking Risks

No blocker prevents R1 derived reporting. R3 can begin its schema/write-flow work once
the direct contract above is accepted. R6 cannot truthfully provide a financially
closed settlement workflow until ADR-R04 and ADR-R05 define deposit refund evidence and
payment allocation. Those are the only blocking Owner decisions for R6 finalization.
