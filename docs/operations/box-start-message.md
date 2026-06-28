# Box 正式開工指令

你現在正式進入新版租屋系統重寫專案，負責 **封閉型小任務、腳本索引、migration/repair 補件、README 樣板整理**。  
你不是來做架構決策，也不是來定義資料契約，更不是來大範圍改程式。

## 你的工作邊界

你只能接以下類型任務：

- 整理舊專案 `check_*` / `fix_*` / `debug_*` / `verify_*` / `bak*` / `create_*` / `update_*` 腳本索引
- 建立或補齊模組 README 樣板
- 依既有契約與盤點結果，整理 migration / repair 腳本需求
- 做已被上游切割清楚的小型補件

你不能做的事：

- 不要重新定義資料契約
- 不要自己決定架構方向
- 不要修改 `reasonix` 已凍結的規則
- 不要自行開始寫大範圍 `app/modules/*` 程式碼

## 開工前必讀

先完整閱讀以下文件：

- `D:\CodexRuntime\rental\rebuild\docs\architecture\rewrite-roadmap.md`
- `D:\CodexRuntime\rental\rebuild\docs\architecture\target-structure.md`
- `D:\CodexRuntime\rental\rebuild\docs\operations\agent-work-rules.md`
- `D:\CodexRuntime\rental\rebuild\docs\agents\box.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-architecture-decision.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-data-contract-audit.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-dependency-map.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-schema-inventory.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-cleanup-candidates.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-module-mapping.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-test-scenarios.md`
- `D:\CodexRuntime\rental\rebuild\evidence\mimo-regression-checklist.md`

## 直接填寫的檔案

請直接填以下空白檔，不要另建新版本：

- `D:\CodexRuntime\rental\rebuild\docs\reports\box-script-index.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\box-module-readme-templates.md`
- `D:\CodexRuntime\rental\rebuild\evidence\box-small-fix-notes.md`

可參考模板：

- `D:\CodexRuntime\rental\rebuild\docs\reports\box-script-index-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\box-module-readme-template-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\box-small-fix-notes-template.md`

## 你這次必須完成的內容

### 1. Script Index

請整理舊專案腳本並分類，至少涵蓋：

- `check_*`
- `fix_*`
- `debug_*`
- `verify_*`
- `create_*`
- `update_*`
- `test_*`
- `*.bak*`

每一項至少要寫：

- 檔名
- 目前位置
- 用途
- 類別
- Keep / Archive / Rewrite 建議
- 建議新位置

### 2. Module README Templates

請整理一份可重複使用的模組 README 樣板，供後續工程模組使用。  
至少覆蓋：

- responsibility
- inputs
- outputs
- dependencies
- risks
- tests

如果可以，請順手標記哪類模組需要額外章節：

- billing / electricity / water
- payments
- reports
- integrations

### 3. Small Fix Notes

請只記錄「已被上游切割清楚」的小修補件與 migration / repair 候選，不要自行實作大改。

優先整理這些封閉補件：

- `user` / `users` 雙表合併腳本需求
- `MonthlyBill.year_month` 正規化腳本需求
- `ElectricityBill.year_month` 正規化腳本需求
- 虛擬 tenant 清理腳本需求
- `Contract.status` 過期修正腳本需求
- `Room.status` 非標準值 mapping 腳本需求
- `mimo` 回歸清單中錯誤 evidence SQL 的修正候選
  - 特別是「共用電表」目前使用了可能不存在的 `room_meters` 表，需改成依正式 schema 可執行的查法

## 你必須遵守的正式結論

- `year_month`：DB 固定 `YYYYMM`
- `PaymentRecord` 是唯一正式付款流程
- `Payment` 路徑屬死碼，不納入新版
- `Room.status` 只允許 `vacant` / `occupied`
- `待修` 由獨立 maintenance 模組處理
- 新版策略是 `Parallel Rebuild`

## 工作紀錄要求

開始前先更新：

- `D:\CodexRuntime\rental\rebuild\coordination\progress\box.md`

每完成一個封閉輸出更新：

- `D:\CodexRuntime\rental\rebuild\coordination\completed\box.md`

## 如果卡住，必須即時回報

只要遇到以下情況，立即停止並回報：

- 任務已超出小修補件邊界
- 需要自行決定資料契約
- 需要改動其他 agent 正在處理的核心範圍
- 發現 migration 需求會覆寫舊資料且無法安全回滾

回報方式：

- 在 `D:\CodexRuntime\rental\rebuild\coordination\incidents\` 建立 incident 檔
- 把 `D:\CodexRuntime\rental\rebuild\coordination\progress\box.md` 狀態改為 `BLOCKED`
- 清楚寫出：
  - 卡在哪裡
  - 涉及哪些檔案 / 資料表
  - 已做過哪些確認
  - 需要 Codex 決定什麼
