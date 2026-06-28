# codex

Status: IN_PROGRESS
Last Updated: 2026-06-28 11:20

## Current Task
- Phase 1 骨架實作主控
- 已完成 `auth`、`dashboard`、`billing`、`rooms`、`contracts`、`tenants`、`properties` 最小可運行骨架
- 正在規劃下一批 `landlords`、`payments`、`electricity`、`water`

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
- 已驗證：
- 未登入 `/` 會轉向 `/auth/login`
- 登入成功後可進入 dashboard
- billing 頁面可顯示資料
- create room / create contract / terminate contract 流程正確
- create property / create tenant / list pages 流程正確

## Active Agent Allocation
- `reasonix`: Phase 1 規格審查與風險守門，不直接重寫主幹
- `open`: 適合承接 `landlords`、`payments` 骨架
- `mimo`: 適合承接已完成頁面的 UI 欄位對齊與回歸檢查
- `box`: 適合承接 smoke tests、runbook、低風險支援腳本

## Next Step
- 由 Codex 繼續補 `landlords + payments` 主幹
- 並行交付：
- `reasonix` 做 Phase 1 review note
- `open` 做 `landlords/payments`
- `mimo` 做 UI gap check
- `box` 做 smoke tests 與 runbook

## Risks / Blockers
- 目前沒有結構性 blocker
- `payments`、`electricity`、`water` 尚未落地，跨模組公式仍需持續受控
- 中斷恢復時，請先讀 `docs/operations/phase1-master-status.md`
