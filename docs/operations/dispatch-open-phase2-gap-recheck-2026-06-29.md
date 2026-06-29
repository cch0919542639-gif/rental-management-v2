# 給 open 的派工指令

你現在負責 **Phase 2 主幹缺口重新盤點**。  
這次是文件盤點工作，不是主幹重寫工作。不要改 `app/models/*`，不要改 data contracts，不要自行修公式。

## 你的目標

在 `codex-phase2-mainline-01` 最新狀態上，重新盤點「還沒做完」的 Phase 2 缺口，特別是：

- integrations 前置
- error pages
- migration 入口與交接點
- 目前仍屬 Phase 2 但尚未落地的 route / template / flow

## 先讀

- `D:\CodexRuntime\rental\rebuild\coordination\progress\codex.md`
- `D:\CodexRuntime\rental\rebuild\docs\operations\phase2-parallel-dispatch-index-2026-06-29.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-phase2-main-gap-reconcile-03.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-phase2-mainline-merge-plan-04.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-phase2-merge-closeout-05.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-phase2-contract-notes-01.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-maintenance-followup-04.md`

## 直接交付

請直接建立並填寫：

- `D:\CodexRuntime\rental\rebuild\docs\reports\open-phase2-gap-recheck-06.md`

## 你必須回答的內容

至少整理這 5 段：

1. Executive Summary
2. 已完成項目 vs 尚未完成項目
3. 尚未完成缺口分級
4. 哪些缺口可直接由 Codex 主幹實作
5. 哪些缺口可再分派給其他 agent

## 必查範圍

- `integrations` 相關前置點是否已存在：
  - route placeholder
  - service boundary
  - docs / runbook 入口
- error pages：
  - 404 / 500 template 是否仍缺
- migration 入口：
  - `scripts/migration/`
  - runbook / docs 是否已有正式入口
- electricity property workflows 完成後，是否還有 route/template 缺口
- maintenance / reports 是否還有只做一半的頁面或流程

## 明確限制

- 不要改 model
- 不要改 repository/service 公式
- 不要自行重寫主幹
- 不要用舊 branch 當真相，請以目前 `codex-phase2-mainline-01` 工作樹為準

## 工作紀錄要求

- 開工前更新 `D:\CodexRuntime\rental\rebuild\coordination\progress\open.md`
- 完成後更新 `D:\CodexRuntime\rental\rebuild\coordination\completed\open.md`

## 如果卡住

遇到以下情況立刻回報：

- 無法判定某 route / flow 是否已正式進主幹
- 文件與程式實況矛盾
- 發現高風險缺口需要資料契約決策

回報方式：

- 新增 `D:\CodexRuntime\rental\rebuild\coordination\incidents\<timestamp>_open_<topic>.md`
- 把 `progress/open.md` 狀態改成 `BLOCKED`

