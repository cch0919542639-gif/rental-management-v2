# Phase 4 — RDBMS / Migration / Backup Policy Guard Note

Date: 2026-07-01
Author: reasonix
Branch: `agent/box-phase4-runbook-tests-01`
Baseline Predecessor: `docs/reports/reasonix-phase4-readiness-01.md`
Status: **Proposed** — architecture guard, not implementation order

---

## Executive Summary

Phase 4 readiness guard (`reasonix-phase4-readiness-01.md`) identified **B3** (Alembic/Flask-Migrate) and **B4** (SQLite→RDBMS) as blockers. This note deep-dives into those two items plus their dependency — backup/restore — to produce a concrete, phase-gated policy:

| Decision | Verdict | Phase Gate |
|----------|---------|------------|
| SQLite can ship Phase 4 preview | ✅ **Yes, with conditions** | Phase 4A–4C |
| PostgreSQL cutover required before public launch | ✅ **Yes, blocker** | Phase 5 gate |
| Alembic should replace custom runner before PG cutover | ✅ **Yes, migration must be Alembic-native** | Phase 4D |
| Backup script required before any production use | ✅ **Yes, blocker** | Phase 4B |

---

## 1. SQLite Sustainability Analysis

### 1.1 Current Configuration

```python
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'runtime.db'}")
```

- Default: `sqlite:///<project>/runtime.db`
- Override via: `DATABASE_URL` env var
- Production validation: **warning only** — does NOT block startup

### 1.2 SQLite Production Risks

| Risk | Impact | Mitigation Possible? |
|------|--------|---------------------|
| **No concurrent writes** — SQLite serialises all writes | Single-user dev/administrative use only; 2+ concurrent admin sessions will contend | ⚠️ Partial — WAL mode helps readers but writers still serialise |
| **No connection pool** — SQLAlchemy pooling is a no-op for SQLite | Each request opens a new connection to the same file; no back-pressure | ❌ Not without a DB proxy |
| **No role-based access** — file-level permissions only | Any process that can read the file can read all data | ❌ App-level auth is independent, but DB file security is OS-only |
| **Corruption risk on crash** — SQLite is crash-safe with WAL, but file-system level corruption is unrecoverable | Single-point-of-failure no replica | 🟡 WAL mode + regular backup |
| **No incremental backup** — must `.backup` or `cp` the whole file | Backup window grows with DB size. At 100 MB+ this becomes noticeable | 🟡 `sqlite3 .backup` is online-safe but still O(DB size) |
| **No point-in-time recovery** — no WAL archive or replication | Any backup interval creates a loss window equal to the interval | 🟡 Acceptable for Phase 4 preview if backup interval ≤ 15 min |
| **Storage bound to single VM** — cannot scale vertically beyond disk IO of one host | No horizontal scaling path for the DB layer | ❌ Requires RDBMS cutover |

### 1.3 Phase-by-Phase SQLite Tolerance

| Phase | Scope | SQLite Acceptable? | Condition |
|-------|-------|-------------------|-----------|
| **Phase 4A** | Auth roles, SECRET_KEY fix | ✅ **Yes** — single-developer or admin-only access | No concurrent admin users expected |
| **Phase 4B** | Config, monitoring, backup | ✅ **Yes** — still admin-only | **Backup script must exist** (see §3) |
| **Phase 4C** | Edge features, ADR items | ✅ **Yes** — controlled rollout to ≤5 total users | Daily backup + WAL mode enforced |
| **Phase 4D** | Regression freeze, Alembic migration | ⚠️ **Conditional** — if >5 concurrent users expected, must begin PG cutover | Alembic setup complete; PG connection string configurable |
| **Phase 5** | Public launch, LINE/OCR production | ❌ **BLOCKER** — SQLite must be replaced | PG (or equivalent RDBMS) with connection pool, backup, monitoring |

### 1.4 Decision: SQLite Phase-Out Threshold

> **SQLite is acceptable for Phase 4 development and internal preview, but MUST be replaced with PostgreSQL before Phase 5 public launch.**

The exact trigger to begin cutover is **any one of**:
1. The team expects >5 concurrent users (admins + landlords)
2. The project expects to handle >10 concurrent background jobs (OCR, LINE webhook, sheet sync)
3. First public / external user account is created
4. Any data-loss incident occurs on the SQLite file

If none of the above are true, the cutover can wait until Phase 4D/5 boundary.

---

## 2. Migration Runner & Alembic Integration

### 2.1 Current Migration System

The project already has a **custom migration runner** (`scripts/migration/`):

