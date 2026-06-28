# Contributing

## Scope

本 repo 是租屋管理系統新版重寫工作區。所有協作者、agent、其他電腦上的工作夥伴，都應只在這個 repo 內協作，不直接把 `D:\rental` 舊系統當主施工區。

## Read First

1. `README.md`
2. `docs/operations/phase1-master-status.md`
3. `docs/operations/agent-work-rules.md`
4. 自己對應的 agent / 任務文件

## Branch Rule

- 不直接在 `main` 上施工
- 每一輪任務使用一條 branch
- branch 命名規則見 `docs/operations/github-branch-and-pr-flow.md`

## Required Work Log

每次開工與收工都要更新：

- `coordination/progress/<agent>.md`
- `coordination/completed/<agent>.md`

若出現阻塞或規格不明：

- 新增 `coordination/incidents/<timestamp>_<agent>_<topic>.md`

若需要交接：

- 新增 `coordination/handoffs/<timestamp>_<from>_to_<to>.md`

## Pull Request Rule

- PR 前先確認沒有改到不屬於自己範圍的核心檔案
- PR 內容必須包含：
- 變更範圍
- 依據的規格文件
- 驗證方式
- 尚未解決風險

PR 模板見 `.github/PULL_REQUEST_TEMPLATE.md`。

## High-Risk Files

以下檔案或目錄屬高衝突區，未經主控同意不要多人同時修改：

- `app/models/`
- `app/services/`
- `data_contracts/`
- `docs/reports/reasonix-architecture-decision.md`

## Do Not Commit

不要提交以下內容：

- `.env`
- `runtime.db`
- `__pycache__/`
- 本機 IDE 設定
- 暫存 log / cache
