# Phase 1 Review And Support Messages

## 給 reasonix

你現在負責 **Phase 1 契約審查**。不要重做架構決策，不要改動大範圍程式。

先讀：

- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-architecture-decision.md`
- `D:\CodexRuntime\rental\rebuild\data_contracts\*.md`
- `D:\CodexRuntime\rental\rebuild\app\core\year_month.py`
- `D:\CodexRuntime\rental\rebuild\app\models\*.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\auth\*.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\dashboard\*.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\billing\*.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\rooms\*.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\contracts\*.py`

你的目標：

- 審查目前已完成的 `auth + dashboard + billing + rooms + contracts` 是否違反已凍結契約

請重點檢查：

- `year_month` 是否只透過 helper 轉換
- `MonthlyBill.total` 是否只走正式公式
- `Room.status` / `Contract.status` 是否符合正式狀態機
- 有沒有重新引入虛擬 tenant / 舊 Payment 死碼
- 合約建立 / 終止時 room status 是否同步正確

輸出位置：

- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-phase1-review.md`

內容格式：

- Finding
- Severity
- File
- Why it violates contract
- Required fix

若沒有問題，也要明確寫「No contract violations found」。

工作紀錄：

- 更新 `coordination/progress/reasonix.md`
- 完成後更新 `coordination/completed/reasonix.md`

## 給 mimo

你現在負責 **Phase 1 已完成頁面的實測驗收補充**。不要寫程式碼。

先讀：

- `D:\CodexRuntime\rental\rebuild\app\modules\auth\*.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\dashboard\*.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\billing\*.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\rooms\*.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\contracts\*.py`
- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-ui-field-matrix.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-test-scenarios.md`
- `D:\CodexRuntime\rental\rebuild\evidence\mimo-regression-checklist.md`

你的目標：

- 針對 `auth / dashboard / billing / rooms / contracts` 五塊，補一版可直接驗收的 evidence 區塊
- 修正 checklist 裡對這五頁不夠精確的驗證描述

你要補的內容：

- 每頁的手測步驟
- 每頁的預期畫面結果
- 每頁的對應查詢或驗證依據
- 已可運行骨架與尚未實作區塊的區分

直接更新：

- `D:\CodexRuntime\rental\rebuild\evidence\mimo-regression-checklist.md`

工作紀錄：

- 更新 `coordination/progress/mimo.md`
- 完成後更新 `coordination/completed/mimo.md`

## 給 box

你現在負責 **migration / repair 腳本草案整理**。不要碰 app 主程式骨架。

先讀：

- `D:\CodexRuntime\rental\rebuild\evidence\box-small-fix-notes.md`
- `D:\CodexRuntime\rental\rebuild\data_contracts\billing-contract.md`
- `D:\CodexRuntime\rental\rebuild\data_contracts\payments-contract.md`
- `D:\CodexRuntime\rental\rebuild\data_contracts\status-machines.md`
- `D:\CodexRuntime\rental\rebuild\data_contracts\migration-and-compatibility.md`

你的目標：

- 為下列項目各寫一份腳本草案說明：
  - `user/users` 合併
  - `MonthlyBill.year_month` 正規化
  - `ElectricityBill.year_month` 正規化
  - 虛擬 tenant 清理

每份草案至少要有：

- 目標
- 影響資料表
- 更新規則
- 驗證 SQL
- 回滾方式

直接更新：

- `D:\CodexRuntime\rental\rebuild\evidence\box-small-fix-notes.md`

若需要拆分，可另建：

- `D:\CodexRuntime\rental\rebuild\scripts\migration\README-<topic>.md`

工作紀錄：

- 更新 `coordination/progress/box.md`
- 完成後更新 `coordination/completed/box.md`