| Component | Purpose | Write Capability |
|-----------|---------|-----------------|
| `run_migrations.py` | CLI runner: `--list`, `--execute`, `--id` | Dispatches `apply_*` scripts |
| `_registry.py` | Discovers `apply_*.py`, tracks applied IDs in `schema_migration_log` table | Creates/reads `schema_migration_log` |
| `_common.py` | `build_script_app()` — creates a Flask app for migration context | Read-only (helper) |
| `migration_index.py` | Human-readable index of all scripts | Read-only |
| `apply_*.py` | Individual migration scripts (one exists: `apply_20260701_000001_phase4_baseline_marker.py`) | Each defines `run_migration(context)` |

### 2.2 Current Runner Strengths

- ✅ **Idempotent** — already skips applied migrations by checking `schema_migration_log`
- ✅ **Dry-run mode** — `--execute` flag required for actual writes
- ✅ **SQLite-native** — works today with SQLite
- ✅ **Zero config** — auto-discovers `apply_*.py` files

### 2.3 Current Runner Limitations (vs Alembic)

| Gap | Current Runner | Alembic | Impact |
|-----|---------------|---------|--------|
| Schema diff generation | Manual — developer writes raw SQL | Automatic — `--autogenerate` detects model changes | Time + human error |
| Reversibility | Not built-in — each script must implement its own rollback | Built-in `downgrade()` per revision | Rollback is ad-hoc |
| Dependency ordering | Filename sort only (`apply_YYYYMMDD_NNNNN_*.py`) | Explicit `revision` / `down_revision` DAG | Risk of wrong order |
| Branching / merge | Not supported | Built-in branch labels | Team collaboration |
| PG/MySQL compatibility | SQL written by hand — may not be portable | SQLAlchemy DDL renders dialect-specific SQL | Portability |
| Ecosystem tooling | None | `flask db upgrade`, `flask db migrate`, `flask db history` | Developer convenience |

### 2.4 Integration Strategy: Custom → Alembic Bridge

For Phase 4, the recommended approach is a **bridge strategy** that preserves existing investment while paving the path to Alembic:

```
Phase 4A ─► Phase 4B ─► Phase 4C ─► Phase 4D
  │                        │               │
  ▼                        ▼               ▼
Custom runner only    Add Alembic         Alembic-only
(no change)           alongside custom    run_migrations.py
                      (bridge mode)       deprecated
```

#### Phase 4A–4C: Custom Runner Continues

- Keep `run_migrations.py` as the active migration runner
- New `apply_*` scripts continue to be added under the existing system
- Each migration script should include an Alembic-compatible docstring for future import:

```python
# Alembic migration candidate: revision=XXXX_description
```

#### Phase 4C: Alembic Bootstrapping

Steps:
1. Install `Flask-Migrate` (wraps Alembic for Flask)
2. Run `flask db init` to create `migrations/` directory
3. Run `flask db migrate -m "baseline"` to generate the first Alembic revision reflecting current models
4. **Do NOT run `flask db upgrade` yet** — the custom runner remains responsible

The initial Alembic revision should use the **`schema_migration_log` table's latest applied ID as the Alembic `base` revision marker**.

#### Phase 4D: Cutover to Alembic

1. Write a **bridge migration** (custom runner style) that stamps Alembic's revision table:
   - Creates Alembic's `alembic_version` table
   - Inserts the latest revision ID so Alembic believes it's up-to-date

2. Create a final `apply_*` script that:
   - Runs `alembic.stamp('head')` to mark Alembic baseline
   - Records itself in `schema_migration_log` as the last custom migration

3. After bridge is applied:
   - `run_migrations.py --list` should show "bridge" as the last applied
   - `flask db current` should show Alembic's `head` revision
   - All **future** schema changes use `flask db migrate` + `flask db upgrade`

4. Set `DATABASE_URL` to PostgreSQL connection string (see §2.5)

5. Deprecate `run_migrations.py` (keep as reference, remove from active use)

### 2.5 PostgreSQL Connection Config

After cutover, the connection string format:

```env
DATABASE_URL=postgresql://user:password@host:5432/rental_rebuild
```

Corresponding config update (in `settings.py`):

```python
# Production only:
class ProductionConfig(BaseConfig):
    # Inherits BaseConfig which defaults to sqlite:///runtime.db
    # Override via DATABASE_URL env var
    # Additional PG-specific settings:
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 5,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }
```

