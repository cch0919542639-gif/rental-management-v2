# Phase 2 Closeout And Push Scope

Date: 2026-06-29
Owner: Codex
Branch: `codex-phase2-mainline-01`
Current Verified Baseline: `44 passed, 15 skipped`

## Purpose

這份文件用來整理：

- Phase 2 已完成的正式收尾範圍
- 建議如何拆 commit
- 哪些檔案應一起 push
- 哪些檔案屬可選文件吸收，不必阻擋主幹提交

## Phase 2 Closeout Verdict

Phase 2 主幹可視為已完成收斂，理由如下：

- `nested creation` 已進主幹
- `maintenance Phase 2B` 已進主幹
- `electricity property detail / new-bill / quick-reading / reading-log` 已進主幹
- 正式 HTML error pages 已進主幹
- `scripts/migration/migration_index.py` 已進主幹
- `scripts/repair/*.py` 4 支已進主幹
- `app/integrations/` skeleton 已進主幹
- 最新 integration baseline 已穩定：`44 passed, 15 skipped`
- `open` 已確認無 blocking gap
- `reasonix` 已確認 migration / integration boundary 合規
- `mimo` 已確認 UI regression 無阻塞
- `box/hermes` 已補 runbook / matrix / usage docs

## Recommended Commit Split

建議拆成兩個主 commit，加一個可選文件 commit。

### Commit A — Phase 2 Mainline Features

建議訊息：

```text
feat: complete phase2 mainline workflows and integration boundaries
```

建議包含：

- `app/core/errors/handlers.py`
- `app/models/__init__.py`
- `app/modules/__init__.py`
- `app/modules/electricity/forms.py`
- `app/modules/electricity/routes.py`
- `app/modules/maintenance/routes.py`
- `app/modules/properties/routes.py`
- `app/modules/reports/routes.py`
- `app/modules/rooms/routes.py`
- `app/repositories/electricity_repository.py`
- `app/repositories/maintenance_repository.py`
- `app/repositories/report_repository.py`
- `app/services/electricity_service.py`
- `app/services/maintenance_service.py`
- `app/services/report_service.py`
- `app/integrations/README.md`
- `app/integrations/__init__.py`
- `app/integrations/ocr_client.py`
- `app/integrations/sheets_client.py`
- `app/integrations/line_webhook.py`
- `app/templates/electricity/property_reading_form.html`
- `app/templates/errors/404.html`
- `app/templates/errors/500.html`
- `app/templates/errors/app_error.html`
- `app/templates/landlords/list.html`
- `app/templates/payments/list.html`
- `app/templates/properties/form.html`
- `app/templates/properties/list.html`
- `app/templates/rooms/form.html`
- `scripts/migration/maintenance_legacy_scan.py`
- `scripts/migration/migration_index.py`
- `scripts/migration/README.md`
- `scripts/repair/README.md`
- `scripts/repair/year_month_audit.py`
- `scripts/repair/room_status_audit.py`
- `scripts/repair/contract_expiry_repair.py`
- `scripts/repair/user_table_audit.py`
- `tests/integration/test_electricity_property_detail.py`
- `tests/integration/test_electricity_property_workflows.py`
- `tests/integration/test_error_pages_and_migration_index.py`
- `tests/integration/test_maintenance_filters_and_summary.py`
- `tests/integration/test_nested_creation_routes.py`
- `tests/integration/test_repair_scripts_and_integrations_boundary.py`
- `tests/integration/test_reports_maintenance_summary.py`
- `tests/integration/test_electricity_calculation_and_posting.py`
- `tests/integration/test_utilities_reporting_smoke.py`

### Commit B — Runbook, Dispatch, Coordination

建議訊息：

```text
docs: close out phase2 runbooks dispatch and coordination
```

建議包含：

