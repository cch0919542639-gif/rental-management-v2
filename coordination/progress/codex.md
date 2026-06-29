# codex

Status: IN_PROGRESS
Last Updated: 2026-06-29 22:18

## Current Task
- Phase 2 主幹收斂與 `repair scripts + integrations skeleton` 完工
- 已補回外部回退的 `maintenance/report/electricity` service + repository 方法
- 已建立正式 HTML `404/500/app_error` 頁面與 `scripts/migration/migration_index.py`
- 已建立 `scripts/repair/` 四支 audit/repair 腳本與 `app/integrations/` boundary skeleton
- `nested creation`、`maintenance Phase 2B`、`electricity property detail / new bill / quick reading / reading log`、`error pages / migration entry / repair scripts / integrations skeleton` 目前已整合進主幹並通過測試
- 下一批主幹目標為 deeper algorithm、正式 migration write path、integration boundary 細部頁面或 API

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
- 完成 `reports` 骨架：monthly / landlord summary / yearly overview query + presenter
- 完成 `maintenance` 模組邊界頁：不新增 schema，只保留正式入口與 room snapshot
- 完成 `maintenance Phase 2B`：filter / open list / room-scoped list / summary cards / maintenance report / legacy scan
- 完成 `electricity property detail`：property overview / recent bills / property filter 導流
- 完成 `electricity property workflows`：property-scoped new bill / quick reading / reading log
- 完成 `nested creation`：`/properties/landlord/<id>/create`、`/rooms/property/<id>/create`
- 完成正式錯誤頁：`404` / `500` / `app_error`
- 完成 migration 只讀入口：`scripts/migration/migration_index.py`
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
- `pytest tests\integration -q` 通過（44 passed, 15 skipped）
- `python .\scripts\seed_demo_data.py` 可成功建立 demo data
- `powershell -ExecutionPolicy Bypass -File .\scripts\run_smoke_tests.ps1` 通過

## Active Agent Allocation
- `reasonix`: Phase 1 規格審查與風險守門，不直接重寫主幹
- `open`: 適合承接 route matrix 對齊、報表欄位驗證或 Phase 2 缺口盤點
- `mimo`: 適合承接已完成頁面的 UI 欄位對齊與回歸檢查
- `box`: 適合承接 smoke tests、runbook、低風險支援腳本

## Next Step
- 由 Codex 繼續推進 Phase 2 剩餘主幹：正式 migration write path、payment-records API boundary、water preview 或 deeper utility algorithm
- 維持 agent 分工：Codex 先做主幹，其他 agent 只承接低風險驗證、盤點、文件與測試擴充

## Risks / Blockers
- 目前沒有結構性 blocker
- 本機有尚未整理 commit 的主幹變更
- 曾發生外部程序回退檔案；若再次出現，先比對 `maintenance/report/electricity` service/repository、`nested routes`、`error handlers` 是否被覆寫
- 中斷恢復時，請先讀 `coordination/progress/codex.md` 與 `docs/operations/current-dispatch-and-handoff-plan.md`
