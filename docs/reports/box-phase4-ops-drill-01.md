# Phase 4 Box — Operations Drill Report (Round 01)

Date: 2026-07-01  
Branch: `agent/box-phase4-runbook-tests-01`  
Baseline pytest: **70 passed, 15 skipped, 0 failures**

---

## 1. Drill Objective

Verify the usage flow of 4 operational scripts under realistic conditions. Record each step's inputs, outputs, exit codes, and safety properties.

---

## 2. Operation Matrix

| # | Script | Mode | Safety | Dry-run? | Execute? | Writes? |
|---|--------|------|--------|----------|----------|---------|
| 1 | `health_check.py` | Read-only check | 🔵 Safe | N/A | N/A | ❌ No |
| 2 | `backup_runtime_db.py` | File copy | 🔵 Safe | N/A | Always writes backup | ✅ Yes (backup file) |
| 3 | `restore_runtime_db.py` | File restore | 🟡 Dry-run by default | ✅ Default | `--execute` | ⚠️ Only with `--execute` |
| 4 | `run_migrations.py` | Migration runner | 🟡 Dry-run by default | ✅ Default | `--execute` | ⚠️ Only with `--execute` |

---

## 3. Drill Log

### 3.1 health_check.py

```powershell
py -3 .\scripts\health_check.py --config default
```

| Check | Result | Note |
|-------|--------|------|
| Flask app created | ✅ PASS | |
| Database connection | ✅ PASS | |
| 14 required tables | ✅ PASS | user, landlords, properties, rooms, tenants, contracts, etc. |
| Admin user found | ✅ PASS | seed had been run |
| Active contracts | ✅ PASS | 1 active contract |
| SECRET_KEY | ⚠️ FAIL | Using default — expected in dev |
| Database URI | ✅ PASS | sqlite:///...runtime.db |
| **Exit code** | **1** | Expected — SECRET_KEY default in dev |

**Verdict:** ✅ Pass. The 1 failure is the expected SECRET_KEY warning for local development.

### 3.2 backup_runtime_db.py

```powershell
py -3 .\scripts\backup_runtime_db.py --output-dir backups
```

| Item | Value |
|------|-------|
| Source | `runtime.db` |
| Backup created | `backups/runtime_20260701_131139.db` |
| Timestamp format | `YYYYMMDD_HHMMSS` |
| Exit code | 0 |
| Safety | 🔵 Creates copy, does not modify source |

**Verdict:** ✅ Pass. Backup created successfully with timestamped filename.

### 3.3 restore_runtime_db.py (Dry-Run)

```powershell
py -3 .\scripts\restore_runtime_db.py --source backups/runtime_20260701_131139.db
```

| Item | Value |
|------|-------|
| Mode | DRY-RUN |
| Source | `backups/runtime_20260701_131139.db` |
| Target | `runtime.db` |
| Exit code | 0 |
| Actual write? | ❌ No — dry-run only |

**Verdict:** ✅ Pass. Dry-run correctly reports the intended operation without writes.

**To actually restore:** `py -3 .\scripts\restore_runtime_db.py --source backups/runtime_*.db --execute`

### 3.4 run_migrations.py --list (Before)

```powershell
py -3 .\scripts\migration\run_migrations.py --list
```

| Migration ID | Status |
|-------------|--------|
| `20260701_000001_phase4_baseline_marker` | [pending] |

**Verdict:** ✅ Pass. 1 migration discovered, correctly reported as pending.

### 3.5 run_migrations.py --execute

```powershell
py -3 .\scripts\migration\run_migrations.py --execute
```

| Step | Result |
|------|--------|
| Bootstrap app | ✅ |
| Ensure schema_migration_log table | ✅ Created if not exists |
| Run `20260701_000001_phase4_baseline_marker` | ✅ Applied |
| Record in log table | ✅ INSERT executed |
| Exit code | 0 |

**Verdict:** ✅ Pass. Migration executed and recorded in `schema_migration_log`.

### 3.6 run_migrations.py --list (After)

```powershell
py -3 .\scripts\migration\run_migrations.py --list
```

| Migration ID | Status |
|-------------|--------|
| `20260701_000001_phase4_baseline_marker` | [applied] |