**Important**: PostgreSQL engine options (`pool_size`, `pool_pre_ping`) should only be applied when the DB is actually PostgreSQL. A future config class `PostgreSQLConfig` or dynamic detection in `ProductionConfig` is the recommended approach.

### 2.6 Decision: Migration Runner Policy

| Rule | Policy |
|------|--------|
| **Phase 4A–4C** | Use `run_migrations.py` — do NOT add Alembic yet |
| **Phase 4C (prep)** | `flask db init` + `flask db migrate` — dry-run only, no upgrade |
| **Phase 4D** | Bridge migration → Alembic active → custom runner deprecated |
| **Phase 5** | Alembic-only; `run_migrations.py` and `apply_*` scripts archived |

---

## 3. Backup / Restore Minimum Requirements

### 3.1 Current State

| Aspect | Status | Risk |
|--------|--------|------|
| Backup script | ❌ **Does not exist** | 🔴 **BLOCKER for Phase 4B+** |
| Restore procedure | ❌ **Not documented** | 🔴 **BLOCKER for Phase 4B+** |
| Disaster recovery plan | ❌ **Not documented** | 🔴 Raised in readiness report |
| WAL mode | Not enforced in config | 🟡 SQLite default is `delete` mode |

### 3.2 Minimum Viable Backup (Phase 4B Gate)

Before any production-adjacent use (even internal preview), the following backup mechanism MUST be in place:

#### 3.2.1 Enforce WAL Mode

Add to `create_app()` or `db.init_app()`:

```python
@db.event.listens_for(db.engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if hasattr(dbapi_connection, "execute"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()
```

This allows concurrent readers without writer blocking, and provides crash recovery.

#### 3.2.2 Backup Script (`scripts/ops/backup_runtime_db.sh` / `.bat`)

A backup script must:

1. Call `sqlite3 /path/to/runtime.db ".backup /path/to/backups/runtime_$(date +%Y%m%d_%H%M%S).db"`
2. Keep the last 7 daily backups and 4 weekly backups
3. Log success/failure to a `logs/backup.log`
4. Exit non-zero on failure (so monitoring can detect)

Minimum schedule: **Every 15 minutes during active use; every hour during idle.**

For Windows environments where `sqlite3.exe` may not be on PATH, provide a Python equivalent:

```python
"""scripts/ops/backup_runtime_db.py — Online-safe SQLite backup."""
import shutil
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path("runtime.db")
BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

def backup():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"runtime_{ts}.db"
    shutil.copy2(DB_PATH, dest)
    print(f"Backup saved: {dest}")

    # Prune: keep last 7 daily
    dailies = sorted(BACKUP_DIR.glob("runtime_*.db"))
    for old in dailies[:-7]:
        old.unlink()
    print(f"Pruned to 7 most recent backups.")

if __name__ == "__main__":
    backup()
```

> **Note**: For SQLite, `shutil.copy2()` while the DB is in WAL mode is safe for crash recovery (WAL checkpoint will replay on next open). For production-grade backup under write load, use `sqlite3 .backup` which serialises the backup transaction. The Python wrapper with `subprocess` calling `sqlite3.exe .backup` is the recommended long-term approach.

#### 3.2.3 Restore Procedure (Minimum)

Document in `docs/operations/disaster-recovery.md`:

```markdown
## SQLite Restore

1. Stop the application (ensure no open connections to runtime.db)
2. `cp backups/runtime_<TIMESTAMP>.db runtime.db`
3. Restart the application
4. Verify: login, check latest contract/bill

## PostgreSQL Restore (future)

1. `pg_restore -d rental_rebuild backup.dump`
2. Run Alembic migrations: `flask db upgrade`
3. Verify with smoke test
```

### 3.3 PostgreSQL Backup (Future)

Once migrated to PostgreSQL, backup strategy upgrades to:

| Feature | Method | Schedule |
|---------|--------|----------|
| Full dump | `pg_dump` | Daily |
| Point-in-time recovery | WAL archive + `pg_basebackup` | Continuous |
| Automated restore test | Restore to staging DB weekly | Weekly |

### 3.4 Decision: Backup Policy

| Phase | Requirement |
|-------|-------------|
| **Phase 4A** | No backup script required (single-dev testing) |
| **Phase 4B Gate** | ⛔ **Backup script MUST exist** (`scripts/ops/backup_runtime_db.py` or `.bat`) |
| **Phase 4B+** | Backup runs every 15 min; WAL mode enforced |
| **Phase 4D+** | Restore procedure documented in `docs/operations/disaster-recovery.md` |
| **Phase 5** | PostgreSQL pg_dump/pg_basebackup with point-in-time recovery |

