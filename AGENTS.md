# Rental Rebuild — Persistent Project Memory Protocol

本專案的可延續記憶以版本控制中的文件為準；不可只依賴單一對話的上下文。

## New Task / Handoff Read Order

每個新 task 在開始實作前，依序閱讀：

1. `README.md`
2. `CONTEXT.md`
3. `COLLABORATION_RULES.md`
4. `docs/operations/phase1-master-status.md`
5. `docs/operations/current-dispatch-and-handoff-plan.md`
6. 對應的 `coordination/progress/<agent>.md` 與 `coordination/completed/<agent>.md`
7. 與工作範圍直接相關的資料契約、ADR、task-board 條目與 handoff

若這些文件互相衝突，先停止實作並在 `coordination/incidents/` 記錄衝突；不得自行猜測或覆寫既有決策。

## Delivery Loop

1. 開始工作時，將負責範圍、目前狀態與預定驗證更新至 `coordination/progress/<agent>.md`。
2. 每完成一個可驗收部分，先執行相應驗證，再更新 `coordination/completed/<agent>.md`。
3. 完成紀錄至少包含：完成項目、變更檔案、驗證指令與結果、已知限制、下一步或交接對象。
4. 在對話回覆中明確寫出「已記錄」，並指出更新的紀錄檔；不可只口頭宣告完成。
5. 需要跨 task 延續時，將可立即接手的下一步與必要背景寫入 `coordination/handoffs/`。

## Definition of Done

一項工作只有在程式或文件完成、驗證結果已留下、完成紀錄已更新，且對話中已告知使用者「已記錄」時，才算完成。

## 固定工作流程技能

下列技能為本專案的固定流程；收到對應用語時必須先完整閱讀並遵循：

- 「初始化專案」：`D:\CodexRuntime\docs\chezmoi-codex-seed\dot_codex\skills\initialize-project\SKILL.md`
- 「開工」：`D:\CodexRuntime\docs\chezmoi-codex-seed\dot_codex\skills\start-work\SKILL.md`
- 「收工」：`D:\CodexRuntime\docs\chezmoi-codex-seed\dot_codex\skills\finish-work\SKILL.md`

「收工」流程須執行最終差異與驗證檢查、更新既有 handoff；若 `handoff.md` 不存在，先取得使用者同意才可建立。提交、推送與部署均須另外取得明確授權。

## Existing Sources of Truth

- 架構與決策：`docs/reports/`
- 主控狀態：`docs/operations/phase1-master-status.md`
- 進行中工作：`coordination/progress/` 與 `coordination/task-board/in_progress/`
- 完成紀錄：`coordination/completed/` 與 `coordination/task-board/done/`
- 阻塞與風險：`coordination/incidents/`
