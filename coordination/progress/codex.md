# codex

Status: IN_PROGRESS
Last Updated: 2026-06-28 15:22

## Current Task
- Phase 1 骨架實作主控
- 已完成 `auth`、`dashboard`、`billing`、`rooms`、`contracts`、`tenants`、`properties`、`landlords`、`payments`、`electricity`、`water`、`reports`、`maintenance` 主幹骨架
- 已完成第一批 integration smoke tests 與 demo seed script
- 已完成 `dev runbook`、接手分工文件、啟動 / smoke 腳本
- 下一批主幹目標為整理提交、更多測試覆蓋與更深層功能收斂

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
- 完成 `electricity` 骨架：meter / bill / reading / calculate / post to monthly bill
- 完成 `water` 骨架：water bill CRUD / shared_by_stay_days / independent_meter posting
- 完成 `reports` 骨架：monthly / landlord summary / yearly overview query + presenter
- 完成 `maintenance` 模組邊界頁：不新增 schema，只保留正式入口與 room snapshot
- 完成 `tests/conftest.py` 與 2 支 integration smoke tests
- 完成 `scripts/seed_demo_data.py`
- 完成 `docs/operations/dev-runbook.md`
- 完成 `docs/operations/current-dispatch-and-handoff-plan.md`
- 完成 `requirements-dev.txt`
- 完成 `scripts/run_dev.ps1`、`scripts/run_smoke_tests.ps1`
- 已驗證：
- 未登入 `/` 會轉向 `/auth/login`
- 登入成功後可進入 dashboard
- billing 頁面可顯示資料
- create room / create contract / terminate contract 流程正確
- create property / create tenant / list pages 流程正確
- create landlord / create payment / verify payment / link payment 流程正確
- create electricity meter / bill / reading / calculate / monthly posting 流程正確
- create water bill / monthly posting 流程正確
- reports monthly / landlord summary / yearly overview 流程正確
- maintenance 邊界頁可用，且未發明新 schema
- `pytest tests\integration -q` 通過（2 passed）
- `python .\scripts\seed_demo_data.py` 可成功建立 demo data
- `powershell -ExecutionPolicy Bypass -File .\scripts\run_smoke_tests.ps1` 通過

## Active Agent Allocation
- `reasonix`: Phase 1 規格審查與風險守門，不直接重寫主幹
- `open`: 適合承接 route matrix 對齊、報表欄位驗證或 Phase 2 缺口盤點
- `mimo`: 適合承接已完成頁面的 UI 欄位對齊與回歸檢查
- `box`: 適合承接 smoke tests、runbook、低風險支援腳本

## Next Step
- 由 Codex 繼續整理提交、擴 tests、推進 deeper algorithm
- 並行交付：
- `reasonix` 做 Phase 1 review note
- `open` 做 route / gap inventory
- `mimo` 做 UI gap check
- `box` 做 tests / runbook 微調

## Risks / Blockers
- 目前沒有結構性 blocker
- 本機新增內容尚未推送到 GitHub
- `payments`、`electricity`、`water` 已落地，但 deeper algorithm 仍需持續受控
- 中斷恢復時，請先讀 `docs/operations/phase1-master-status.md`
