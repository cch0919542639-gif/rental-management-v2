# Mimo 正式開工指令

你現在正式進入新版租屋系統重寫專案，負責 **UI 欄位來源盤點、測試情境、回歸檢查表**。  
你不是來建立模組程式碼，也不要自行定義資料契約。你的依據是 `reasonix` 已凍結的規格，以及 `open` 已完成的盤點結果。

## 你的目標

完成以下三份正式輸出：

- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-ui-field-matrix.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-test-scenarios.md`
- `D:\CodexRuntime\rental\rebuild\evidence\mimo-regression-checklist.md`

## 開工前必讀

先完整閱讀以下文件，不要跳過：

- `D:\CodexRuntime\rental\rebuild\docs\architecture\rewrite-roadmap.md`
- `D:\CodexRuntime\rental\rebuild\docs\architecture\target-structure.md`
- `D:\CodexRuntime\rental\rebuild\docs\operations\agent-work-rules.md`
- `D:\CodexRuntime\rental\rebuild\docs\agents\mimo.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reporting-contract-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-architecture-decision.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-data-contract-audit.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-dependency-map.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-route-template-matrix.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-schema-inventory.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-cleanup-candidates.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-module-mapping.md`

## 直接填寫的檔案

請直接填以下空白檔，不要另外自建版本：

- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-ui-field-matrix.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-test-scenarios.md`
- `D:\CodexRuntime\rental\rebuild\evidence\mimo-regression-checklist.md`

可參考模板：

- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-ui-field-matrix-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-test-scenarios-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-regression-checklist-template.md`

## 你這次必須完成的內容

### 1. UI Field Matrix

你必須為主要頁面建立欄位來源對照，至少涵蓋：

- Dashboard
- Landlords
- Properties / Rooms
- Tenants
- Contracts
- Monthly Bills
- Electricity
- Water
- Payments
- Monthly Report
- Landlord Report（即使舊版未註冊，也要標記它是孤立報表）

每個欄位至少要交代：

- 畫面欄位名稱
- template/display variable
- 來源模組
- 來源資料實體 / 欄位
- 空值顯示規則
- 風險等級

### 2. Test Scenarios

請建立關鍵測試情境，至少涵蓋：

- 正常登入
- 空房顯示
- 待修房顯示
- 新簽約當月帳單
- 已到期合約
- 提前終止合約
- 未繳帳單
- 溢繳 / 對帳
- 共用電表
- 共用水表
- year_month 格式轉換
- PaymentRecord 驗證 / 連結狀態

### 3. Regression Checklist

請整理一份可供人工驗收的回歸清單，至少要能檢查：

- 主要列表頁顯示是否正確
- 月帳單總額是否與契約一致
- 電費與水費顯示是否與來源一致
- payment status 是否與正式資料契約一致
- 月報 / 房東報表總額是否與來源一致

## 明確限制

- 不要建立新的資料契約
- 不要自行判定 `year_month` 或 occupancy 規則
- 不要開始寫 `app/modules/*` 程式碼
- 不要把舊系統的虛擬 tenant 名稱邏輯當成新版正規做法

## 你必須依據的正式結論

- `year_month`：DB 固定 `YYYYMM`，UI/API 才使用 `YYYY-MM`
- `PaymentRecord` 是唯一正式付款流程
- `Payment` 路徑屬死碼，不納入新版
- `Room.status` 只允許 `vacant` / `occupied`
- `待修` 需獨立處理，不得再由 tenant 名稱承載

## 工作紀錄要求

開始前先更新：

- `D:\CodexRuntime\rental\rebuild\coordination\progress\mimo.md`

每完成一份文件更新：

- `D:\CodexRuntime\rental\rebuild\coordination\completed\mimo.md`

## 如果卡住，必須即時回報

只要遇到以下情況，立即停止並回報：

- 畫面欄位找不到唯一資料來源
- 同一頁面出現兩套不同資料語義
- `open` 的 route/template mapping 與 `reasonix` 契約衝突
- 報表欄位無法追溯到正式資料契約

回報方式：

- 在 `D:\CodexRuntime\rental\rebuild\coordination\incidents\` 建立 incident 檔
- 把 `D:\CodexRuntime\rental\rebuild\coordination\progress\mimo.md` 狀態改為 `BLOCKED`
- 清楚寫出：
  - 卡在哪裡
  - 哪些頁面/欄位受影響
  - 已做過哪些確認
  - 需要 Codex 決定什麼
