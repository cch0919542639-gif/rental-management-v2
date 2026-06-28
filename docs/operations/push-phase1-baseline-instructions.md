# Push Phase 1 Baseline Instructions

Last Updated: 2026-06-28 15:28

## Purpose

這份文件提供其他 agent 或其他電腦，將目前本機已完成但尚未推送的 Phase 1 baseline 一次整理、commit、push 到 GitHub 的標準做法。

## Current Remote State

- `origin/main` 目前仍停在 `61f84a4`

## What This Push Includes

這一批應推送的內容：

- `landlords` module
- `payments` module
- `electricity` module
- `water` module
- `reports` module
- `maintenance` module boundary
- repository / service 擴充
- `tests/conftest.py`
- `tests/integration/*`
- `scripts/seed_demo_data.py`
- `scripts/run_dev.ps1`
- `scripts/run_smoke_tests.ps1`
- `requirements-dev.txt`
- `docs/operations/dev-runbook.md`
- `docs/operations/current-dispatch-and-handoff-plan.md`
- `coordination/progress/codex.md`
- `docs/operations/phase1-master-status.md`

## Pre-Push Verification

先在 repo 根目錄執行：

```powershell
python .\scripts\seed_demo_data.py
powershell -ExecutionPolicy Bypass -File .\scripts\run_smoke_tests.ps1
git status --short
```

預期：

- seed 成功
- smoke tests 通過
- `git status` 只顯示本輪預期檔案

## Recommended Commit Message

```text
feat: add phase1 runnable baseline modules tests and runbook
```

## Push Steps

```powershell
cd D:\CodexRuntime\rental\rebuild
git add .
git status
git commit -m "feat: add phase1 runnable baseline modules tests and runbook"
git push origin main
```

## Post-Push Report

完成後必須回報：

- `git status --short --branch`
- 最新 commit hash
- push 是否成功
- 若失敗，卡在哪一步

## Do Not Mix In This Push

不要在這一輪順手加入：

- 新 schema 設計
- maintenance 正式 table
- deeper algorithm 改寫
- 不相關文件整理

這一輪目標是把已驗證完成的 Phase 1 baseline 送上 GitHub。
