# Reasonix 續跑指令

你上次已完成：

- 閱讀 `data_contracts/` 全部文件
- 閱讀 roadmap、target-structure、agent-work-rules、reasonix 任務書
- 更新 `coordination/progress/reasonix.md`

你上次中斷前的狀態是：

- `Status: IN-PROGRESS`
- 無 blocker
- 下一步是填寫三份正式輸出檔

請不要重做前面的閱讀與盤點，直接從目前狀態續跑，完成以下三份檔案：

- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-architecture-decision.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-data-contract-audit.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-dependency-map.md`

可參考模板：

- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-architecture-decision-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-data-contract-audit-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-dependency-map-template.md`

這次請直接產出內容，不要只保留空白模板。你必須明確回答以下五點：

1. `MonthlyBill.year_month` 的正式規格與轉換策略
2. `user` / `users` 雙表的處理方式
3. 付款流程正式保留 `PaymentRecord`、淘汰未完成 `Payment` 路徑的理由與方式
4. 空房 / 待修 / 待補 不能再依賴 tenant 名稱的替代方案
5. 新版應採 `parallel rebuild`、`refactor in place` 或 `hybrid`，以及理由

輸出要求：

- `reasonix-architecture-decision.md`
  - 要有明確決策，不可只列選項
- `reasonix-data-contract-audit.md`
  - 至少先完成核心實體與高風險欄位稽核：
    - `User`
    - `MonthlyBill.year_month`
    - `PaymentRecord`
    - `Room.status`
    - `Contract.status`
- `reasonix-dependency-map.md`
  - 要寫出目前邊界違規點與建議切割線

工作紀錄要求：

- 開始前先更新 `D:\CodexRuntime\rental\rebuild\coordination\progress\reasonix.md`
- 每完成一份文件就更新 `D:\CodexRuntime\rental\rebuild\coordination\completed\reasonix.md`

若再次卡住，必須立即回報，不可直接中止：

- 在 `D:\CodexRuntime\rental\rebuild\coordination\incidents\` 建立 incident 檔
- 將 `progress\reasonix.md` 狀態改成 `NEEDS-DECISION`
- 清楚寫出卡點、已嘗試動作、需要 Codex 決定的事項
