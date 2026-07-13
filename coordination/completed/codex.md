# codex completed log

## 2026-07-12 16:10

Completed:
- 凍結「前期未收餘額」為 MonthlyBill 正式領域術語，新增 `CONTEXT.md` 與 ADR
- 新增 `monthly_bills.previous_balance` schema migration
- 總額公式加入 previous_balance；計算與畫面金額採四捨五入整數
- 帳單清單新增物件／房間／房客與前期未收欄位
- 新增單筆前期未收 repair script
- `runtime-real.db` migration execute 後，bill 819 寫入 `previous_balance=25047`

Verification:
- `pytest tests\integration -q`
- `109 passed, 15 skipped`
- bill 819：`4465 + 198 + 25047 = 29710`

Remaining:
- incident 剩餘 10 筆 legacy total mismatch 待業務確認

## 2026-07-12 14:20

Completed:
- 備份 `runtime-real.db`：`backups/runtime_20260712_163020.db`
- 對 target 套用 `20260703_000003_utility_policy_codes`
- Batch 2 whitelist import execute：403 rows
- Batch 2 policy assignment execute：8 properties
- 修正 `monthly_bill_paid_null_repair.py` 的 delayed config import，讓 `--database-url` 真正覆寫目標 DB
- `paid=NULL` repair execute：39 rows -> `paid=0`

Verification:
- 目標資料庫筆數：landlords/properties/rooms/tenants/contracts/monthly_bills = `10/13/89/80/80/391`
- policy pair 覆蓋：8 approved properties
- active contract missing dates：0
- invalid year_month：0
- paid NULL：0
- 11 筆 total formula mismatch 均與舊資料庫逐欄一致

Remaining:
- 11 筆 legacy total mismatch 等待業務決策；incident 已建立

## 2026-07-12 13:20

Completed:
- 建立 Batch 2 legacy whitelist exporter，固定輸出 PID `1, 2, 3, 4, 5, 6, 21, 22`
- 建立 Batch 2 incremental importer，禁止 upsert 與既有 primary key 覆寫
- 同步匯出 PID 5/6 的 electricity meters / bills / readings，保留比例分攤核對資料
- 建立本機 `real_import/batch2/` evidence bundle：403 筆資料
- 對 `runtime-real.db` 執行 utility policy migration dry-run，確認只涉及 4 個新增欄位

Verification:
- `rtk pytest tests\integration\test_batch2_whitelist_import_scripts.py tests\integration\test_batch2_policy_assignment_script.py tests\integration\test_batch2_utility_resolver_flow.py tests\integration\test_utility_policy_settings.py -q`
- `rtk py -3 .\scripts\real_import\export_batch2_whitelist.py`
- `DATABASE_URL=sqlite:///.../runtime-real.db rtk py -3 .\scripts\migration\run_migrations.py --id 20260703_000003_utility_policy_codes`

Result:
- `9 passed`
- legacy export dry-run: `403` rows
- target import dry-run intentionally stopped before write because `runtime-real.db` lacks the four policy-code columns

Remaining:
- Backup target, execute the approved additive migration, then run Batch 2 import dry-run / execute under the operator checklist

## 2026-07-12 12:05

Completed:
- 新增 Batch 2 白名單策略套用器 `scripts/real_import/apply_batch2_utility_policies.py`
- 固定核准範圍為 PID `1, 2, 3, 4, 5, 6, 21, 22`
- 預設 dry-run；缺少目標物件與既有策略衝突均會停止
- 新增腳本整合測試與 operator README

Verification:
- `rtk pytest tests\integration\test_batch2_policy_assignment_script.py tests\integration\test_batch2_utility_resolver_flow.py tests\integration\test_utility_policy_settings.py tests\integration\test_utility_policy_gating.py tests\integration\test_water_preview.py -q`

Result:
- `15 passed`

Remaining:
- 提交本輪 Batch 2 resolver / policy assignment 主幹變更
- 由 box/hermes 對真實 Batch 2 whitelist CSV 執行 dry-run、parity 與策略套用器預演

## 2026-07-12 11:30

Completed:
- Batch 2 resolver path 第一輪主幹施工
- 擴充 property / room utility policy 設定 UI 與 nested creation 測試
- 補齊 `monthly_bill_paid_null_repair.py` 的 `--database-url`，可指向 `runtime-real.db`
- 在 `electricity_service.py` 實作：
- `electricity_bill_usage_ratio`
- `electricity_bill_usage_ratio_plus_public_share`
- 在 `water_service.py` 實作：
- `auto_policy`
- `water_bill_by_stay_days`
- `water_free`
- 新增 `tests/integration/test_batch2_utility_resolver_flow.py`

Verification:
- `rtk pytest tests\integration\test_batch2_utility_resolver_flow.py tests\integration\test_utility_policy_gating.py tests\integration\test_water_preview.py tests\integration\test_billing_utility_algorithms.py -q`
- `rtk pytest tests\integration\test_utility_policy_settings.py tests\integration\test_nested_creation_routes.py tests\integration\test_repair_scripts_and_integrations_boundary.py tests\integration\test_electricity_calculation_and_posting.py tests\integration\test_water_preview.py tests\integration\test_batch2_utility_resolver_flow.py -q`

Result:
- `13 passed`
- `20 passed`

Remaining:
- 整理 commit / push 範圍，之後銜接 Batch 2 匯入腳本與白名單擴大

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
## 2026-07-13

Completed:
- 以 Google Sheet `202605`／`202606` 逐筆核對並完成全部 11 筆 Batch 2 historical total 對帳。
- `previous_balance` 支援正負值；負值代表前期貸項／超收，不再誤判為資料錯誤。
- 新增公設電費單欄修復腳本，bill 943 依來源修正 `public_electricity=0`。
- bill 172、567、573、578、833 已依 Sheet 的 signed 未收款欄完成修復。
- Google Sheet `202605`／`202606` 核對侯家敏（凱旋309號5樓房6）：
  - bill 171 寫入 `previous_balance=78`，`4520 = 4200 + 52 + 190 + 78`
  - bill 832 寫入 `previous_balance=20`，`4220 = 4200 + 20`
- 高富國／凱旋309號5樓／房間 5 的 legacy total 對帳完成：
  - bill 170（202605）寫入 `previous_balance=17615`，總額維持 `22654`
  - bill 831（202606）寫入 `previous_balance=18154`，總額維持 `22654`
- 月報表格改為可捲動容器；16 欄標頭在垂直捲動時固定於頂端。

Verification:
- 直接讀取 `runtime-real.db`：兩筆 `previous_balance`、`total` 均符合確認值。
- `pytest tests\\integration -q`：`109 passed, 0 failed, 15 skipped`
- 本機服務 `http://127.0.0.1:5001/healthz`：HTTP 200。

Remaining:
- bill 170 的 `paid=4500` 為既有付款語意異常，未自動轉換；需另行確認舊資料代表的實際收款。
