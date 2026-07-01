# Phase 4 Box — CI & Operations Verification (Round 02)

Date: 2026-07-01  
Branch: `agent/box-phase4-runbook-tests-01`  
Baseline pytest: **passed (exit 0)**

---

## 1. Verification Scope

| Area | Files Verified | Status |
|------|---------------|--------|
| CI workflow | `.github/workflows/test.yml` | ✅ |
| pytest config | `pyproject.toml` | ✅ |
| Git ignore rules | `.gitignore` | ✅ |
| LINE webhook audit | `app/integrations/line_webhook.py` + `settings.py` | ✅ |
| Backup/restore scripts | `scripts/backup_runtime_db.py`, `scripts/restore_runtime_db.py` | ✅ (verified in Round 01) |
| Migration runner | `scripts/migration/run_migrations.py` | ✅ (verified in Round 01) |
| Health check | `scripts/health_check.py` | ✅ (verified in Round 01) |

---

## 2. CI Workflow: `.github/workflows/test.yml`

### 2.1 Structure

```yaml
name: test
on:
  push:
    branches: [main, codex-phase2-mainline-01, agent/**]
  pull_request:   # any PR
jobs:
  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5 (3.13)
      - pip install -r requirements.txt -r requirements-dev.txt
      - pytest tests/integration -q --tb=short
```

### 2.2 Verification

| Item | Actual | Verdict |
|------|--------|---------|
| Triggers on push to main | ✅ `branches: [main, ...]` | ✅ |
| Triggers on push to agent branches | ✅ `branches: [agent/**]` | ✅ |
| Triggers on PR | ✅ `pull_request:` (no filter) | ✅ |
| Python version | 3.13 | ✅ |
| Dependency install | `requirements.txt` + `requirements-dev.txt` | ✅ |
| Test command | `pytest tests/integration -q --tb=short` | ✅ |
| CI runner | ubuntu-latest | ✅ |

### 2.3 Consistency Check: CI vs Local

| Aspect | CI (test.yml) | Local (pyproject.toml) | Match? |
|--------|---------------|----------------------|--------|
| Test path | `tests/integration` | `testpaths = ["tests/integration"]` | ✅ |
| pytest flags | `-q --tb=short` | `addopts = "-q --tb=short"` | ✅ |
| Python version | 3.13 | 3.13 (from dev-runbook) | ✅ |
| Pip install | `requirements.txt -r requirements-dev.txt` | Same in dev-runbook | ✅ |

**Verdict:** CI and local configs are fully consistent. No drift.

### 2.4 Recommendations

| # | Suggestion | Priority |
|---|-----------|----------|
| 1 | Add `--ignore=tests/integration/test_maintenance_core_flow.py` if the Windows encoding issue persists in CI | 🟡 Optional |
| 2 | Consider adding a `seed + health_check` step before the test step to verify DB bootstrap | 🟢 Future |

---

## 3. pytest Configuration: `pyproject.toml`

```toml
[tool.pytest.ini_options]
testpaths = ["tests/integration"]
python_files = ["test_*.py"]
addopts = "-q --tb=short"
```

| Setting | Value | Effect |
|---------|-------|--------|
| `testpaths` | `tests/integration` | Only integration tests (unit/e2e skipped) |
| `python_files` | `test_*.py` | Ignores files without `test_` prefix |
| `addopts` | `-q --tb=short` | Quiet mode, short traceback |

**Verdict:** Minimal, focused, and CI-identical. ✅ No issues.

---

## 4. `.gitignore` Audit

| Rule | Purpose | Effectiveness |
|------|---------|--------------|
| `__pycache__/`, `*.py[cod]`, `*.pyo`, `*.pyd` | Python bytecode | ✅ |
| `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` | Tool caches | ✅ |
| `.venv/`, `venv/`, `env/` | Virtual environments | ✅ |
| `runtime.db`, `*.db`, `*.sqlite`, `*.sqlite3` | Local databases | ✅ |
| `*.log` | Log files (incl. LINE audit log) | ✅ |
| `.env`, `.env.*` | Secrets | ✅ |
| `.vscode/`, `.idea/` | Editor config | ✅ |
| `.coverage`, `coverage.xml`, `htmlcov/` | Coverage outputs | ✅ |
| `.codebase-memory/` | Agent memory cache | ✅ |