**Verdict:** ✅ Pass. Status changed from [pending] to [applied] after execution.

### 3.7 Re-run --execute (Idempotency)

```powershell
py -3 .\scripts\migration\run_migrations.py --execute
```

| Migration | Result |
|-----------|--------|
| `20260701_000001_phase4_baseline_marker` | Skipped: already applied |

**Verdict:** ✅ Pass. Re-running is safe — already-applied migrations are skipped.

---

## 4. Script Usage Reference

### 4.1 health_check.py

```powershell
# Quick check (uses default config)
py -3 .\scripts\health_check.py

# Production config check (will fail on SECRET_KEY if not set)
py -3 .\scripts\health_check.py --config production
```

**Note:** `--config production` validates SECRET_KEY, SESSION_COOKIE_SECURE, and other production requirements. Use this before deployment.

### 4.2 backup_runtime_db.py

```powershell
# Backup to default directory (backups/)
py -3 .\scripts\backup_runtime_db.py

# Backup to custom directory
py -3 .\scripts\backup_runtime_db.py --output-dir D:\rental\backups
```

### 4.3 restore_runtime_db.py

```powershell
# Dry-run (safe default)
py -3 .\scripts\restore_runtime_db.py --source backups\runtime_20260701_131139.db

# Execute restore (overwrites runtime.db)
py -3 .\scripts\restore_runtime_db.py --source backups\runtime_20260701_131139.db --execute
```

**Important:** Stop the server before restore. Run health check after.

### 4.4 run_migrations.py

```powershell
# List all migrations with status
py -3 .\scripts\migration\run_migrations.py --list

# Run all pending migrations (dry-run first)
py -3 .\scripts\migration\run_migrations.py --execute

# Run a specific migration only
py -3 .\scripts\migration\run_migrations.py --id 20260701_000001_phase4_baseline_marker --execute
```

---

## 5. Safety Summary

| Script | Default | Destructive? | Safe to run anytime? |
|--------|---------|-------------|---------------------|
| `health_check.py` | Read-only check | ❌ No | ✅ Yes |
| `backup_runtime_db.py` | Creates backup file | ✅ Yes (backup copy) | ✅ Yes (non-destructive to source) |
| `restore_runtime_db.py` | Dry-run | ⚠️ Only with `--execute` | ✅ Yes (default) |
| `run_migrations.py` | Dry-run | ⚠️ Only with `--execute` | ✅ Yes (default) |

---

## 6. Idempotency & Error Handling

| Scenario | Script | Behavior |
|----------|--------|----------|
| Backup when DB missing | `backup_runtime_db.py` | `SystemExit("Database file not found")` |
| Restore when source missing | `restore_runtime_db.py` | `SystemExit("Backup source not found")` |
| Migration re-run | `run_migrations.py` | Skips already-applied migrations |
| Restore without `--execute` | `restore_runtime_db.py` | Prints summary, no write |
| Unknown migration ID | `run_migrations.py` | `SystemExit("Unknown migration id: ...")` |
| Non-SQLite DATABASE_URL | Both backup/restore | `SystemExit("only supports sqlite:///")` |

---

## 7. Head-to-Head Comparison: Dry-Run vs Execute

| Script | Dry-run behavior | Execute difference |
|--------|-----------------|-------------------|
| `restore_runtime_db.py` | Prints source/target, no copy | `shutil.copy2(source, target)` |
| `run_migrations.py` | Calls `run_migration(context)` with `execute=False` | Calls with `execute=True`, then records in `schema_migration_log` |

---

## 8. Baseline Verification (Post-Drill)

```bash
pytest tests/integration -q
→ 70 passed, 15 skipped, 0 failures
```

All integration tests pass. The `schema_migration_log` table created by the drill does not affect application logic.

---

## 9. Deliverables

| File | Action | Description |
|------|--------|-------------|
| `docs/reports/box-phase4-ops-drill-01.md` | **Created** | Full operations drill report with matrix, logs, and safety analysis |
| `coordination/progress/box.md` | Updated | Status: DONE |
| `coordination/completed/box.md` | Updated | Archival record |

---

## 10. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-07-01 | Round 01: Operations drill for health_check, backup, restore, run_migrations. All 4 scripts verified. | box |