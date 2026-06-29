# Incident: ElectricityMeter/ElectricityBill missing property relationship

Date: 2026-06-29
Author: mimo
Severity: Medium
Status: Open

## Description

`ElectricityMeter` and `ElectricityBill` models in `app/models/electricity.py` do not have a `property` relationship, so templates cannot display `property.name` directly.

## Current State

- `electricity/index.html` shows `property_id` (numeric ID) instead of `property.name`
- `water/list.html` was fixed because `WaterBill` has a `property` relationship
- Electricity models lack this relationship

## Impact

- Users see numeric IDs instead of readable property names on electricity pages
- Inconsistent with water list which shows property.name

## Resolution Required

Codex needs to add to `app/models/electricity.py`:
```python
# In ElectricityMeter class:
property = db.relationship("Property", backref="electricity_meters", lazy=True)

# In ElectricityBill class:
property = db.relationship("Property", backref="electricity_bills", lazy=True)
```

Then update `electricity/index.html` to use `meter.property.name` and `bill.property.name`.

## Files Affected

- `app/models/electricity.py` (needs Codex update)
- `app/templates/electricity/index.html` (needs Codex update after model change)
