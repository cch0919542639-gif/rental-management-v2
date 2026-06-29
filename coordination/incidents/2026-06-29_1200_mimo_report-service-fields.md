# Incident: report_service missing public_electricity and other_desc

Date: 2026-06-29
Author: mimo
Severity: Medium
Status: Open

## Description

`app/services/report_service.py` monthly_report() method does not return `public_electricity` or `other_desc` fields, even though:
1. `MonthlyBill` model has both fields
2. `app/repositories/report_repository.py` now queries both fields
3. `app/templates/reports/monthly.html` expects both fields

## Impact

- Monthly report template will throw `UndefinedError` for `row.public_electricity` and `row.other_desc`
- Cannot fix without modifying `app/services/*` (out of scope for mimo)

## Resolution Required

Codex needs to add to `report_service.py` monthly_report() dict:
```python
"other_desc": row.other_desc,
"public_electricity": row.public_electricity,
```

## Files Affected

- `app/repositories/report_repository.py` (modified by mimo — fields added to query)
- `app/services/report_service.py` (needs Codex update)
- `app/templates/reports/monthly.html` (modified by mimo — columns added)
