# Box — R3 PropertyExpense Test Plan & Acceptance Spec

Branch: `agent/box-property-expense-test-plan-01`
Baseline: `codex-phase2-mainline-01`
Author: box (tests / scripts / runbook agent)
Date: 2026-07-17

---

## 1. Scope

Plan and specify integration tests for the `PropertyExpense` domain. No app code
(models, migrations, services, routes, templates) is written here — this is a
pure test-spec + acceptance-criteria deliverable.

### What Is PropertyExpense

A property-level operating-expense ledger. One row = one financial fact:
cleaning, repair, utility, tax, etc. **Not** a tenant charge — never stored in
`MonthlyBill.other_charges`.

Contract reference: `docs/reports/reasonix-reporting-expansion-contract-01.md` §
Direct Items: PropertyExpense Minimum Contract.

---

## 2. Invariants

From the Reasonix contract:

| # | Invariant | Enforcement |
|---|-----------|-------------|
| 1 | `amount > 0` for every `posted` row | DB CHECK + service guard |
| 2 | `transaction_date` is non-null for every `posted` row | Service guard |
| 3 | `category` is one of the formal controlled values | Enum/choices guard |
| 4 | Only `posted` records contribute to net-income totals | Query filter |
| 5 | A voided record preserves original amount, date, property, audit trail | No in-place mutation |
| 6 | Expense totals = sum of posted rows in date range, never inferred from `MonthlyBill.other_charges` | Service guard |
| 7 | `property_id` uses `ON DELETE RESTRICT` | DB constraint |
| 8 | Record must exist before transition; delete on `draft`-only rows allowed, `posted`/`voided` rows forbidden | Service guard |

---

## 3. State Machine

```text
draft -> posted -> voided
draft -> cancelled
```

| State | Editable | In Totals | Can Delete |
|-------|----------|-----------|------------|
| `draft` | Yes | No | Yes (physical) |
| `posted` | No | Yes | No |
| `voided` | No | No | No |
| `cancelled` | No | No | Yes (physical) |

A correction to a `posted` record must be a void + replacement, never an in-place
amount edit. Re-posting a voided or cancelled record is forbidden.

---

## 4. Test Areas

### 4.1 CRUD

| Area | Detail |
|------|--------|
| Create | Create expense with all fields; each optional field omitted separately; required field missing → 400/error |
| Read | List by property, list by date range, list by category, single-record detail |
| Update (draft) | Edit amount, category, payee, reference_no, notes, transaction_date |
| Update (posted) | Edit rejected (immutable) |
| Delete (draft) | Physical delete succeeds |
| Delete (posted) | Physical delete **rejected** (403 or flash error) |
| Delete (voided) | Physical delete **rejected** (403 or flash error) |
| Create with negative amount | **Rejected**: amount must be > 0 |

### 4.2 Status Transitions

| Transition | From | To | Condition |
|-----------|------|-----|-----------|
| Post | `draft` | `posted` | `amount > 0`, `transaction_date` set, `category` valid |
| Post (invalid) | `draft` | — | `amount = 0` → rejected; `amount = None` → rejected; missing `transaction_date` → rejected; invalid `category` → rejected |
| Void | `posted` | `voided` | Requires `void_reason`, sets `voided_at` |
| Void (no reason) | `posted` | — | Rejected |
| Cancel | `draft` | `cancelled` | Sets `voided_at` + `void_reason = "cancelled"` |
| Re-post (failed) | `voided` | — | Forbidden |
| Re-post (failed) | `cancelled` | — | Forbidden |
| Double-void (failed) | `voided` | — | Forbidden |
| Post (already posted) | `posted` | — | No-op / rejected |

### 4.3 Amount Validation

| Test | Expect |
|------|--------|
| `amount = 0` | Rejected at create and post |
| `amount = negative` | Rejected at create and post |
| `amount = 0.01` | Accepted (minimum positive) |
| `amount = large number` | Accepted (e.g. 9,999,999) |
| `amount = None` | Rejected |
| `amount` has >2 decimal places | Rounded or rejected per policy |

### 4.4 Category Validation

| Category | Formal Value |
|----------|-------------|
| Management fee | `management_fee` |
| Utility (water/electricity) | `utility` |
| Cleaning | `cleaning` |
| Repair | `repair` |
| Tax | `tax` |
| Insurance | `insurance` |
| Supplies | `supplies` |
| Other | `other` |

