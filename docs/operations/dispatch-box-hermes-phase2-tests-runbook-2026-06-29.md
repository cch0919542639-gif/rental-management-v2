# 給 box / hermes 的派工指令

你現在負責 **Phase 2 tests + runbook 補強**。  
這次目標是為已進主幹的新流程補測試、補驗證說明、補開發操作文檔。你可以改測試與文件；不要改 model，不要改核心 service 規則。

## 你的目標

圍繞目前已進主幹的新功能，補強：

- integration coverage
- 單支測試執行說明
- 本地手動驗證步驟
- runbook 中對 `electricity property workflows` 的操作指引

## 先讀

- `D:\CodexRuntime\rental\rebuild\coordination\progress\codex.md`
- `D:\CodexRuntime\rental\rebuild\docs\operations\phase2-parallel-dispatch-index-2026-06-29.md`
- `D:\CodexRuntime\rental\rebuild\docs\operations\dev-runbook.md`
- `D:\CodexRuntime\rental\rebuild\tests\README.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\box-phase2-test-matrix-04.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\box-phase2-test-matrix-05.md`

## 可修改範圍

- `tests/integration/*`
- `tests/README.md`
- `docs/operations/dev-runbook.md`
- `scripts/README.md`
- 低風險 wrapper / helper scripts
- `coordination/progress/box.md`
- `coordination/completed/box.md`

## 直接交付

請直接建立並填寫：

- `D:\CodexRuntime\rental\rebuild\docs\reports\box-phase2-test-runbook-06.md`

## 這次優先任務

至少完成其中大部分：

1. 為 `electricity property workflows` 增補 integration coverage 或 matrix 說明
2. 補 `reading-log` / `quick-reading` 的手動驗證步驟
3. 更新 runbook，讓其他電腦知道如何從本地登入後操作這些新頁面
4. 若有必要，補單支測試執行說明或 wrapper 使用說明

## 明確限制

- 不要改 `app/models/*`
- 不要改 billing/electricity/water 核心公式
- 不要碰資料契約
- 不要把 placeholder 測試硬轉正，除非主幹功能真的已存在

## 驗收標準

你的交付至少要交代：

- 新增或更新了哪些測試 / 文件
- 這些測試驗證了什麼
- 目前 baseline 是多少 pass / skip
- 哪些 skip 仍應保持 skip

## 工作紀錄要求

- 開工前更新 `D:\CodexRuntime\rental\rebuild\coordination\progress\box.md`
- 完成後更新 `D:\CodexRuntime\rental\rebuild\coordination\completed\box.md`

## 如果卡住

遇到以下情況請回報：

- 測試需要未存在的 route / model / status transition
- 文件與實際主幹不一致
- 需要改核心程式才能讓測試過

回報方式：

- 新增 `D:\CodexRuntime\rental\rebuild\coordination\incidents\<timestamp>_box_<topic>.md`
- 把 `progress/box.md` 狀態改成 `BLOCKED`

