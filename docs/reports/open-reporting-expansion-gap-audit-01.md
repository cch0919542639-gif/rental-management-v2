# Reporting Expansion Gap Audit 01

## Scope and Baseline

This audit compares `docs/architecture/reporting-expansion-roadmap.md` with the
current reports module and domain models. It is read-only analysis: no application,
test, or coordination files were changed.

The roadmap is currently present in the reporting-planning worktree. The code
baseline reviewed here is `codex-phase2-mainline-01`.

## Existing Reporting Boundary

The current reports module has monthly, landlord-summary, yearly, and maintenance
reports, each with CSV/XLSX export. The monthly query already joins:

`MonthlyBill -> Contract -> Room -> Property -> Landlord + Tenant`.

It currently accepts only a month filter. It returns `MonthlyBill.paid` as a boolean
and does not return either a linked-payment amount or a remaining balance. The
yearly and landlord summary queries aggregate the same boolean paid flag; they do
not aggregate `PaymentRecord.amount`.

`PaymentRecord` has an `amount`, `monthly_bill_id`, and controlled
`record_status`. The payment-link service associates the record to a bill, then
calculates the linked amount to decide whether `MonthlyBill.paid` is true. Therefore
PaymentRecord can provide an actual "已繳" amount only when the report sums records
that are linked to the bill. The existing report query does not do this yet. Pending,
verified-but-unlinked, rejected, or unlinked historical records must not be included
as bill-level paid money.

## R1: Property Rent Collection Detail

### Available now

| Required output | Current source |
| --- | --- |
| Month, landlord, property, room, tenant | Existing monthly report join |
| Contract dates | `Contract.start_date`, `Contract.end_date` |
| Rent, electricity, public electricity, water | `MonthlyBill` |
| Other charge and description | `MonthlyBill.other_charges`, `MonthlyBill.other_desc` |
| Previous balance and stored total due | `MonthlyBill.previous_balance`, `MonthlyBill.total` |

### Gaps and minimum boundary

1. Add a validated single `property_id` filter to the report form and repository.
2. Add a report repository query that returns contract dates and aggregates linked
   `PaymentRecord.amount` per `MonthlyBill.id`.
3. Add a service projection that converts the month for UI, preserves stored
   `MonthlyBill.total` as `total_due`, and calculates
   `remaining_due = max(total_due - linked_paid_amount, 0)`.
4. Add HTML, CSV, and XLSX routes using the existing export adapter.

No billing mutation is required. Do not recalculate or overwrite `MonthlyBill.total`
while rendering the report.

## R2: Selected-Property Settlement Summary

### Available now

All monetary source fields except the linked paid amount already exist in
`MonthlyBill`. Property and landlord identity are already reachable through the
monthly report join. Existing export infrastructure can produce CSV/XLSX.

### Gaps and minimum boundary

1. Add a multi-value `property_ids` filter and validate every selected ID against the
   authenticated user's visible property set.
2. Add a grouped repository query over the R1-safe bill projection. It must aggregate
   bill count, rent, electricity, public electricity, water, other charges, previous
   balance, stored total, linked paid amount, and non-negative outstanding amount.
3. The service must append one grand-total row and must use the same linked-payment
   predicate as R1 so both outputs reconcile.
4. Add HTML, CSV, and XLSX routes.

Excluded from this report: landlord payable, commission, service fees, and property
expenses. None of these values has an approved transaction source today.

## R3: Property Expense Detail

### Available now

No expense model, repository, service, route, or approved expense ledger was found.
Maintenance requests are operational records, not a property expense ledger.

### Required new boundary

Create a separate `PropertyExpense` domain only after contract review and migration
approval. The minimum record is one immutable expense row with property, transaction
date, category, amount, payee/reference, notes, and audit timestamps. It needs its
own repository, service, write routes, report query, migration, and integration tests.

Do **not** store property expenses in `MonthlyBill.other_charges`; that field is a
tenant bill component and would make tenant receivables and owner operating costs
indistinguishable.

## R4: New Tenant Detail

### Available now

| Required output | Current source |
| --- | --- |
| Property and room | `Contract -> Room -> Property` |
| Tenant and phone | `Tenant.name`, `Tenant.phone` |
| Start/end date, deposit, rent | `Contract` |
| Starting electricity/water readings and notes | `Contract` |

### Gaps and minimum boundary

1. Add a month filter using `Contract.start_date` calendar-month boundaries, not a
   string comparison.
2. Add optional validated property selection, including multi-property selection if
   it shares the R2 filter component.
3. Create a dedicated read query and export projection; terminated contracts remain
   included when their start date is in the requested month.
4. Add HTML, CSV, and XLSX routes.

No new financial model is required for R4.

## R5: Annual Monthly Property Statistics

### Available now

`MonthlyBill.year_month`, `MonthlyBill.total`, and the property join support the
base twelve-month matrix. The existing yearly overview and export adapter provide a
useful pattern, but they are not property-selectable and do not expose the requested
matrix or linked paid/outstanding totals.

### Gaps and minimum boundary

1. Add a year filter plus zero-or-more validated property IDs.
2. Repository returns property/month aggregates from stored `MonthlyBill.total` and
   linked-payment sums; no utility or total recomputation is allowed.
3. Service creates rows per property, January through December columns, annual total,
   linked-paid annual total, outstanding annual total, and a grand-total row.
4. Add HTML, CSV, and XLSX routes.

R5 must reconcile with R2 when both are filtered to the same property and month.

## R6: Move-Out Settlement Detail

### Available now

Contracts expose tenant, room/property, dates, deposit, status, and final monthly
bills. PaymentRecord can provide linked amounts for a final bill. There is no
dedicated move-out settlement record or write workflow.

### Required new boundary

Create an independent `MoveOutSettlement` domain after contract review and migration
approval. It must link to a contract and record final rent, electricity, water,
management fee, previous debt, cleaning fee, repair fee, other charge, deposit
applied, refund, paid amount, outstanding amount, status, and finalized date. A single
service must derive the settlement total and protect finalized records.

Do **not** put settlement components in `MonthlyBill` and do not alter historical
MonthlyBill totals implicitly. A move-out settlement is a separate closing financial
event, not a replacement monthly receivable.

## Delivery Order and Blockers

| Order | Work | Status | Blocker |
| --- | --- | --- | --- |
| 1 | Shared property visibility and multi-select validation | Needed | Define authenticated visibility boundary |
| 2 | R1 property collection detail | Ready for implementation | Linked-payment aggregation query |
| 3 | R2 selected-property summary | Ready after R1 projection | Shared aggregation predicate |
| 4 | R4 new tenant detail | Ready for implementation | None beyond filter validation |
| 5 | R5 annual property statistics | Ready after R2 aggregation | Shared linked-payment aggregation |
| 6 | R3 property expense detail | Blocked by new data contract | `PropertyExpense` ADR, migration, write flow |
| 7 | R6 move-out settlement detail | Blocked by new data contract | `MoveOutSettlement` ADR, migration, write flow |

## Audit Verdict

R1, R2, R4, and R5 can proceed as read-only reporting work once server-side property
visibility validation and linked-payment aggregation are implemented. R3 and R6 must
remain separate Phase R2 financial domains. There is no blocker to beginning the
derived-report implementation, but there is a hard boundary against treating
`MonthlyBill.other_charges` as an expense ledger or using MonthlyBill as a move-out
settlement store.
