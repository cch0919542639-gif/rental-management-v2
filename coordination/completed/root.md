# root

## 2026-08-01 Daily operational access guard

- Added `admin_required` to all routes under `properties`, `tenants`, `contracts`, and `payments`.
- Added landlord-role regression coverage for all operational GET routes and tenant deletion / contract termination POST routes.
- Files changed: `app/modules/properties/routes.py`, `app/modules/tenants/routes.py`, `app/modules/contracts/routes.py`, `app/modules/payments/routes.py`, and `tests/integration/test_landlord_operational_access.py`.
- Validation: `27 passed, 2 skipped`; targeted `git diff --check` passed.
- Known limitation: users lack an enabled/disabled account field. This requires a separately approved migration because `app/models/user.py` already contains user-owned changes.
- Next: apply the same role boundary to maintenance, electricity, water, and any other non-report operational blueprints after auditing their intended owner access.
# 2026-08-09 System Startup Baseline

- Completed: resumed the existing rental-management rebuild without touching its pre-existing unstaged implementation changes.
- Changed: `coordination/progress/root.md` and this completion record only.
- Validation: `rtk py -3 -m pytest -q tests\\integration\\test_auth_billing_payments_smoke.py` => `1 passed`; `rtk git diff --check` => passed.
- Known limitation: no new business feature was selected by the owner; formal databases, staging data, Git history, and remote state remain untouched.
- Next: prioritize a concrete vertical slice (billing, contracts, payments, maintenance, or owner portal) and implement it with focused regression coverage.
# 2026-08-09 July Company Receipt Classification

- Completed: resolved the pending ownership of transfer account tail `59324` as company-held cash for 錦州173號4樓 room 7 (JACKMILLS): rent NT$4,500 plus water NT$65, total NT$4,565.
- Changed: `scripts/render_july_detailed_settlement.py` and the root progress record; regenerated `D:\CodexRuntime\outputs\july-2026-v4-grouped-forms\2607結算表完整細項-v3.html`.
- Validation: report check confirms the account is labeled 公司, includes `4,565`, and retains the basis `使用者確認：59324 入公司帳`; `rtk git diff --check` passed.
- Boundary: no Google Sheet, bank account, or formal database was written.
# 2026-08-09 昌裕122巷17號 2026 Payment Reconciliation

- Reviewed source: [Google Sheet](https://docs.google.com/spreadsheets/d/1fkOeCvSu2zYEwWjAyHd8_7ihGhvdGV0VzhMqEJpxWAE/edit?gid=5#gid=5), `對帳表` / sheet ID `5`.
- Completed: verified all 20 existing 2026-05–2026-07 linked payment records for rooms A, B1, B2, C1, C2, D1, and D2. Every received amount matches the source; D2 2026-07 remains unpaid in both places.
- No database write: January–April source rows cannot be safely imported because runtime.db has no matching monthly bills and the sheet's historical contract identities do not consistently match current contracts.
- Validation: source sheet metadata plus `對帳表!A1:AE119`; database reconciliation of rooms/contracts/monthly bills/payment records.

# 2026-09-01 Landlord explicit-access release verification

- Completed: verified the owner portal release. Report data is server-filtered exclusively by `user_property_accesses`; zero-grant accounts receive no property rows and unauthorized property selection returns 403. Owners are denied all billing, property, tenant, contract, and payment operations.
- Migration: an isolated copy of the formal database successfully completed `20260724_000002` upgrade → downgrade → upgrade; core data counts remained unchanged, integrity check was `ok`, and foreign-key check was empty.
- Validation: reporting tests 9 passed, migration scaffold tests 10 passed, full integration suite 168 passed with 15 skipped; `git diff --check` passed.
- Known release constraint: migration downgrade drops `user_property_accesses`. Back up/export existing grants before any production rollback, then restore them after re-upgrade. 已記錄。