---

## 4. Phase Gate Summary

| Gate | SQLite | Migration Runner | Backup |
|------|--------|------------------|--------|
| **Phase 4A** | ✅ OK | Custom runner only | ❌ Not required |
| **Phase 4B** | ✅ OK (WAL mode enforced) | Custom runner only | ✅ **Backup script mandatory** |
| **Phase 4C** | ✅ OK (≤5 users) | Custom runner + `flask db init` (dry-run) | ✅ 15-min schedule |
| **Phase 4D** | ⚠️ Begin PG cutover if >5 users | **Bridge migration → Alembic active** | ✅ Restore doc mandatory |
| **Phase 5** | ❌ **Must migrate to PostgreSQL** | Alembic only | ✅ pg_dump + PITR |

### Blocker Checklist (Before Phase 4B can be considered complete)

- [ ] `scripts/ops/backup_runtime_db.py` exists and runs successfully
- [ ] WAL mode is enforced via SQLAlchemy event listener or `config.py`
- [ ] Backup schedule is set (cron / Task Scheduler)
- [ ] First successful backup file exists in `backups/`

### Blocker Checklist (Before Phase 4D can be considered complete)

- [ ] Alembic `migrations/` directory initialized with `flask db init`
- [ ] Initial Alembic revision generated (`flask db migrate`) — dry-run verified
- [ ] Bridge migration script written and tested in staging
- [ ] PostgreSQL connection string tested (with `pool_size`/`pool_pre_ping`)
- [ ] `docs/operations/disaster-recovery.md` written with restore procedure
- [ ] `run_migrations.py --list` run as final verification after bridge

### Blocker Checklist (Before Phase 5 launch)

- [ ] PostgreSQL instance provisioned (credentials in env vars, not code)
- [ ] Alembic migration applied to PostgreSQL: `flask db upgrade`
- [ ] All data verified migrated (row count parity, smoke test)
- [ ] `run_migrations.py` removed from active use, archived to `scripts/archive/`
- [ ] SQLite `runtime.db` file retained as read-only backup (30-day retention)
- [ ] `pg_dump` cron job active

---

## 5. Risk Notes

| ID | Risk | Severity | Mitigation |
|----|------|----------|------------|
| R1 | Bridge migration fails and Alembic cannot reconcile schema log | HIGH | Keep custom runner operational until Alembic upgrade is verified. Do not delete any custom `apply_*` files until Phase 5 is complete. |
| R2 | PG connection string stored in env var, not validated at startup | MEDIUM | Add `_is_postgresql()` detection in `validation.py` — production should emit error if `DATABASE_URL` is still SQLite. |
| R3 | Backup script runs while a long write transaction is in progress | MEDIUM | WAL mode ensures `shutil.copy2()` sees a consistent snapshot. For extra safety, add `PRAGMA busy_timeout=5000` before backup. |
| R4 | Team adds new migration via Alembic before bridge is applied, causing two migration systems to conflict | HIGH | **Rule: no Alembic `flask db upgrade` before bridge migration is applied.** During Phase 4C, `flask db migrate` is allowed for revision generation ONLY (dry-run). |
| R5 | `.backup` SQLite command locks the DB for the duration | LOW | Use `sqlite3 .backup` which is an online backup command; it does NOT block readers/writers. The Python `shutil.copy2` fallback also reads without locks in WAL mode. |

---

## Appendices

### A. Quick-Reference: Migration Script Naming Convention

```
apply_YYYYMMDD_NNNNN_short_description.py
# Example:
apply_20260701_000001_phase4_baseline_marker.py
```

- `YYYYMMDD` — date the migration was created
- `NNNNN` — sequence number (00001, 00002, ...)
- No two migrations on the same date should share the same sequence number

### B. Quick-Reference: Alembic Commands (Phase 4D+)

```bash
flask db init              # One-time: creates migrations/ directory
flask db migrate -m "msg"  # Generate new revision from model changes
flask db upgrade           # Apply pending revisions
flask db downgrade         # Rollback last revision
flask db history           # Show revision history
flask db current           # Show current revision
```

### C. References

- `docs/reports/reasonix-phase4-readiness-01.md` — upstream guard note (B3, B4)
- `scripts/migration/run_migrations.py` — current custom migration runner
- `scripts/migration/_registry.py` — migration discovery & log table management
- `app/core/config/settings.py` — `SQLALCHEMY_DATABASE_URI` default
- `app/core/config/validation.py` — production SQLite warning

---

*End of Phase 4 DB Migration Guard Note*