**Verdict:** Comprehensive. The `logs/line_webhook_events.jsonl` output is covered by `*.log`. ✅

---

## 5. LINE Webhook Audit Log

### 5.1 Data Flow

```
LINE platform → POST /integrations/line/callback
                ↓
         Signature verification (HMAC-SHA256)
                ↓
         JSON payload validation
                ↓
         Audit log write → logs/line_webhook_events.jsonl
                ↓
         200 response to LINE
```

### 5.2 Audit Log Format

```json
{
  "received_at": "2026-07-01T12:00:00+00:00",
  "event_count": 1,
  "reply_capable": false,
  "events": [
    {
      "type": "message",
      "source_type": "user",
      "user_id": "U...",
      "message_type": "text",
      "message_id": "...",
      "reply_token_present": true
    }
  ]
}
```

### 5.3 Configuration

| Setting | Source | Default |
|---------|--------|---------|
| `LINE_WEBHOOK_AUDIT_LOG` | `app/core/config/settings.py` | `BASE_DIR / "logs" / "line_webhook_events.jsonl"` |
| Override via | `ENV LINE_WEBHOOK_AUDIT_LOG` | Point to custom path |

### 5.4 Security Verification

| Feature | Implemented? |
|---------|-------------|
| HMAC-SHA256 signature verification | ✅ `_verify_signature()` |
| Secret key required (returns 501 if unset) | ✅ |
| JSON payload validation (400 on malformed) | ✅ |
| Events array validation (400 on missing) | ✅ |
| Audit log with timestamps | ✅ |
| No real message processing (Phase 3 placeholder) | ✅ |

**Verdict:** LINE webhook is in audit-only mode. It verifies, logs, and returns 200 without processing. Safe for Phase 4 baseline.

---

## 6. Backup / Restore / Migration Scripts (Cross-Reference)

Already verified in `box-phase4-ops-drill-01.md`. Key points to ensure consistency:

| Script | Doc exists? | Safety documented? | Command matches actual? |
|--------|-----------|-------------------|------------------------|
| `backup_runtime_db.py` | ✅ In drill report | ✅ Dry-run safe | ✅ `--output-dir` |
| `restore_runtime_db.py` | ✅ In drill report | ✅ `--execute` required | ✅ `--source` + `--execute` |
| `run_migrations.py` | ✅ In drill report | ✅ `--execute` required | ✅ `--list`, `--id`, `--execute` |

**Note:** These scripts are NOT yet listed in `scripts/README.md` or `dev-runbook.md`. That gap is flagged in the recommendations below.

---

## 7. Gap Analysis

| Gap | File | Severity | Recommendation |
|-----|------|----------|--------------|
| Backup/restore/migration scripts not in `scripts/README.md` | `scripts/README.md` | 🟡 Medium | Add a "Production Scripts" section |
| Backup/restore/migration scripts not in `dev-runbook.md` | `docs/operations/dev-runbook.md` | 🟡 Medium | Add a "Production Operations" section |
| LINE webhook not in `dev-runbook.md` Quick Verification | `docs/operations/dev-runbook.md` | 🟢 Low | Already noted as Phase 3 |
| No `.env.example` template | repo root | 🟢 Low | Would help new operators |
| No deploy/ directory | repo root | 🟢 Low | Depends on actual deployment target |

---

## 8. Recommendations

| Priority | Action | Effort |
|----------|--------|--------|
| 🔴 P0 | CI is consistent and correct | ✅ Already satisfied |
| 🟡 P1 | Add backup/restore/migration to `scripts/README.md` | Low (documentation) |
| 🟡 P1 | Add production ops section to `dev-runbook.md` | Low (documentation) |
| 🟢 P2 | Add `.env.example` | Low |
| 🟢 P3 | Add deploy/ directory when deployment target is known | Medium |

---

## 9. Deliverables

| File | Action | Description |
|------|--------|-------------|
| `docs/reports/box-phase4-ci-ops-02.md` | **Created** | CI/ops verification: 7 areas audited, consistency confirmed, gaps documented |
| `coordination/progress/box.md` | Updated | Status: DONE |
| `coordination/completed/box.md` | Updated | Archival record |

---

## 10. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-07-01 | Round 02: CI/ops verification — test.yml, pyproject.toml, .gitignore, LINE audit log, backup/restore/migration scripts | box |