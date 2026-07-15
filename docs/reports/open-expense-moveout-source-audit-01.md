# Expense & Move-Out Settlement Source Audit — Open

Date: 2026-07-14
Author: open
Base: `codex-phase2-mainline-01`
Branch: `agent/open-expense-moveout-source-audit-01`
Target: R3 PropertyExpense / R6 MoveOutSettlement (per `reasonix-reporting-expansion-contract-01.md`)

---

## Sources Scanned

| # | Source | Location | Content |
|---|--------|----------|---------|
| S1 | Old system DB | `D:\rental\rental.db` | 18 tables: contracts, monthly_bills, payment_records, electricity_bills, water_bills, properties, rooms, tenants, landlords, maintenance_requests, sheets_import_logs |
| S2 | Google Sheet 202604 | `real_import/sheet_202604.csv` | 18 columns (tenant billing); no expense/settlement columns |
| S3 | Google Sheet 202605 | `real_import/sheet_202605.csv` | 23 columns (same + notification/calc/notes); no expense/settlement columns |
| S4 | Google Sheet 202606 | `real_import/sheet_202606.csv` | 25 columns (same); no expense/settlement columns |
| S5 | New system DB | `runtime-real.db` | Empty (0 tables); no schema yet for R3/R6 |
| S6 | Existing contract | `reasonix-reporting-expansion-contract-01.md` | R3 and R6 field specs (see "Target Schema" below) |

---

## Target Schema (per Reasonix Contract)

### R3: PropertyExpense

| Field | Type | Required |
|-------|------|----------|
| id | PK | auto |
| property_id | FK→properties | yes |
| transaction_date | DATE | yes |
| category | enum(8) | yes |
| amount | numeric > 0 | yes |
| payee | varchar | no |
| reference_no | varchar | no |
| notes | text | no |
| record_status | enum(4) | yes |
| created_at, updated_at | datetime | auto |
| created_by_id | FK→user | no |
| voided_at, void_reason | -, text | void cases |

### R6: MoveOutSettlement

| Field | Type | Required |
|-------|------|----------|
| id | PK | auto |
| contract_id | FK→contracts | yes |
| final_monthly_bill_id | FK→monthly_bills | no |
| move_out_date | DATE | yes (before finalize) |
| finalized_date | DATE | no |
| final_rent | numeric >= 0 | yes |
| electricity_amount | numeric >= 0 | yes |
| water_amount | numeric >= 0 | yes |
| management_fee | numeric >= 0 | yes |
| previous_debt | numeric >= 0 | yes |
| cleaning_fee | numeric >= 0 | yes |
| repair_fee | numeric >= 0 | yes |
| other_charge, other_desc | numeric, text | other_charge>0 requires other_desc |
| deposit_held | numeric | snapshot at settlement |
| deposit_applied | numeric | applied against charges |
| refund_amount | numeric | to return |
| paid_amount | numeric | payment received |
| gross_charges | numeric | derived sum |
| outstanding_amount | numeric | derived |
| status | enum(5) | yes |
| notes | text | no |
| created_at, updated_at, created_by_id | - | audit |

---

## R3 — PropertyExpense Source Mapping

### DIRECT fields

| # | R3 Field | Source | Table.Column | Sample Value | Notes |
|---|----------|--------|-------------|--------------|-------|
| D1 | property_id | FK | `electricity_bills.property_id` | 5, 6, 9, 10, 13 | 9 of 11 ebills have valid property_id matching `properties.id` |
| D2 | property_id | FK | `water_bills.property_id` | — | Table is empty (0 rows) |
| D3 | category | Fixed | — | `utility` | electricity_bills → `utility`; water_bills → `utility` |
| D4 | amount | Direct | `electricity_bills.total_amount` | 1318–7320 | Includes both flow + public; already aggregated per bill |
| D5 | amount | Direct | `electricity_bills.public_amount` | 0–75 | Public electricity portion, can be split into separate expense or merged |
| D6 | notes | Direct | `electricity_bills.notes` | JSON strings with meter metadata | Contains OCR source, meter labels, calc methods |
| D7 | created_at | Direct | `electricity_bills.created_at` | timestamp | Can be used directly |
| D8 | transaction_date | Derivable | `electricity_bills.period_start` / `period_end` | 2026-03-25~05-26 | Use period_end as transaction_date; `year_month` field also available (though sparse) |

### CAUTION fields

