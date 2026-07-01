# codex completed log

## 2026-07-01 12:50

Completed:
- Phase 4A / 4B 主幹第一批：`deployment + migration baseline`
- 新增 tracked migration runner：`scripts/migration/run_migrations.py`
- 新增 migration registry：`scripts/migration/_registry.py`
- 新增 baseline marker：`apply_20260701_000001_phase4_baseline_marker.py`
- 更新 migration index / README / template，讓 `apply_*` migration 可被正式追蹤
- 新增 `scripts/health_check.py` production preflight
- 新增 `docs/operations/phase4-launch-baseline.md`
- 補齊 Phase 4 integration tests：migration runner + health check

Verification:
- `pytest tests\integration\test_admin_route_protection.py tests\integration\test_production_readiness.py tests\integration\test_phase4_migration_and_health.py -q`
- `pytest tests\integration -q`

Result:
- `68 passed, 15 skipped`

Remaining:
- 整理 Phase 4A / 4B commit / push 範圍
- 進入 DB / backup / deployment 後續基線

## 2026-06-30 23:47

Completed:
- Phase 4A-1 第一批：`auth hardening + production readiness`
- 將主要寫入 HTML routes 補上 `@admin_required`
- 將 payment write API 補上 `@admin_required`
- 新增 `app/core/config/validation.py`
- 將 runtime config validation 接入 app factory
- 補上 production secure cookie / https scheme defaults
- 新增 `/readyz` readiness endpoint
- 新增 `requirements.txt` runtime 依賴清單
- 新增 Waitress production-like 啟動面：`app/wsgi.py`、`scripts/run_production.py`、`scripts/run_prod.ps1`
- 新增 `tests/integration/test_admin_route_protection.py`
- 新增 `tests/integration/test_production_readiness.py`

Verification:
- `pytest tests\integration\test_admin_route_protection.py tests\integration\test_production_readiness.py -q`
- `pytest tests\integration -q`

Result:
- `66 passed, 15 skipped`

Remaining:
- 整理 Phase 4A commit / push 範圍
- 進入 WSGI / migration / production DB readiness

## 2026-06-30 01:32

Completed:
- Phase 3 第八個主題：`Sheets export-only`
- 補齊 `app/integrations/sheets_client.py`，支援 `csv` / `xlsx`
- 新增 `app/services/report_export_service.py`
- 新增 `/reports/monthly/export`
- 新增 `/reports/landlord-summary/export`
- 新增 `/reports/yearly/export`
- 明確限制 export-only：不做 OAuth、不做 import、不做 write-back
- 新增 `tests/integration/test_reports_export_adapter.py`

Verification:
- `pytest tests\integration\test_reports_export_adapter.py tests\integration\test_reports_monthly_and_landlord_summary.py -q`
- `pytest tests\integration -q`

Result:
- `61 passed, 15 skipped`

Remaining:
- 進入整體收尾：最終驗收、總結與 commit-push 整理

## 2026-06-30 01:02

Completed:
- Phase 3 第六個主題：`LINE webhook`
- 擴充 `app/integrations/line_webhook.py` 為最小可運行版
- 補上 LINE signature verification
- 補上 JSON payload parsing 與 event summary response
- 缺少 `LINE_CHANNEL_SECRET` 時回傳 graceful `501 not_configured`
- webhook 不直接寫入 payment / maintenance / 其他 domain tables
- 更新 integrations README 與 LINE webhook integration tests

Verification:
- `pytest tests\integration\test_repair_scripts_and_integrations_boundary.py tests\integration\test_payments_api_boundary.py -q`
- `pytest tests\integration -q`

Result:
- `58 passed, 15 skipped`

Remaining:
- Phase 3 其餘主題可往 Sheets export-only、payment API backlog 或 OCR/LINE review UI 前進

## 2026-06-30 00:45

Completed:
- Phase 3 第五個主題：`OCR adapter`
- 補齊 `app/integrations/ocr_client.py` provider factory 與 graceful fallback
- 新增 `app/services/payment_ocr_service.py`
- 擴充 `/api/payment-records`：保留 list / detail / create，新增 `POST /api/payment-records/<id>/analyze`
- OCR analyze 僅寫入 `raw_ocr_text` / `raw_llm_response` / `ocr_engine`
- OCR analyze 不自動修改 `PaymentRecord.record_status`，也不自動覆蓋核心付款欄位
- payment API create 補上 field-level 422 details
- 同步收斂 migration scaffold index/README 與測試基線

Verification:
- `pytest tests\integration\test_payments_api_boundary.py tests\integration\test_auth_billing_payments_smoke.py tests\integration\test_payments_reject_and_status.py -q`
- `pytest tests\integration -q`
- `py -3 .\scripts\migration\migration_index.py`

Result:
- `56 passed, 15 skipped`

Remaining:
- Phase 3 其餘主題可往 LINE webhook、Sheets export-only 或 payment API backlog 補完前進

## 2026-06-29 23:36

Completed:
- Phase 3 第三個主題：`migration write path`
- 新增 `scripts/repair/_common.py`，統一 repair script app bootstrap 與 reference-date parsing
- 修正四支 repair scripts 的直接執行啟動路徑，避免 `app` / `scripts.repair` import 失敗
- 擴充 `contract_expiry_repair.py` 為正式 dry-run-first write path：支援 `--execute`、`--reference-date`
- 補上 write convention 文件
- 新增 execute-path integration test，驗證 dry-run 不寫入、execute 會把過期 active contract 改為 expired

