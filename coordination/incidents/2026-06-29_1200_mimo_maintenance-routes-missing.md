# Incident: Maintenance module missing create/edit/transition routes

Date: 2026-06-29
Author: mimo
Severity: High
Status: Open

## Description

The `maintenance` module currently only has a room snapshot index page. The `maintenance-contract.md` defines a full MaintenanceRequest entity with status machine, but:
1. No create/edit/transition routes exist
2. No MaintenanceRequest CRUD operations
3. No status transition logic

## Current State

- `maintenance/index.html` shows room snapshot only
- `maintenance/form.html` exists but has no routes
- `maintenance/model.py` has `MaintenanceRequest` model
- `maintenance/routes.py` only has `maintenance_index()`

## Contract Requirements (from maintenance-contract.md)

Minimum first version should support:
1. Create maintenance request
2. Assign handler
3. Start work
4. Mark resolved
5. Close request

Status machine:
- reported → assigned → in_progress → resolved → closed
- reported → cancelled
- assigned → cancelled

## Resolution Required

Codex needs to:
1. Create routes for create/edit/transition
2. Implement MaintenanceService CRUD operations
3. Add status transition logic
4. Update templates for full CRUD

## Files Affected

- `app/modules/maintenance/routes.py` (needs Codex update)
- `app/services/maintenance_service.py` (needs Codex update)
- `app/templates/maintenance/index.html` (needs Codex update)
- `app/templates/maintenance/form.html` (already exists, needs routes)