| Test | Expect |
|------|--------|
| Valid category (each of 8) | Accepted |
| Invalid category string | Rejected |
| Empty category | Rejected |
| Case-mismatch category | Rejected or normalised per impl |

### 4.5 Property Scoping

| Test | Expect |
|------|--------|
| Create expense for property A → listed under A | Pass |
| List expenses for property A → only A's expenses shown | Pass |
| List expenses for property B → A's expenses not shown | Pass |
| User without property A permission cannot create expense for A | 403 / flash |
| User without property A permission cannot view A's expenses | 403 / flash |

### 4.6 Filters

| Filter | Expect |
|--------|--------|
| Date range (from + to) → returns expenses in range | Correct results |
| Date range (from only) → returns expenses ≥ from | Correct results |
| Date range (to only) → returns expenses ≤ to | Correct results |
| Category filter → returns only that category | Correct results |
| Date range + category combined | Correct intersection |
| Empty result set for non-overlapping filter | 200, empty table |
| `year_month` derived from `transaction_date` | Report month is correct |
| Non-Gregorian transaction date → derived as year_month | Correct derivation |

### 4.7 CSV / XLSX Export

| Test | Expect |
|------|--------|
| CSV export of property expense list | Returns `text/csv`, correct headers, all rows |
| XLSX export of property expense list | Returns `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, correct data |
| CSV with no rows | Returns header row only |
| XLSX with no rows | Valid XLSX with header row only |
| Date-range filtered CSV | Rows match the filter |
| Category-filtered CSV | Rows match the filter |
| Export column set matches displayed table | id, property, category, amount, payee, transaction_date, record_status |
| CSV filename includes property name + date range | `property_expense_<property>_<from>_<to>.csv` |

### 4.8 Mobile Table

| Test | Expect |
|------|--------|
| Table page renders on mobile viewport | No horizontal scroll, responsive |
| Amount column right-aligned | ₿ aligned |
| Record status column shows badge/colour | Visual indicator per state |
| Category column shows translated label | Full name not code |
| Date column sortable | Asc/desc toggle |
| Row tap → detail/edit page | Navigates correctly |

### 4.9 Forbidden Operations

| Operation | Expect |
|-----------|--------|
| Store expense data in `MonthlyBill.other_charges` | Audit / service must prevent |
| Hard-delete a `posted` expense | Blocked |
| Hard-delete a `voided` expense | Blocked |
| Include `draft` expenses in `total_expenses` report sum | Excluded |
| Include `cancelled` expenses in report sum | Excluded |
| Create expense without a valid `property_id` | FK violation or 400 |

---

## 5. Test File & Case Manifest

All tests go into a single new file:

**File:** `tests/integration/test_property_expense_crud_states.py`

| # | Test Function | Area | Notes |
|---|---------------|------|-------|
| 1 | `test_expense_create_basic` | CRUD / Create | Full fields, verify DB row |
| 2 | `test_expense_create_missing_required` | CRUD / Create | Missing category → 400 |
| 3 | `test_expense_create_negative_amount` | Amount validation | `amount=-100` → rejected |
| 4 | `test_expense_create_zero_amount` | Amount validation | `amount=0` → rejected |
| 5 | `test_expense_create_optional_fields_omitted` | CRUD / Create | No payee, reference, notes → ok |
| 6 | `test_expense_read_list_by_property` | CRUD / Read | Property-scoped list |
| 7 | `test_expense_read_detail` | CRUD / Read | Single-record detail |
| 8 | `test_expense_update_draft_ok` | CRUD / Update | Edit amount, category, notes |
| 9 | `test_expense_update_posted_rejected` | CRUD / Update | Immutable → 403 |
| 10 | `test_expense_delete_draft_ok` | CRUD / Delete | Physical delete succeeds |
| 11 | `test_expense_delete_posted_rejected` | CRUD / Delete | 403 / flash error |
| 12 | `test_expense_delete_voided_rejected` | CRUD / Delete | 403 / flash error |
| 13 | `test_expense_post_from_draft` | State / Post | Valid transition |
| 14 | `test_expense_post_missing_amount` | State / Post | `amount=None` → rejected |
| 15 | `test_expense_post_missing_transaction_date` | State / Post | `transaction_date=None` → rejected |
| 16 | `test_expense_post_invalid_category` | State / Post | Bogus category → rejected |
| 17 | `test_expense_void_posted` | State / Void | Requires `void_reason` |
| 18 | `test_expense_void_missing_reason` | State / Void | `void_reason=None` → rejected |
| 19 | `test_expense_cancel_draft` | State / Cancel | Sets `voided_at` + `void_reason="cancelled"` |
| 20 | `test_expense_repost_voided_forbidden` | State / Guard | Forbidden |
| 21 | `test_expense_repost_cancelled_forbidden` | State / Guard | Forbidden |
| 22 | `test_expense_double_void_forbidden` | State / Guard | Forbidden |
| 23 | `test_expense_category_list_valid` | Category | All 8 enum values accepted |
| 24 | `test_expense_category_invalid_rejected` | Category | `"unknown"` → rejected |
| 25 | `test_expense_property_scoping_create` | Property scope | Property A only accessible to A |
| 26 | `test_expense_property_scoping_list` | Property scope | B's list excludes A's expenses |
| 27 | `test_expense_filter_date_range` | Filters | From + to → correct set |
| 28 | `test_expense_filter_category` | Filters | Single category |
| 29 | `test_expense_filter_date_and_category` | Filters | Combined intersection |
| 30 | `test_expense_filter_empty_result` | Filters | Non-overlapping → empty table |
| 31 | `test_expense_filter_year_month_derived` | Filters | `year_month` from `transaction_date` |
| 32 | `test_expense_export_csv` | Export | `text/csv`, correct rows |
| 33 | `test_expense_export_xlsx` | Export | Valid XLSX, correct data |
| 34 | `test_expense_export_csv_filtered` | Export | Rows match active filter |
| 35 | `test_expense_export_csv_empty` | Export | Header only when no rows |
| 36 | `test_expense_draft_excluded_from_totals` | Invariant | Not counted in sum |
| 37 | `test_expense_posted_included_in_totals` | Invariant | Counted in sum |
| 38 | `test_expense_voided_excluded_from_totals` | Invariant | Excluded after void |
| 39 | `test_expense_no_cascade_from_property_delete` | FK / Delete rule | `ON DELETE RESTRICT` enforced |
| 40 | `test_expense_forbidden_other_charges_leak` | Constraint | Not stored in `MonthlyBill` |

**Total: 40 test cases.**

---

## 6. Existing Fixtures Used

| Fixture | Source | Purpose |
|---------|--------|---------|
| `app` | `conftest.py` | Flask app context |
| `logged_in_client` | `conftest.py` | Authenticated test client |
| `seeded_data` | `conftest.py` | Pre-seeded property, rooms, contracts |
| `db` | `conftest.py` | SQLAlchemy session |

No custom fixtures needed for PropertyExpense; the standard set is sufficient.

---

## 7. Acceptance Criteria

| Criteria | Status |
|----------|--------|
| All 40 tests pass against `codex-phase2-mainline-01` | ⬜ |
| No schema, model, service, route, or template modifications | ✅ |
| No `PropertyExpense` data stored in `MonthlyBill.other_charges` | ✅ |
| No `draft` / `cancelled` records included in `total_expenses` | ⬜ |
| Hard delete of `posted` or `voided` records is blocked | ⬜ |
| CSV and XLSX exports produce valid files with correct data | ⬜ |
| Mobile viewport renders table without horizontal scroll | ⬜ |
| All 8 formal categories accepted; invalid categories rejected | ⬜ |
| Property-scoped access enforced at both create and list | ⬜ |

---

## 8. Data Contract Reference

Minimum fields (from Reasonix contract):

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | PK int | — | Auto |
| `property_id` | FK int | ✅ | `ON DELETE RESTRICT` |
| `transaction_date` | date | ✅ | Report month derived from this |
| `category` | str(32) | ✅ | Controlled enum (8 values) |
| `amount` | numeric | ✅ | Positive, precise, rounded |
| `payee` | str(128) | ❌ | Counterparty name |
| `reference_no` | str(64) | ❌ | Receipt/invoice ref |
| `notes` | text | ❌ | Human explanation |
| `record_status` | str(16) | ✅ | `draft` / `posted` / `voided` / `cancelled` |
| `voided_at` | datetime | ⚠️ | Required when status = voided |
| `void_reason` | str(256) | ⚠️ | Required when status = voided |
| `created_at` | datetime | — | Auto audit |
| `updated_at` | datetime | — | Auto audit |
| `created_by_id` | FK int (nullable) | ❌ | User audit |

`year_month` is derived, never stored independently.

---

## 9. Run Command

```bash
cd D:\CodexRuntime\rental\rebuild-main
pytest tests/integration/test_property_expense_crud_states.py -v --tb=line
```