Verification:
- `py -3 .\scripts\repair\year_month_audit.py`
- `py -3 .\scripts\repair\contract_expiry_repair.py --reference-date 2026-06-29`
- `pytest tests\integration\test_repair_scripts_and_integrations_boundary.py -q`
- `pytest tests\integration -q`

Result:
- `51 passed, 15 skipped`

Remaining:
- Phase 3 其餘主題可往實作型 integrations 或 migration scaffold 擴充前進

## 2026-06-29 18:28

Completed:
- 補回 `maintenance/report/electricity` 被外部回退的 service + repository 方法
- 整合 `maintenance Phase 2B` 主幹：filter / open list / room-scoped list / summary cards / maintenance report / legacy scan
- 整合 `electricity property detail` 主幹：property overview / recent bills / property filter 導流
- 完成 `nested creation` 主幹：`/properties/landlord/<id>/create`、`/rooms/property/<id>/create`

Verification:
- `pytest tests\integration\test_nested_creation_routes.py tests\integration\test_maintenance_core_flow.py tests\integration\test_maintenance_filters_and_summary.py tests\integration\test_reports_maintenance_summary.py tests\integration\test_electricity_property_detail.py -q`
- `pytest tests\integration -q`

Result:
- `37 passed, 15 skipped`

Remaining:
- Phase 2 剩餘缺口施工與 commit/push 整理

## 2026-06-29 22:42

Completed:
- Phase 3 第一個主題：`water preview`
- 新增 `GET,POST /water/<id>/preview`
- 新增不寫入版 water allocation preview service
- 新增 `water/preview.html`
- 在 `water/list.html`、`water/post_form.html` 接上 preview 入口
- 新增 `tests/integration/test_water_preview.py`

Verification:
- `pytest tests\integration\test_water_preview.py tests\integration\test_water_edit_and_independent_post.py tests\integration\test_electricity_water_edge_cases.py -q`
- `pytest tests\integration -q`

Result:
- `46 passed, 15 skipped`

Remaining:
- Phase 3 後續主題施工

## 2026-06-29 22:52

Completed:
- Phase 3 第二個主題：`payment-records API boundary`
- 新增 `GET /api/payment-records/`
- 新增 `GET /api/payment-records/<id>`
- 新增 `POST /api/payment-records/`
- 新增 payment JSON serializer 與 repository filter
- 保持 API 與既有 `PaymentService` 共用同一正式流程
- 新增 `tests/integration/test_payments_api_boundary.py`

Verification:
- `pytest tests\integration\test_payments_api_boundary.py tests\integration\test_auth_billing_payments_smoke.py tests\integration\test_payments_reject_and_status.py -q`
- `pytest tests\integration -q`

Result:
- `50 passed, 15 skipped`

Remaining:
- Phase 3 後續主題施工

## 2026-06-29 18:40

Completed:
- 完成 `electricity property` 第二輪主幹：`/electricity/property/<id>/new-bill`、`/electricity/property/<id>/quick-reading`、`/electricity/property/<id>/reading-log`
- 新增 property-scoped 抄表歷史模板與快捷抄表表單
- 新增 integration test 覆蓋 property-scoped bill + reading workflow

Verification:
- `pytest tests\integration\test_electricity_property_workflows.py tests\integration\test_electricity_property_detail.py tests\integration\test_electricity_meter_edit_and_post.py tests\integration\test_electricity_calculation_and_posting.py -q`
- `pytest tests\integration -q`

Result:
- `38 passed, 15 skipped`

Remaining:
- Phase 2 剩餘缺口施工與 commit/push 整理

## 2026-06-29 22:00

Completed:
- 建立正式 HTML error pages：`404` / `500` / `app_error`
- 建立 migration 只讀入口：`scripts/migration/migration_index.py`
- 更新 `scripts/migration/README.md` 與 `docs/operations/dev-runbook.md`
- 再次收斂外部回退造成的 `maintenance/report/electricity/nested routes` 不一致
- 調整既有 electricity 測試，讓 UI 本地化後仍能正確驗證狀態顯示

Verification:
- `pytest tests\integration\test_error_pages_and_migration_index.py tests\integration\test_nested_creation_routes.py tests\integration\test_maintenance_core_flow.py tests\integration\test_maintenance_filters_and_summary.py tests\integration\test_reports_maintenance_summary.py tests\integration\test_electricity_property_detail.py tests\integration\test_electricity_property_workflows.py -q`
- `pytest tests\integration -q`
- `py -3 .\scripts\migration\migration_index.py`

Result:
- `41 passed, 15 skipped`

Remaining:
- Phase 2 剩餘缺口施工與 commit/push 整理

## 2026-06-29 22:18

Completed:
- 建立 `scripts/repair/` 四支腳本：`year_month_audit.py`、`room_status_audit.py`、`contract_expiry_repair.py`、`user_table_audit.py`
- 建立 `app/integrations/` skeleton：`__init__.py`、`ocr_client.py`、`sheets_client.py`、`line_webhook.py`
- 在 `payments/list.html` 加入 OCR 資訊 display-only 區塊
- 更新 `app/integrations/README.md`、`scripts/repair/README.md`
- 註冊 LINE webhook placeholder route

Verification:
- `py -3 .\scripts\repair\year_month_audit.py`
- `py -3 .\scripts\repair\room_status_audit.py`
- `py -3 .\scripts\repair\contract_expiry_repair.py`
- `py -3 .\scripts\repair\user_table_audit.py`
- `pytest tests\integration\test_repair_scripts_and_integrations_boundary.py -q`
- `pytest tests\integration -q`

Result:
- `44 passed, 15 skipped`

Remaining:
- Phase 2 剩餘缺口施工與 commit/push 整理
