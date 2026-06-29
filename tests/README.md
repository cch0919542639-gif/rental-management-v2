# tests

測試分成 `unit`、`integration`、`e2e`。

## Integration Tests (Phase 2 Final — 22 files, 38 active, 15 skip)

| # | Test File | Active | Skip | Coverage | Author |
|---|-----------|--------|------|----------|--------|
| 1 | `test_auth_billing_payments_smoke.py` | 1 | 0 | Auth, dashboard, billing list, payment CRUD | box R1 |
| 2 | `test_billing_edit_and_contract_list.py` | 2 | 2 | Billing edit (total recalc), contract list page | box R2 |
| 3 | `test_billing_generate_flow.py` | 1 | 0 | Billing create, toggle-paid, generate, batch | open |
| 4 | `test_billing_monthly_bill_flow.py` | 1 | 0 | Billing view + payment linking | open |
| 5 | `test_billing_placeholders_and_edges.py` | 2 | 2 | Billing edge cases (no-data, default month) | box R1 |
| 6 | `test_billing_utility_algorithms.py` | 2 | 0 | Electricity rate fallback, water shared alloc | open |
| 7 | `test_billing_year_month_edges.py` | 4 | 2 | YYYYMM/YYYY-MM format, UI→DB storage | box R2 |
| 8 | `test_electricity_calculation_and_posting.py` | 1 | 0 | Electricity calculate + idempotency | mimo |
| 9 | `test_electricity_meter_edit_and_post.py` | 2 | 2 | Meter edit, bill→post to monthly bill | box R1 |
| 10 | `test_electricity_property_detail.py` | 1 | 0 | Property detail page (summary, meters, bills) | codex |
| 11 | `test_electricity_property_workflows.py` | 1 | 0 | new-bill → quick-reading → reading-log flow | codex |
| 12 | `test_electricity_water_edge_cases.py` | 3 | 2 | Water min/large amounts, multi-bill same meter | box R2 |
| 13 | `test_low_risk_crud_and_filters.py` | 2 | 0 | Property filter, low-risk delete | open R2 |
| 14 | `test_maintenance_core_flow.py` | 1 | 0 | Maintenance create + status transitions | codex |
| 15 | `test_maintenance_filters_and_summary.py` | 1 | 0 | Maintenance filters, open view, room list | codex |
| 16 | `test_maintenance_readiness.py` | 2 | 2 | Maintenance page, room_snapshot struct | box R2 |
| 17 | `test_nested_creation_routes.py` | 2 | 0 | Nested property→landlord, room→property | codex |
| 18 | `test_payments_reject_and_status.py` | 2 | 2 | Payment reject flow, list rendering | box R1 |
| 19 | `test_reports_maintenance_summary.py` | 1 | 0 | Maintenance summary report | codex |
| 20 | `test_reports_monthly_and_landlord_summary.py` | 1 | 0 | Monthly report with payment + paid status | mimo |
| 21 | `test_utilities_reporting_smoke.py` | 1 | 0 | Electricity/water/reports/maintenance smoke | open |
| 22 | `test_water_edit_and_independent_post.py` | 4 | 1 | Water edit, independent post, reports | box R1 |
| | **Total** | **38** | **15** | | |

## Skip Breakdown

| Category | Count | Detail |
|----------|-------|--------|
| Phase 3+ deferred | 13 | Algorithm-dependent tests for deeper billing, electricity, water, payments |
| Empty stubs (coverage in core_flow) | 2 | maintenance_request_create, maintenance_status_workflow |
| Activable now | **0** | None |

## 執行

```powershell
pytest tests\integration -q
.\scripts\run_tests.bat
.\scripts\run_single_test.bat test_electricity_property_workflows.py
```
