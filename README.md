# Rental Rebuild Workspace

這是租屋管理系統的新版重寫工作區。各 agent 從這裡開始，不要直接在 `D:\rental` 舊系統上自由改動。

## 先讀文件順序

1. [docs/architecture/rewrite-roadmap.md](/abs/path/D:/CodexRuntime/rental/rebuild/docs/architecture/rewrite-roadmap.md)
2. [docs/architecture/target-structure.md](/abs/path/D:/CodexRuntime/rental/rebuild/docs/architecture/target-structure.md)
3. [docs/operations/agent-work-rules.md](/abs/path/D:/CodexRuntime/rental/rebuild/docs/operations/agent-work-rules.md)
4. 自己對應的 agent 任務書

## 開工規則

- 開工前先更新 `coordination/progress/<agent>.md`
- 完成一項工作後更新 `coordination/completed/<agent>.md`
- 發生錯誤或阻塞時，立即新增 `coordination/incidents/<timestamp>_<agent>_<topic>.md`
- 需要交接時，寫入 `coordination/handoffs/`

## 重寫原則

- 先固定資料契約，再寫模組
- 先建立新版結構，再逐步搬移功能
- 不接受舊案裡的隱性規則直接複製，必須文件化後再實作

## 目前目標

- 做出可以取代舊案的新版骨架
- 將核心模組拆開：`auth`、`properties`、`contracts`、`billing`、`electricity`、`water`、`payments`、`reports`、`integrations`
- 建立可驗證、可回滾、可移交的實作流程

## GitHub 協作入口

- `CONTRIBUTING.md`
- `COLLABORATION_RULES.md`
- `docs/operations/github-second-round-collaboration.md`
- `docs/operations/github-branch-and-pr-flow.md`
- `docs/operations/github-upload-checklist.md`
- `docs/operations/github-upload-agent-instructions.md`

## GitHub 上傳前

建議先執行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\github_preflight_check.ps1
```

## Quick Start

```powershell
python -m pip install -r .\requirements-dev.txt
python .\scripts\seed_demo_data.py
pytest tests\integration -q
powershell -ExecutionPolicy Bypass -File .\scripts\run_dev.ps1
```

接手前先讀：

- `docs/operations/phase1-master-status.md`
- `docs/operations/current-dispatch-and-handoff-plan.md`
- `docs/operations/dev-runbook.md`
