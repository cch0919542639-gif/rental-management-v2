# Repeatable Agent Delivery Loop

Last Updated: 2026-06-28
Owner: Codex

## Goal

將多 agent 協作流程固定成一個可重複執行的模式：

1. Codex 先定義階段目標
2. Codex 先完成該階段主幹與規範
3. Codex 將子任務切分給不同 agent
4. agent 回報交付物
5. Codex 驗收、整合、修正
6. 進入下一階段

## Recommended Lifecycle

### Stage 0: Freeze

- 定義階段目標
- 凍結必要契約 / 邊界 / 驗收標準
- 建立該階段的主控文件

輸出：

- `docs/operations/<phase>-master-status.md`
- `docs/operations/current-dispatch-and-handoff-plan.md`
- 若需契約，先補 `data_contracts/*`

### Stage 1: Codex Skeleton

- Codex 先做最小可運行主幹
- 不等 agent 先做分散實作
- 先把高衝突區收斂：
- `app/models`
- `app/services`
- `repositories`
- 核心路由與模板

輸出：

- 可跑 baseline
- smoke test baseline
- handoff / runbook baseline

### Stage 2: Task Packet Dispatch

- 將剩餘工作切成低耦合 task packet
- 每包只能有：
- 目標
- 可改檔案範圍
- 禁止事項
- 驗收標準
- 交付檔名

規則：

- 一個 agent 只拿一種責任類型
- 高衝突區只保留 Codex 或單一 owner

### Stage 3: Agent Delivery

- agent 開 branch
- agent 更新 `coordination/progress/<agent>.md`
- agent 完成後交付：
- code / docs / tests
- `coordination/completed/<agent>.md`
- 若阻塞，寫 incident

### Stage 4: Codex Review Gate

- Codex 驗檔
- Codex 驗測試
- Codex 驗是否越權
- Codex 做總整理

可能結果：

- `accepted`
- `accepted_with_followup`
- `needs_fix`
- `reassign`

### Stage 5: Consolidation

- Codex 寫總進度報告
- 更新 master status
- 更新下一階段 dispatch plan

### Stage 6: Next Stage

- 根據最大 blocker 決定下一個主線
- 重複 Stage 0 到 Stage 5

## Incident Handling

若 agent 回報：

- 契約不清
- schema 衝突
- route/service 邊界不清
- 測試無法穩定

流程：

1. agent 寫 incident
2. Codex 先裁定
3. 如有必要，Codex 直接修主幹
4. 原 agent 繼續，或改派另一個 agent

## Reassignment Rule

若某 agent 連續兩次：

- 無法在限制內完成
- 多次越權
- 多次交付不一致

則該 task packet 直接：

- 收回給 Codex
- 或改派給另一個 agent

## Why Localhost Kanban Worked Poorly

`http://localhost:8080/kanban` 類看板對 agent 常失效，原因通常是：

- 任務狀態與 repo 狀態分離
- agent 只會回填看板，不會同步 repo 文件
- 看板內容不夠精確，缺少可改檔範圍與禁止事項
- 崩潰後無法單靠 repo 還原

## Better Implementation Pattern

優先使用「repo 內檔案式任務板」，而不是只靠外部看板。

理由：

- 任務與程式碼同版本管理
- 可用 GitHub branch / PR 直接追蹤
- 崩潰後只要 pull repo 就能恢復
- 其他電腦不需要依賴本機 localhost 服務

## Minimal Repeatable Stack

建議固定使用四層：

1. GitHub branch / PR
2. `coordination/progress/*.md`
3. `coordination/incidents/*.md`
4. `coordination/task-board/` 檔案式任務板

## Success Condition

這套模式的成功標準不是「agent 能自己找事做」，而是：

- 每一輪都有清楚 owner
- 每一輪都有可驗收交付物
- 每一輪失敗都能快速重派或回收
- 專案狀態只靠 repo 就能重建
