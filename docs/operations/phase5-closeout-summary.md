# Phase 5 Closeout Summary

Last Updated: 2026-07-02

## Status

Phase 5 主幹已完成到「可 rehearsal、不可直接 production cutover」的狀態。

目前已具備：

- PostgreSQL / Alembic scaffold
- custom runner → Alembic bridge guard
- SQLite export drill
- target schema preparation
- CSV import drill
- row parity verification
- bridge rehearsal checklist
- rehearsal evidence bundle
- cutover checklist
- rollback checklist
- operator env template 與 operator runbook

目前尚未執行：

- 正式 PostgreSQL production cutover
- 正式 Alembic bridge execute
- production target 實際資料導入

## Verified Baseline

最新主幹驗證基線：

```text
pytest tests\integration --disable-warnings
92 passed, 15 skipped
```

這個數字是目前 Phase 5 closeout 的有效基線。

## Delivered Components

### 1. Bridge / Migration Boundary

- `scripts/migration/run_migrations.py`
- `scripts/migration/_registry.py`
- `scripts/migration/apply_20260701_000001_phase4_baseline_marker.py`
- `scripts/migration/apply_20260701_000002_alembic_bridge.py`
- `alembic.ini`
- `app/migrations/env.py`

### 2. Drill Toolchain

- `scripts/migration/export_sqlite_to_pg.py`
- `scripts/migration/prepare_target_db.py`
- `scripts/migration/import_csv_to_target.py`
- `scripts/migration/verify_row_parity.py`
- `scripts/migration/bridge_drill_checklist.py`
- `scripts/migration/write_rehearsal_evidence.py`

### 3. Operator Documents

- `docs/operations/phase5.env.example`
- `docs/operations/phase5-bridge-drill.md`
- `docs/operations/phase5-cutover-checklist.md`
- `docs/operations/phase5-rollback-checklist.md`
- `docs/operations/phase5-operator-runbook.md`

## What Operators May Do Now

允許：

1. 跑 PostgreSQL tooling preflight
2. 跑 SQLite export drill
3. 準備 rehearsal target schema
4. 做 CSV import rehearsal
5. 做 row parity 驗證
6. 產出 evidence bundle
7. 反覆 rehearsal，直到流程穩定

不允許：

1. 未經明確批准直接執行 Alembic bridge
2. 未做 backup 就直接操作 target
3. 跳過 row parity 驗證
4. 跳過 evidence bundle
5. 在 production target 手動修表 / 補資料

## Remaining Phase 5 Gaps

以下項目仍未完成，且不應在本次主幹結案時假裝已完成：

### A. Formal Cutover Execution

- 真正的 PostgreSQL target 環境
- 真正的 cutover 視窗
- 真正的 `--allow-bridge` 執行紀錄

### B. Production DB Operations

- PostgreSQL HA / PITR / managed backup policy
- production monitoring / alert routing
- production secret distribution

### C. External Integrations Go-Live

- OCR provider 正式實作上線
- LINE webhook 正式實作上線
- Sheets/匯出整合的 production policy

## Recommended Next Step

若要繼續往下推，不要再擴主幹功能面，應改成下面順序：

1. 建立一個真實 rehearsal target PostgreSQL 實例
2. 用 `phase5-operator-runbook.md` 跑完整 rehearsal
3. 保存 evidence bundle
4. 檢查 cutover / rollback checklist
5. 再決定是否進入正式 cutover 視窗

## Handoff Rule

後續任何 agent / 人員接手前，至少先讀：

- `docs/operations/phase5-closeout-summary.md`
- `docs/operations/phase5-operator-runbook.md`
- `docs/operations/phase5-cutover-checklist.md`
- `docs/operations/phase5-rollback-checklist.md`

若缺少這四份閱讀，視為未完成交接。
