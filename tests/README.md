# tests

測試分成 `unit`、`integration`、`e2e`。

## Integration Tests (Phase 2)

| Test File | Coverage | Active |
|-----------|----------|--------|
| `test_auth_billing_payments_smoke.py` | Auth, dashboard, billing list, payment CRUD (create → verify → link) | ✅ |
| `test_utilities_reporting_smoke.py` | Electricity meter/bill/reading/calculate/post, water create/post, reports monthly, maintenance page | ✅ |
| `test_billing_placeholders_and_edges.py` | Billing edge cases (no-data month, default month) + placeholders for deeper billing tests | ✅ |
| `test_payments_reject_and_status.py` | Payment reject flow, list rendering + placeholders for duplicate TXN, reconciliation | ✅ |
| `test_electricity_meter_edit_and_post.py` | Meter edit, bill + reading → calculate → post to monthly bill + placeholders for status transitions | ✅ |
| `test_water_edit_and_independent_post.py` | Water bill edit, independent mode post, landlord summary, yearly overview + placeholders | ✅ |

## Placeholders

Several test files contain `@pytest.mark.skip` placeholders marked with "TBD".
These serve as documented entry points for deeper algorithm tests in Phase 3+.

## 執行

```powershell
pytest tests\integration -q
```
> ℹ️ On some systems `python` resolves to Python 3.11 (Hermes venv) without Flask.
> If the above fails, use `py -3 -m pytest tests\integration -q` or ensure `pytest` is on PATH for Python 3.13.