- `coordination/completed/codex.md`
- `coordination/progress/codex.md`
- `coordination/progress/open.md`
- `coordination/completed/open.md`
- `coordination/progress/box.md`
- `coordination/completed/box.md`
- `coordination/incidents/2026-06-29_0915_box_maintenance-trunk-defects.md`
- `coordination/task-board/done/2026-06-29_phase2_codex_maintenance-core-01.md`
- `coordination/task-board/review/2026-06-29_phase2_box_tests-runbook-02.md`
- `docs/operations/dev-runbook.md`
- `docs/operations/phase2-round2-agent-dispatch.md`
- `docs/operations/phase2-parallel-dispatch-index-2026-06-29.md`
- `docs/operations/dispatch-open-phase2-gap-recheck-2026-06-29.md`
- `docs/operations/dispatch-mimo-phase2-ui-regression-2026-06-29.md`
- `docs/operations/dispatch-reasonix-phase2-migration-boundary-2026-06-29.md`
- `docs/operations/dispatch-box-hermes-phase2-tests-runbook-2026-06-29.md`
- `docs/operations/phase2-closeout-and-push-scope-2026-06-29.md`
- `docs/reports/open-phase2-gap-recheck-06.md`
- `docs/reports/open-phase2-integrations-gap-check-07.md`
- `docs/reports/open-phase2-main-gap-reconcile-03.md`
- `docs/reports/open-phase2-mainline-merge-plan-04.md`
- `docs/reports/open-phase2-merge-closeout-05.md`
- `docs/reports/reasonix-phase2-migration-integration-06.md`
- `docs/reports/reasonix-maintenance-review-02.md`
- `docs/reports/box-phase2-test-matrix-03.md`
- `docs/reports/box-phase2-test-matrix-04.md`
- `docs/reports/box-phase2-test-matrix-05.md`
- `docs/reports/box-phase2-test-runbook-06.md`
- `docs/reports/box-phase2-repair-runbook-07.md`
- `scripts/README.md`
- `tests/README.md`

### Commit C — Optional Agent Reports

這一批不是主幹阻塞，可視情況跟 Commit B 一起上，或分開上。

建議訊息：

```text
docs: archive supporting phase2 agent reports
```

可選包含：

- `docs/reports/mimo-phase2-ui-regression-05.md`
- `docs/reports/mimo-phase2-ui-regression-06.md`
- 其他只作為驗證憑證、但不影響主幹功能的 round report

註：
- 若這些檔案目前不在工作樹，則跳過，不需要為了湊齊而阻擋 push。

## Not Required For This Push

以下項目不需要為了 Phase 2 收尾而先做：

- `water preview`
- 真實 `PaymentRecords API` 對外版本
- OCR provider implementation
- Google Sheets implementation
- LINE webhook real integration
- 虛擬 tenant → `MaintenanceRequest` 寫入轉換腳本

這些都屬 Phase 3 或 ADR 後工作。

## Recommended Push Sequence

### 1. Preflight

```powershell
cd D:\CodexRuntime\rental\rebuild
powershell -ExecutionPolicy Bypass -File .\scripts\github_preflight_check.ps1
pytest tests\integration -q
```

Expected:

- `44 passed, 15 skipped`

### 2. Commit A

先只加入主幹功能與測試。

### 3. Commit B

再加入 docs / runbook / coordination / dispatch / reports。

### 4. Push

```powershell
git status
git push origin codex-phase2-mainline-01
```

## Notes For Upload Agent

- `coordination/progress/box.md`、`coordination/completed/box.md` 內若仍記錄 `38 passed`，可保留原交付記錄，但在 commit 說明中以主幹最新 baseline `44 passed, 15 skipped` 為準。
- `open`、`mimo`、`reasonix` 的文件若時間點比主幹稍早，只要結論未與主幹衝突，就可以吸收。
- 若再度出現外部程序回退檔案，優先檢查：
  - `app/modules/electricity/routes.py`
  - `app/modules/maintenance/routes.py`
  - `app/modules/reports/routes.py`
  - `app/modules/properties/routes.py`
  - `app/modules/rooms/routes.py`
  - `app/core/errors/handlers.py`
  - `app/repositories/*`
  - `app/services/*`

## Definition Of Safe Phase 2 Push

符合以下條件即可視為可安全 push：

- `pytest tests\integration -q` 通過
- `scripts/migration/migration_index.py` 可執行
- `scripts/repair/*.py` 預設模式可執行
- 主幹功能與文件分開 commit
- `coordination/progress/codex.md` 已更新

