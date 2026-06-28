# Collaboration Rules

## Goal

讓不同電腦上的協作者與不同 agent 可以在 GitHub 上並行工作，同時維持資料契約與主幹穩定。

## Source of Truth

- 架構與決策：`docs/reports/`
- 主控狀態：`docs/operations/phase1-master-status.md`
- 當前施工：`coordination/progress/`
- 完成紀錄：`coordination/completed/`
- 事故與阻塞：`coordination/incidents/`

## Collaboration Model

- `Codex` 維護主幹整合與高衝突區
- `reasonix` 負責決策守門、規格審查、風險提示
- `open` 負責 route-heavy / CRUD-heavy 模組骨架
- `mimo` 負責 UI、欄位對齊、驗收與回歸
- `box` 負責測試、runbook、支援腳本、低風險文件

## File Ownership

- 每個 agent 優先只改自己任務範圍內的模組與紀錄檔
- `coordination/progress/<agent>.md` 只能由該 agent 更新
- `coordination/completed/<agent>.md` 只能由該 agent 更新
- 共用核心檔由主控決定合併順序

## Escalation Rule

出現以下情況時，不直接硬改，先寫 incident：

- 資料契約不明
- 公式或狀態機衝突
- 需要跨 agent 改同一個 service / model
- 需要更改 Phase 0 凍結決策

## GitHub Workflow

- 詳細 branch / PR 流程見 `docs/operations/github-branch-and-pr-flow.md`
- 第二輪派工規範見 `docs/operations/github-second-round-collaboration.md`
