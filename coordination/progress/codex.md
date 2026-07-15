# codex

Status: IN_PROGRESS - REPORTING_EXPANSION_R1_R2_R4_R5
Last Updated: 2026-07-15

## 2026-07-15 Reporting Expansion (R1 / R2 / R4 / R5)
- Added read-only report routes for property collection, selected-property settlement, new-tenant details, and property annual monthly statistics.
- Every new report supports month/year filtering, multi-property selection, sticky table headers, integer money display, empty-state messaging, and CSV/XLSX export.
- Actual received amount is derived only from linked `PaymentRecord.amount`; outstanding amount is `max(MonthlyBill.total - linked payments, 0)` so overpayments never appear as negative debt.
- Collection rows now include contract start/end dates; CSV/XLSX money fields use the same whole-dollar rounding rule as the UI.
- Added a selected-property total row to the settlement and yearly views.
- R3 property expenses and R6 move-out settlements remain separate-ledger work. They must not be stored in `MonthlyBill`.

Verification:
- `pytest tests\\integration\\test_reporting_expansion.py -q`: `5 passed`.
- `pytest tests\\integration -q`: `128 passed, 15 skipped`.

## 2026-07-14 Missing Bill Backfill
- Integrated the dry-run-first backfill tool and verified its 9 stop conditions.
- Executed only the approved candidates: 24 bills for 202604 and 1 bill for 202605.
- Imported 23 matching historical payments through PaymentRecord; 2 zero-payment rows remain unpaid.
- Verified no duplicate bills, zero formula mismatches, 23 linked payment records, and an idempotent payment rerun.
- Backups: `backups/runtime-real_before_missing_bills_20260714_180206.db` and `backups/runtime-real_before_backfill_payments_20260714_180706.db`.

## 2026-07-14 Reviewed Exception Backfill
- Added reviewed-override support for explicitly evidenced historical exceptions; it still validates source row, contract, Sheet rent, duplicate bills, and calculated totals.
- Backfilled five 202604 rows: Zhang Yanjie, Zhang Qizhong, Qiu Shenglin, Gao Fuguo, and Hou Jiamin.
- Linked three payment records where Sheet evidence existed; two rows have no payment evidence.
- Remaining blocked rows: Li Zhengyan (negative credit), He Yiyang (terminated zero-rent contract and no due amount), Zheng Boren (unclassified 160 difference), and Tian Meili (missing due amount).
- Follow-up repair candidate: Qiu Shenglin 202605 Sheet has `other=6`, while the imported bill total is 6 lower.
- Backup: `backups/runtime-real_before_reviewed_backfill_20260714_222035.db` and `backups/runtime-real_before_reviewed_payments_20260714_222116.db`.

## Current Task
- 建立 R3 `PropertyExpense` 的正式資料契約、遷移、CRUD 與物件支出明細。
- 在 Owner 決策後建立 R6 `MoveOutSettlement`，處理押金、結清、退款與付款分攤。

## Scope
- 以 `rebuild/app/` 建立新版模組化主幹
- 維持與 Phase 0 凍結契約一致
- 管理 agent 分工、交付依賴、風險與恢復入口