| # | R3 Field | Source | Issue | Workaround |
|---|----------|--------|-------|------------|
| C1 | payee | `landlords.name` for utility | Landlord name available but payee for utility bill is the utility company (台電/自來水), not landlord | Use `landlord.electricity_account` holder name if available; else mark as `NULL` |
| C2 | reference_no | `electricity_bills.notes.ocr_source` or `electricity_bills.ocr_image_path` | OCR raw text may contain bill numbers but not structured | Parse from `ocr_raw_text` if needed; otherwise NULL |
| C3 | record_status | — | No status concept in old system for expenses | Default to `posted` for confirmed bills (`status='confirmed'`); `draft` for unconfirmed |
| C4 | created_by_id | — | Old system has no user tracking per expense | Set to NULL; old system has `created_by` column but value is always NULL in data |

### BLOCKED fields

| # | R3 Field | Reason |
|---|----------|--------|
| B1 | category: management_fee, cleaning, repair, tax, insurance, supplies, other | No source data exists. `monthly_bills.other_charges` with `other_desc='管理費'` are **tenant-level** pass-through charges (collected from tenants, not property-level expenses). They represent income, not expense. Cannot be used for R3. |
| B2 | category: repair | No table or field in old system records repair expenses. `maintenance_requests` exists in new system but is empty/unrelated. |
| B3 | payee for non-utility expenses | No vendor/supplier records exist in old system. |
| B4 | reference_no for non-utility | No invoice/receipt tracking in old system. |

---

## R6 — MoveOutSettlement Source Mapping

### DIRECT fields

| # | R6 Field | Source | Table.Column | Sample Value | Notes |
|---|----------|--------|-------------|--------------|-------|
| D9 | contract_id | FK | `contracts.id` | 46, 68, 81, 85, 90, 173 | 6 contracts with status=terminated/ended |
| D10 | move_out_date | Direct | `contracts.terminated_date` | 2026-06-07 | Only 1 of 6 has a value (contract 90); others NULL |
| D11 | deposit_held | Direct | `contracts.deposit` | NULL / 0 | All 6 are NULL or 0 — no deposit recorded |
| D12 | notes | Direct | `contracts.settle_notes` | '' (empty) | All 6 are empty |
| D13 | final_rent | Derivable | `contracts.rent` | 4800, 7265, 0, 0, 7000, 5800 | Rent at contract level; for prorated final month, see CAUTION |
| D14 | electricity_amount | Direct | `contracts.settle_electricity` | 0 | All are 0 — no settlement electricity data was recorded |
| D15 | water_amount | Direct | `contracts.settle_water` | 0 | All are 0 |
| D16 | previous_debt | Derivable | `monthly_bills` (unpaid totals) | Various | Can be computed as sum of unpaid bills for the contract before final month |
| D17 | final_monthly_bill_id | Derivable | `monthly_bills.id` where year_month = move_out month | — | If move_out_date is known, join with monthly_bills |

### CAUTION fields

| # | R6 Field | Source | Issue | Workaround |
|---|----------|--------|-------|------------|
| C5 | final_rent (prorated) | `contracts.settle_rent_extra` | Field exists but **all are 0**; no prorated rent was ever recorded | Use `monthly_bills.rent` for last full month; for partial month, no source exists. **Owner must confirm if proration was ever done.** |
| C6 | final_monthly_bill_id | — | Only 1 of 6 terminated contracts has a date; others have `terminated_date=NULL`. Without date, no bill can be identified as "final" | Use `last monthly_bill` for that contract by max(year_month) as heuristic |
| C7 | management_fee | `monthly_bills.other_charges` where `other_desc LIKE '%管理%'` | Management fee in old system is a **tenant charge** (collected by landlord), not a property expense. It should go into R6 but amount must match last bill. | Read from the final monthly_bill's `other_charges` field |
| C8 | keys_returned | `contracts.keys_returned` | Field exists (0/1 BOOLEAN) but all 6 records have 0 | Need manual verification if keys were actually returned |
| C9 | refund_bank / refund_account / refund_account_holder | `contracts.refund_*` | Fields exist but all are NULL; no refund info recorded | Manual collection needed |

### BLOCKED fields

| # | R6 Field | Reason |
|---|----------|--------|
| B5 | cleaning_fee | No source in old system. `monthly_bills` has no cleaning fee category. Contracts have no cleaning field. |
| B6 | repair_fee | No source in old system. No repair cost tracking exists. |
| B7 | other_charge / other_desc | `contracts.settle_other` exists but is empty for all 6 records. Cannot be populated from any other source. |
| B8 | deposit_applied | No deposit data exists (all NULL/0). Cannot compute applied amount. |
| B9 | refund_amount | No deposit and no refund info. Cannot compute. |
| B10 | paid_amount (settlement payment) | `payment_records` table is **empty** (0 rows). No settlement payment was ever recorded. |
| B11 | finalized_date / status progression | No concept of settlement lifecycle in old system. All status would need to be inferred or defaulted. |

