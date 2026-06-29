# Phase 2 Parallel Dispatch Index

Date: 2026-06-29
Owner: Codex
Branch Baseline: `codex-phase2-mainline-01`

## Current Mainline Status

- `nested creation` 已進主幹
- `maintenance Phase 2B` 已進主幹
- `electricity property detail / new-bill / quick-reading / reading-log` 已進主幹
- Integration baseline: `38 passed, 15 skipped`

## Dispatch Files

- `D:\CodexRuntime\rental\rebuild\docs\operations\dispatch-open-phase2-gap-recheck-2026-06-29.md`
- `D:\CodexRuntime\rental\rebuild\docs\operations\dispatch-mimo-phase2-ui-regression-2026-06-29.md`
- `D:\CodexRuntime\rental\rebuild\docs\operations\dispatch-reasonix-phase2-migration-boundary-2026-06-29.md`
- `D:\CodexRuntime\rental\rebuild\docs\operations\dispatch-box-hermes-phase2-tests-runbook-2026-06-29.md`

## Parallel / Sequence Rule

- `open`、`mimo`、`reasonix`、`box/hermes` 這四份工作可同步進行
- 不需要等待彼此完成
- 都不得改 `app/models/*`、不得改已凍結資料契約
- 若發現需要改資料契約、狀態機或核心公式，必須建立 incident 回報 Codex

## Shared Reporting Rule

- 開工前更新 `coordination/progress/<agent>.md`
- 完成後更新 `coordination/completed/<agent>.md`
- 若被阻塞，建立 `coordination/incidents/<timestamp>_<agent>_<topic>.md`
- 若使用 task-board：
  - 接手時移到 `coordination/task-board/in_progress/`
  - 完成待驗收時移到 `coordination/task-board/review/`

