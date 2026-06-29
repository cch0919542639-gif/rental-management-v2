# Incident: Maintenance Module Trunk Defects Blocking Test Collection

Date: 2026-06-29 09:15  
Filed by: box  
Affected file: `tests/integration/test_maintenance_core_flow.py`

---

## Blocked Test

`test_maintenance_core_flow.py::test_maintenance_create_and_transition_flow` cannot be collected or executed on current `origin/main`.

---

## Root Cause 1: Model Not Exported (TD-01)

**Severity:** 🔴 High — blocks collection entirely

The file `app/models/maintenance.py` exists and defines `class MaintenanceRequest(BaseModel)`, but:

- `app/models/__init__.py` does **not** import or export `MaintenanceRequest`
- `from app.models import MaintenanceRequest` raises `ImportError`

**Fix:** Add two lines to `app/models/__init__.py`:
```python
from app.models.maintenance import MaintenanceRequest
# ...and add "MaintenanceRequest" to __all__
```

---

## Root Cause 2: Routes Missing (TD-02)

**Severity:** 🟡 Medium — test cannot pass even after TD-01 fix

The test expects the following routes to exist:

| Route | Expected status | Actual |
|-------|----------------|--------|
| `POST /maintenance/create` | 200 → redirect | 404 (not registered) |
| `POST /maintenance/<id>/transition/assigned` | 200 → redirect | 404 (not registered) |
| `POST /maintenance/<id>/transition/in_progress` | 200 → redirect | 404 (not registered) |
| `POST /maintenance/<id>/transition/resolved` | 200 → redirect | 404 (not registered) |
| `POST /maintenance/<id>/transition/closed` | 200 → redirect | 404 (not registered) |

Only `GET /maintenance/` (index page) is currently registered.

---

## Workaround

Run tests excluding this file:
```bash
pytest tests/integration -q --ignore=tests/integration/test_maintenance_core_flow.py
```

---

## Recommended Owner

codex (who created `app/models/maintenance.py` and `test_maintenance_core_flow.py`)

---

## Remediation Steps

1. Register `MaintenanceRequest` in `app/models/__init__.py` (TD-01)
2. Implement `/maintenance/create` POST route (TD-02)
3. Implement `/<id>/transition/<status>` POST routes (TD-02)
4. Verify: `pytest tests/integration/test_maintenance_core_flow.py -v`