---

## Non-Derivable Amounts Summary

Amounts that **cannot** be derived from any existing old-system source or Google Sheet:

| # | Amount | R3/R6 | Why Missing | What's Needed |
|---|--------|-------|-------------|---------------|
| N1 | Cleaning fee per move-out | R6 | Old system has no cleaning cost tracking | Owner to provide flat fee per contract/room type |
| N2 | Repair fee per move-out | R6 | No repair/maintenance cost history | Owner to provide actual cost or estimate |
| N3 | Deposit refund amount | R6 | No deposit recorded for any terminated/ended contract | Owner to confirm deposit policy |
| N4 | Deposit applied amount | R6 | Same as N3 | Owner to confirm offset logic |
| N5 | Non-utility payee names | R3 | No vendor/supplier records | Manual entry after R3 UI is built |
| N6 | Prorated rent (partial month) | R6 | `settle_rent_extra` all zero | Owner to confirm if proration was ever calculated |

---

## Questions for Owner

1. **Cleaning fee**: Is there a standard cleaning fee applied per move-out (e.g., NT$500–2000)? Or does it vary per room?

2. **Repair fee**: Who determines repair deductions at move-out? Are they based on actual invoices or flat estimates?

3. **Deposit handling**: 6 terminated/ended contracts exist with zero/NULL deposit. Was deposit ever collected for these? What is the standard deposit amount (1 month / 2 months rent)?

4. **Refund bank info**: `refund_bank`, `refund_account`, `refund_account_holder` are all NULL. Were refunds issued in cash instead? Or is this data elsewhere (paper records)?

5. **Move-out date for contracts 46, 68, 81, 85, 173**: `terminated_date` is NULL despite `status='terminated'/'ended'`. Can the date be found from other records (e.g., final monthly_bill date, key return log)?

6. **Prorated final month rent**: `settle_rent_extra` = 0 for all. Was prorated rent ever calculated for mid-month move-outs? If so, where?

7. **Property-level expenses beyond electricity**: No water bills, property tax, insurance, or supplies records exist. Will these be entered through the R3 UI going forward, or is there historical data elsewhere?

---

## Historical Import Order

### Phase 1 (NO BLOCKERS — ready after R3 model is deployed)

```
1. electricity_bills → property_expenses (category=utility)
   - 11 records, all fields available
   - Stop condition: all electricity_bills processed
   - Validate: property_id maps to new system property, amount > 0
```

### Phase 2 (awaits Owner answers on questions Q1-Q3)

```
2. Move-out settlement stubs (R6)
   - 6 terminated/ended contracts
   - Populate: contract_id, move_out_date (if available), final_rent, deposit_held
   - Leave cleaning_fee, repair_fee, refund_amount as NULL
   - Stop condition: all 6 processed; mark for manual review
```

### Phase 3 (manual data entry — no automated source)

```
3. Cleaning fees, repair fees, deposit refunds per Owner's policy
4. Non-utility property expenses (tax, insurance, supplies, management fee)
   - These have NO automated source; must be entered via R3 UI or import template
```

---

## Summary

| Domain | DIRECT | CAUTION | BLOCKED |
|--------|--------|---------|---------|
| R3 PropertyExpense | 8 fields from electricity_bills | 4 fields (payee, ref, status, creator) | 5 categories (management, cleaning, repair, tax, insurance, supplies) |
| R6 MoveOutSettlement | 9 fields from contracts + monthly_bills | 5 fields (prorated rent, final bill ID, mgmt fee, keys, refund info) | 7 fields (cleaning, repair, other, deposit, refund, payment, status) |
| **Total** | **17** | **9** | **12** |

### Hard Blockers (cannot proceed without Owner decision)

1. **R3 expense categories** — Only `utility` (electricity) has source data. All other categories need manual entry.
2. **R6 deposit & refund** — No deposit records, no refund bank info, no payment records. Settlement cannot compute refund amounts.
3. **R6 cleaning/repair fees** — No source data exists. Cannot populate.
4. **R6 move-out dates** — 5 of 6 contracts have `terminated_date=NULL` despite terminated/ended status.

### Import Readiness

| Layer | Readiness | Blocked By |
|-------|-----------|------------|
| R3 utility expenses (electricity_bills only) | ✅ Ready | — |
| R3 all other categories | ❌ Blocked | No source data |
| R6 contract stubs | ⚠️ Partial | Owner answers Q1-Q7 |
| R6 financial close | ❌ Blocked | No deposit/refund/cleaning/repair data |

---

## Files Changed

- `docs/reports/open-expense-moveout-source-audit-01.md` (this file)
- `coordination/progress/open.md`
- `coordination/completed/open.md`