## Completed So Far
- 建立 app factory、config、db、errors、logging、security、year_month helper
- 建立正式 models：`user`、`landlords`、`properties`、`rooms`、`tenants`、`contracts`、`monthly_bills`、`payment_records`、`water_bills`、`calc_methods`、`electricity_*`
- 建立 repositories 與 services 主骨架
- 完成 `auth`、`dashboard`、`billing` 最小頁面與流程
- 完成 `rooms`、`contracts` CRUD 骨架與狀態同步
- 完成 `tenants`、`properties` CRUD 骨架
- 完成 `landlords` CRUD 骨架
- 完成 `payments` 統一流程骨架：create / verify / reject / link
- 完成 `billing` 正式流程：create / edit / toggle paid / per-contract list / generate / batch generate
- 完成 `electricity` 骨架：meter / bill / reading / calculate / post to monthly bill
- 完成 `water` 骨架：water bill CRUD / shared_by_stay_days / independent_meter posting
- 完成 `reports`：monthly / landlord summary / yearly overview，以及 R1/R2/R4/R5 物件選取與 CSV/XLSX 匯出
- 完成 `maintenance` 模組邊界頁：不新增 schema，只保留正式入口與 room snapshot
- 完成 `maintenance Phase 2B`：filter / open list / room-scoped list / summary cards / maintenance report / legacy scan
- 完成 `electricity property detail`：property overview / recent bills / property filter 導流
- 完成 `electricity property workflows`：property-scoped new bill / quick reading / reading log
- 完成 `nested creation`：`/properties/landlord/<id>/create`、`/rooms/property/<id>/create`
- 完成正式錯誤頁：`404` / `500` / `app_error`
- 完成 migration 只讀入口：`scripts/migration/migration_index.py`
- 完成 migration scaffold：
- `scripts/migration/_common.py`
- `scripts/migration/_template_write_migration.py`
- migration metadata / naming / write-safe convention
- 完成 migration write path：
- `scripts/repair/_common.py`
- repair scripts 啟動前置 `sys.path` 修正
- `contract_expiry_repair.py --execute --reference-date`
- write-capable repair integration test
- 完成 repair scripts：
- `scripts/repair/year_month_audit.py`
- `scripts/repair/room_status_audit.py`
- `scripts/repair/contract_expiry_repair.py`
- `scripts/repair/user_table_audit.py`
- 完成 integrations skeleton：
- `app/integrations/__init__.py`
- `app/integrations/ocr_client.py`
- `app/integrations/sheets_client.py`
- `app/integrations/line_webhook.py`
- 完成 OCR adapter 第一版：
- `app/services/payment_ocr_service.py`
- `POST /api/payment-records/<id>/analyze`
- OCR provider factory + graceful fallback
- OCR metadata-only persistence (`raw_ocr_text`, `raw_llm_response`, `ocr_engine`)
- field-level 422 details for payment API create
- 完成 LINE webhook 第一版：
- signature verification
- JSON payload parsing
- event summary response
- graceful `501 not_configured`
- no direct payment / maintenance write
- 完成 Sheets export-only 第一版：
- `app/integrations/sheets_client.py`
- `app/services/report_export_service.py`
- `/reports/monthly/export`
- `/reports/landlord-summary/export`
- `/reports/yearly/export`
- 支援 `csv` / `xlsx`
- no OAuth / no import / no write-back
- 完成 `tests/conftest.py` 與多支 integration smoke / coverage tests
- 完成 `scripts/seed_demo_data.py`
- 完成 `docs/operations/dev-runbook.md`
- 完成 `docs/operations/current-dispatch-and-handoff-plan.md`
- 完成 `requirements-dev.txt`
- 完成 `scripts/run_dev.ps1`、`scripts/run_smoke_tests.ps1`
- 已驗證：
- 未登入 `/` 會轉向 `/auth/login`
- 登入成功後可進入 dashboard
- billing 頁面可顯示資料
- billing 可建立單筆月帳單
- billing 可依合約產生月帳單
- billing 可批次產生月帳單
- billing 可切換已繳狀態
- create room / create contract / terminate contract 流程正確
- create property / create tenant / list pages 流程正確
- create landlord / create payment / verify payment / link payment 流程正確
- create electricity meter / bill / reading / calculate / monthly posting 流程正確
- create water bill / monthly posting 流程正確
- reports monthly / landlord summary / yearly overview 流程正確
- maintenance create / edit / transition / filters / open list / room-scoped list / maintenance report 流程正確
- electricity property detail / property-scoped new bill / quick reading / reading log / nested creation routes 流程正確
- error pages / migration index 流程正確
- repair scripts / integration placeholder route 流程正確
- migration write path dry-run / execute 流程正確
- migration scaffold / template / index 流程正確
- OCR analyze API / graceful fallback / validation detail 流程正確
- LINE webhook config-missing / invalid-signature / valid-signed-payload 流程正確
- reports export csv / xlsx / invalid-format 流程正確
- 完成 `monthly_bill_paid_null_repair.py` 指向資料庫修正：支援 `--database-url`
- 完成 property / room utility policy 設定 UI：
- `properties/form,list`
- `rooms/form,list`
- property / room nested creation 可直接帶入 policy_code
- 完成 Batch 2 resolver service path：
- electricity `bill_usage_ratio`
- electricity `bill_usage_ratio_plus_public_share`
- water `auto_policy`
- water `water_bill_by_stay_days`
- water `water_free`
- 完成 Batch 2 resolver integration tests
- 完成 Batch 2 白名單策略套用器：
- `scripts/real_import/apply_batch2_utility_policies.py`
- 僅允許 PID `1, 2, 3, 4, 5, 6, 21, 22`
- 預設 dry-run；缺少目標物件或既有策略衝突時停止
- 新增 `tests/integration/test_batch2_policy_assignment_script.py`
- 完成 Batch 2 真實資料白名單匯出／增量匯入主幹：
- `scripts/real_import/export_batch2_whitelist.py`
- `scripts/real_import/import_batch2_whitelist.py`
- 只讀舊庫、固定 PID `1, 2, 3, 4, 5, 6, 21, 22`、輸出 403 筆資料
- 目標端禁止 upsert；任何既有 primary key 都是 stop condition
- 已建立 `real_import/batch2/` 本機 CSV evidence bundle，尚未寫入 `runtime-real.db`
- Batch 2 正式資料導入完成：
- target backup：`backups/runtime_20260712_163020.db`
- 403 rows inserted；8 個 property policy pairs 已設定
- `paid=NULL` 39 rows 已正規化為 `paid=0`
- 11 筆 legacy monthly bill total mismatch 已建立 incident，禁止自動覆寫
- 完成前期未收餘額主幹：
- `MonthlyBill.previous_balance` 與 additive migration
- 總額公式加入前期未收，計算金額四捨五入至整數
- 帳單／合約帳單／儀表板／月報改用整數金額 display，帳單清單新增物件／房間／房客與前期未收
- bill `819` 已依 Owner 確認寫入 `previous_balance=25047`，總額 `29710` 完成對帳
- bill `170`、`831` 已依 Owner 確認寫入前期未收 `17615`、`18154`，兩筆總額均維持 `22654`
- Google Sheet 核對後，bill `171`、`832` 已寫入前期未收 `78`、`20`，分別對應侯家敏 202605／202606 的未收款欄。
- 侯家敏兩筆「已繳」金額 `4500`、`4200` 尚未建立歷史 PaymentRecord；帳單維持未全額繳清，禁止將金額寫入 `paid` 布林欄。
- Google Sheet 完成其餘 6 筆核對：bill `172`、`567`、`573`、`578`、`833` 已寫入正負前期餘額；bill `943` 已修正誤匯的公設電費 `40 -> 0`。
- 全部 11 筆 historical total 已對齊 expanded formula；不再是 Batch 2 財務總額 blocker。
- 已匯入 11 筆已核對的歷史 PaymentRecord；來源交易 ID 可重跑去重，部分付款保持未全額繳清。
- 前期餘額生成改為扣除已連結付款，並保留手動 `paid` 舊帳的相容語意。
- 月報 16 欄標頭已改為垂直捲動時固定顯示
- `pytest tests\integration -q` 通過（61 passed, 15 skipped）
- `python .\scripts\seed_demo_data.py` 可成功建立 demo data
- `powershell -ExecutionPolicy Bypass -File .\scripts\run_smoke_tests.ps1` 通過
- `rtk pytest tests\integration\test_batch2_utility_resolver_flow.py tests\integration\test_utility_policy_gating.py tests\integration\test_water_preview.py tests\integration\test_billing_utility_algorithms.py -q` 通過（13 passed）
- `rtk pytest tests\integration\test_utility_policy_settings.py tests\integration\test_nested_creation_routes.py tests\integration\test_repair_scripts_and_integrations_boundary.py tests\integration\test_electricity_calculation_and_posting.py tests\integration\test_water_preview.py tests\integration\test_batch2_utility_resolver_flow.py -q` 通過（20 passed）
- `rtk pytest tests\integration\test_batch2_policy_assignment_script.py tests\integration\test_batch2_utility_resolver_flow.py tests\integration\test_utility_policy_settings.py tests\integration\test_utility_policy_gating.py tests\integration\test_water_preview.py -q` 通過（15 passed）
- `rtk pytest tests\integration\test_batch2_whitelist_import_scripts.py tests\integration\test_batch2_policy_assignment_script.py tests\integration\test_batch2_utility_resolver_flow.py tests\integration\test_utility_policy_settings.py -q` 通過（9 passed）
- `runtime-real.db` policy migration dry-run：只會新增 properties / rooms 共 4 個 policy_code 欄位
- `pytest tests\integration -q` 通過（109 passed, 15 skipped）

