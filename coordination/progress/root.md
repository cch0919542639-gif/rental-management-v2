# root

Status: COMPLETED - CHANGYU_2026_PAYMENT_RECONCILIATION
Last Updated: 2026-08-09

## 2026-08-09 System Startup Baseline
- Scope: safely resume the rental-management rebuild without changing pre-existing unstaged work; establish the runnable baseline and identify the next user-prioritized vertical slice.
- Intended users: property administrators for daily operations and property owners for scoped report access.
- In scope: current app/runtime verification and project recovery records. Out of scope: formal database writes, staging-data imports, Git changes, and changes to existing dirty files.
- Planned validation: focused authentication, billing, and payment integration smoke test plus `git diff --check`.
- Completed: `rtk py -3 -m pytest -q tests\\integration\\test_auth_billing_payments_smoke.py` passed (1 passed); `rtk git diff --check` passed.
- Next: begin the first business feature the owner prioritizes.

## 2026-08-09 July Company Receipt Classification
- Scope: record the owner-confirmed transfer destination for account tail `59324` as company-held cash in the July settlement report.
- Evidence: 錦州173號4樓 room 7 (JACKMILLS), rent NT$4,500 plus water NT$65, total NT$4,565; the former handoff identified it as a pending account-ownership decision.
- Guardrails: update report classification only; do not alter Google Sheets, bank records, or formal databases.
- Planned validation: regenerate the July detailed settlement and confirm the row is classified as 公司 with NT$4,565 included.
- Completed: account `59324` is now classified as company-held cash with the user-confirmed basis; the regenerated report includes the NT$4,565 receipt.

## 2026-08-09 昌裕122巷17號 2026 Payment Reconciliation
- Source: Google Sheet `1fkOeCvSu2zYEwWjAyHd8_7ihGhvdGV0VzhMqEJpxWAE`, `對帳表` (sheet ID `5`).
- Completed: reconciled rooms A, B1, B2, C1, C2, D1, and D2 against `runtime.db`.
- Result: 2026-05 through 2026-07 already contain 20 linked `PaymentRecord` rows whose amounts match the source. D2 2026-07 is unpaid in both systems (NT$7,060), so no payment was fabricated or duplicated.
- Boundary: source payments for 2026-01 through 2026-04 have no corresponding monthly bills in `runtime.db`; several historical sheet contracts also conflict with the current contract records. No unlinked payment was imported.
- Next: if historical January–April accounting is required, create/reconcile the corresponding reviewed monthly bills and contract identity evidence first; the existing dry-run-first importer can then link payments idempotently.

- Scope: require administrator role for property, tenant, contract, and payment operational routes while preserving the existing owner report portal.
- Guardrails: did not alter pre-existing dirty files, formal databases, migrations, Git history, or remote state.
- Validation: `rtk py -3 -m pytest -q tests\\integration\\test_landlord_operational_access.py tests\\integration\\test_landlord_billing_access.py tests\\integration\\test_billing_edit_and_contract_list.py tests\\integration\\test_auth_billing_payments_smoke.py` => `27 passed, 2 skipped`; targeted `git diff --check` passed.

## 2026-09-01 Landlord explicit-access release verification
- Completed: validated the landlord report and operational-access release against the approved rule: a landlord sees only explicitly granted `user_property_accesses`; a zero-grant account gets empty reports and cannot select a property; billing, property, tenant, contract, and payment operations return 403.
- Migration evidence: isolated formal-DB copy completed upgrade → downgrade → upgrade with existing core-table counts unchanged, `integrity_check=ok`, and no foreign-key violations. Rollback deliberately drops the new grant table, so a production rollback must export and restore grants.
- Validation: reporting regression 9 passed; migration scaffolding 10 passed; full integration suite 168 passed, 15 skipped; `git diff --check` passed.
- Next: selectively stage only the landlord-access/report/migration slice, commit, and upload. 已記錄。
