# Project Progress Master

Date: 2026-06-28
Owner: Codex
Scope: Phase 0 + Phase 1 consolidation

## Executive Summary

目前專案已完成：

- Phase 0：架構決策、資料契約、舊系統盤點、agent 分工文件
- Phase 1：新版可運行主幹、第一批 smoke tests、demo seed、runbook、GitHub 協作文件

GitHub 最新主幹已推送：

- Repo: `git@github.com:cch0919542639-gif/rental-management-v2.git`
- Branch: `main`
- Commit: `6456069`

## Phase 0 Summary

### Codex

- 建立 `D:\CodexRuntime\rental\rebuild` 工作區與多 agent 協作文件
- 建立 GitHub 協作骨架、handoff、incident、progress 機制

### reasonix

已交付：

- `docs/reports/reasonix-architecture-decision.md`
- `docs/reports/reasonix-data-contract-audit.md`
- `docs/reports/reasonix-dependency-map.md`

凍結結論：

- 採 `Parallel Rebuild`
- `year_month`: DB `YYYYMM`, UI/API `YYYY-MM`
- 正式付款流程只保留 `PaymentRecord`
- occupancy 不再依賴虛擬 tenant 名稱
- `maintenance` 應為獨立模組，不得污染 `Room.status`

Phase 1 口頭回報：

- 主幹通過 Phase 1 compliance
- 無需主幹修正

補件完成：

- `docs/reports/reasonix-phase1-review-02.md`

### open

已交付：

- `docs/reports/open-route-template-matrix.md`
- `docs/reports/open-schema-inventory.md`
- `docs/reports/open-cleanup-candidates.md`
- `docs/reports/open-module-mapping.md`
- `docs/reports/open-phase2-gap-audit-02.md`

關鍵結論：

- 舊系統與新契約盤點一致
- `billing` 是 Phase 2 第一阻塞點
- 目前最大功能缺口是 `MonthlyBill` 建立 / generate / batch 流程

### mimo

已交付：

- `docs/reports/mimo-ui-field-matrix.md`
- `docs/reports/mimo-test-scenarios.md`
- `evidence/mimo-regression-checklist.md`

口頭回報已完成：

- P1 UI 修正 5 項
- P2 gap 10 項
- 11 個頁面、10 個 flash、導覽與欄位對齊通過

補件完成：

- `docs/reports/mimo-phase1-ui-regression-02.md`

### box

已交付：

- `docs/reports/box-script-index.md`
- `docs/reports/box-module-readme-templates.md`
- `evidence/box-small-fix-notes.md`
- 追加：
- 3 支 integration tests
- `scripts/seed_reset_check.ps1`
- runbook / scripts 文件補強

## Phase 1 Implemented Baseline

### Modules Implemented

- `auth`
- `dashboard`
- `billing`
- `landlords`
- `properties`
- `rooms`
- `tenants`
- `contracts`
- `payments`
- `electricity`
- `water`
- `reports`
- `maintenance` (boundary only)

### Billing Blocking Resolved

- `MonthlyBill` 現在已有正式建立流程
- 已補：
- `billing create`
- `billing edit`
- `billing toggle paid`
- per-contract bill listing
- per-contract generate
- batch generate

- `electricity` / `water` post-to-monthly 不再只依賴測試資料或手動塞資料

### Services / Repositories Added

- `landlord_service`
- `payment_service`
- `electricity_service`
- `water_service`
- `water_allocation_service`
- `report_service`
- `maintenance_service`

- `electricity_repository`
- `water_repository`
- `report_repository`
- repository `session_get_or_404` helper

### Verification Completed

- login / dashboard
- room + contract flow
- payment create / verify / reject / link
- electricity meter / bill / reading / calculate / post
- water bill / post
- reports monthly / landlord summary / yearly
- maintenance boundary page

### Test State

- `pytest tests\integration -q` → `16 passed, 7 skipped`
- `python .\scripts\seed_demo_data.py` → pass
- `powershell -ExecutionPolicy Bypass -File .\scripts\run_smoke_tests.ps1` → pass

## Current Known Gaps

### High Priority

- `maintenance` 正式 schema 尚未凍結
- deeper electricity / water / billing algorithm 尚未完成

### Medium Priority

- reports 欄位完整性第二輪補強
- payments list 對帳欄位補強
- delete / nested CRUD / integrations 尚未移植

### Low Priority

- HTML 404/500 頁
- polish / UX consistency

## Recommended Next Sequence

1. Codex：補 deeper billing/electricity/water algorithm
2. mimo：UI 第二輪細修
3. box：擴 integration coverage / wrapper
4. open：Phase 2 backlog follow-up
5. reasonix：作為 review gate，不再直接進主幹
