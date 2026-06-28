# open

Status: IN_PROGRESS
Last Updated: 2026-06-28
Branch: `agent/open-phase2-implementation-backlog-01`

## Current Task

- 根據 gap audit 整理 Phase 2 實作 backlog，拆分優先序與依賴關係
- 產出 `docs/reports/open-phase2-implementation-backlog-01.md`
- 不碰 billing create/generate 主幹、不修改資料契約、不修改 `app/models`

## Scope

- Phase 2 缺口分類（billing-dependent / low-risk CRUD / nested CRUD / electricity detail / integrations / Phase 3）
- 每個項目標記 owner 建議、依賴、風險、是否需要 Codex 主控
- 產出 task-board 可派發的 packet 建議

## Completed So Far

1. 讀完 4 份核心文件（phase1-master-status, dispatch-handoff, gap-audit, project-progress）
2. 讀完現有 billing module（routes.py, repository, service, model, template）
3. 讀完 electricity/water post flow 確認 monthyl_bill 依賴
4. 建立 `agent/open-phase2-implementation-backlog-01` branch
5. 產出 `docs/reports/open-phase2-implementation-backlog-01.md`

## Next Step

- 等待 Codex 審閱 backlog，決定下一輪任務派發

## Risks / Blockers

- T1 (billing create/generate) 是 Phase 2 最大阻塞點 — electricity/water post flow 都依賴已存在的 MonthlyBill
- 本次 backlog 不觸及 billing 主幹實作，需要 Codex 接手 T1
- 其餘 T2-T5 無互鎖阻塞，可平行開發
