# Phase 1 Agent Dispatch Messages

以下是四個 agent 下一輪可直接貼上的正式派工指令。

## 給 open

你現在負責 **`rooms + contracts` 最小 CRUD 骨架實作**。不要重做盤點，也不要重新定義資料契約。

先讀：

- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-architecture-decision.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-module-mapping.md`
- `D:\CodexRuntime\rental\rebuild\data_contracts\core-entities.md`
- `D:\CodexRuntime\rental\rebuild\data_contracts\status-machines.md`
- `D:\CodexRuntime\rental\rebuild\app\models\parties.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\rooms\README.md`
- `D:\CodexRuntime\rental\rebuild\app\modules\contracts\README.md`

你的目標：

- 建立 `modules/rooms/` 最小可運行骨架
- 建立 `modules/contracts/` 最小可運行骨架
- 補齊對應的 forms / routes / templates
- 補齊必要 repository 查詢

你必須遵守：

- `Room.status` 只允許 `vacant` / `occupied`
- `Contract.status` 只允許 `active` / `expired` / `terminated`
- 同一房間不可有兩筆 active contract
- `Contract` 終止時，需同步讓 `Room.status` 轉成 `vacant`
- 不可引入虛擬 tenant 名稱邏輯

建議輸出：

- `D:\CodexRuntime\rental\rebuild\app\modules\rooms\forms.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\rooms\routes.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\contracts\forms.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\contracts\routes.py`
- 對應 templates

工作紀錄：

- 更新 `coordination/progress/open.md`
- 完成後更新 `coordination/completed/open.md`

若卡住：

- 開 incident
- `progress/open.md` 改成 `BLOCKED`

## 給 reasonix

你現在負責 **Phase 1 契約審查**。不要重做架構決策，不要大改程式。

先讀：

- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-architecture-decision.md`
- `D:\CodexRuntime\rental\rebuild\data_contracts\*.md`
- `D:\CodexRuntime\rental\rebuild\app\core\year_month.py`
- `D:\CodexRuntime\rental\rebuild\app\models\*.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\auth\*.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\dashboard\*.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\billing\*.py`

你的目標：

- 審查目前已完成的 `auth + dashboard + billing` 骨架是否違反已凍結契約

重點檢查：

- `year_month` 是否只透過 helper 轉換
- `MonthlyBill.total` 是否只走正式公式
- `PaymentRecord` 是否仍是唯一正式付款實體
- 有沒有重新引入虛擬 tenant / 舊 Payment 死碼 / 非正式 status

輸出方式：

- 直接新增一份 review 文件：
  - `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-phase1-review.md`

內容只要：

- 發現的違反契約點
- 嚴重度
- 需要修正的檔案
- 不要重開新方向

工作紀錄：

- 更新 `coordination/progress/reasonix.md`
- 完成後更新 `coordination/completed/reasonix.md`

## 給 mimo

你現在負責 **已完成頁面的實測驗收補充**。不要寫程式碼。

先讀：

- `D:\CodexRuntime\rental\rebuild\app\modules\auth\*.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\dashboard\*.py`
- `D:\CodexRuntime\rental\rebuild\app\modules\billing\*.py`
- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-ui-field-matrix.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-test-scenarios.md`
- `D:\CodexRuntime\rental\rebuild\evidence\mimo-regression-checklist.md`

你的目標：

- 針對 `auth / dashboard / billing` 三塊，補一版可直接驗收的 evidence 區塊
- 修正目前 checklist 裡對這三頁不夠精確的驗證描述

你要補的內容：

- 每頁的手測步驟
- 每頁的預期畫面結果
- 每頁的對應查詢或驗證依據

輸出位置：

- 直接更新：
  - `D:\CodexRuntime\rental\rebuild\evidence\mimo-regression-checklist.md`

工作紀錄：

- 更新 `coordination/progress/mimo.md`
- 完成後更新 `coordination/completed/mimo.md`

## 給 box

你現在負責 **migration / repair 腳本草案**。不要碰 app 主程式骨架。

先讀：

- `D:\CodexRuntime\rental\rebuild\docs\reports\box-small-fix-notes.md`
- `D:\CodexRuntime\rental\rebuild\data_contracts\billing-contract.md`
- `D:\CodexRuntime\rental\rebuild\data_contracts\payments-contract.md`
- `D:\CodexRuntime\rental\rebuild\data_contracts\status-machines.md`
- `D:\CodexRuntime\rental\rebuild\data_contracts\migration-and-compatibility.md`

你的目標：

- 為下列項目各寫一份腳本草案說明，不要求完整可執行，但要足夠讓工程端照著實作：
  - `user/users` 合併
  - `MonthlyBill.year_month` 正規化
  - `ElectricityBill.year_month` 正規化
  - 虛擬 tenant 清理

每一份草案至少要有：

- 目標
- 影響資料表
- 更新規則
- 驗證 SQL
- 回滾方式

輸出位置：

- 直接更新：
  - `D:\CodexRuntime\rental\rebuild\evidence\box-small-fix-notes.md`

如有需要可另建：

- `D:\CodexRuntime\rental\rebuild\scripts\migration\README-<topic>.md`

工作紀錄：

- 更新 `coordination/progress/box.md`
- 完成後更新 `coordination/completed/box.md`