## Active Agent Allocation
- `reasonix`: Phase 1 規格審查與風險守門，不直接重寫主幹
- `open`: 適合承接 route matrix 對齊、報表欄位驗證或 Phase 2 缺口盤點
- `mimo`: 適合承接已完成頁面的 UI 欄位對齊與回歸檢查
- `box`: 適合承接 smoke tests、runbook、低風險支援腳本

## Next Step
- 先完成 R3 物件支出帳本；其後再依押金退款與付款分攤決策開啟 R6 退租結清。

## Risks / Blockers
- 歷史付款資料仍不完整：Google Sheet 的部分收款金額不能寫入 `MonthlyBill.paid`，必須以 PaymentRecord 匯入與連結。
- 支出與退租結清尚無正式帳本資料，R1/R2/R5 不會推估房東費用、管理費、清潔費或維修費。
- 本機有尚未整理 commit 的主幹變更
- Batch 2 電費比例分攤目前以 property/room policy 為主，不含 custom module（7/8/9/10 與 Room 432 例外仍不在本輪）
- 曾發生外部程序回退檔案；若再次出現，先比對 `maintenance/report/electricity` service/repository、`nested routes`、`error handlers` 是否被覆寫
- 中斷恢復時，請先讀 `coordination/progress/codex.md` 與 `docs/operations/current-dispatch-and-handoff-plan.md`
