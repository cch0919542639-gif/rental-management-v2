# Current Dispatch And Handoff Plan

Last Updated: 2026-06-28 15:18
Owner: Codex

## GitHub Status

- GitHub `origin/main` 目前仍停在 commit `61f84a4`
- 本機已完成但尚未推送的內容：
- `landlords`
- `payments`
- `electricity`
- `water`
- `reports`
- `maintenance`
- integration smoke tests
- demo seed script
- warnings 收斂

## Codex Current Priority

### In Progress

- 補 `dev runbook`
- 補啟動 / 驗證腳本
- 補其他電腦接手文件
- 補本輪 push 指令與提交範圍摘要

### Next

- 整理並提交本機未推送變更
- 視情況擴充更多 integration tests
- 視情況補正式 runbook / deployment notes

## Agent Work Allocation

### `reasonix`

- 任務：
- 審核 Phase 1 現有主幹是否有契約偏移
- 特別檢查 `reports`、`payments`、`electricity`、`water`
- 產出 Phase 1 review note

- 不應做：
- 不直接重寫主幹
- 不自行新增 schema

### `open`

- 任務：
- 對齊 route matrix 與目前實作
- 補「尚未完成 route / 舊系統對應缺口」清單
- 協助整理可進 Phase 2 的功能缺口

- 不應做：
- 不修改高衝突資料契約
- 不自行變更狀態機語義

### `mimo`

- 任務：
- 針對已完成頁面做 UI 欄位對齊
- 補手動回歸清單與視覺一致性修正
- 針對 `reports`、`payments`、`electricity`、`water` 補 Evidence

- 不應做：
- 不自行定義後端規則
- 不改 service 公式

### `box`

- 任務：
- 擴充 smoke/integration tests
- 補 runbook 細節
- 補低風險 scripts，例如 `run_dev.ps1`、`run_smoke_tests.ps1` 的改良

- 不應做：
- 不主導 schema 或跨模組狀態機調整

## Other Computer Handoff Order

1. `git pull`
2. 讀 `README.md`
3. 讀 `docs/operations/phase1-master-status.md`
4. 讀本檔
5. 讀 `docs/operations/dev-runbook.md`
6. 安裝依賴
7. 跑 demo seed
8. 跑 smoke tests
9. 更新自己的 `coordination/progress/<agent>.md`
10. 再開始開工

## Definition Of Ready For Another Computer

- 依賴檔已存在
- runbook 已存在
- seed script 已存在
- smoke tests 已存在
- handoff / dispatch 文件已存在

## Definition Of Next Safe Push

- `pytest tests\integration -q` 通過
- `python .\scripts\seed_demo_data.py` 通過
- `git status` 僅含本輪預期變更
- `coordination/progress/codex.md` 已更新
- 依 `docs/operations/push-phase1-baseline-instructions.md` 執行
