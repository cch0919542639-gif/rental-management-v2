# 可直接貼給各 Agent 的派工指令

## 給 reasonix

你現在負責新版租屋系統的架構決策與資料契約凍結。不要先做大量修補，也不要直接去改舊系統 `D:\rental`。

先讀：

- `D:\CodexRuntime\rental\rebuild\docs\architecture\rewrite-roadmap.md`
- `D:\CodexRuntime\rental\rebuild\docs\architecture\target-structure.md`
- `D:\CodexRuntime\rental\rebuild\docs\operations\agent-work-rules.md`
- `D:\CodexRuntime\rental\rebuild\docs\agents\reasonix.md`
- `D:\CodexRuntime\rental\rebuild\data_contracts\`

直接填寫這些檔案：

- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-architecture-decision.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-data-contract-audit.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-dependency-map.md`

可參考模板：

- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-architecture-decision-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-data-contract-audit-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-dependency-map-template.md`

你必須先回答：

- `year_month` 正式格式是什麼
- `user` / `users` 雙表怎麼處理
- 付款流程正式保留哪一條主路徑
- 空房 / 待修 是否還能留在 tenant 名稱邏輯
- 新版應採平行重寫、原地重構，還是 hybrid

工作記錄要求：

- 開工前更新 `D:\CodexRuntime\rental\rebuild\coordination\progress\reasonix.md`
- 每完成一份文件更新 `D:\CodexRuntime\rental\rebuild\coordination\completed\reasonix.md`

若遇到以下情況，立即回報：

- 無法唯一決定資料契約
- 發現核心流程互相衝突
- 遷移風險無法評估

回報方式：

- 在 `D:\CodexRuntime\rental\rebuild\coordination\incidents\` 新增 incident 檔
- 把 `progress\reasonix.md` 狀態改成 `NEEDS-DECISION`

## 給 open

你現在負責舊系統盤點、route/template/schema 清單與新舊模組映射。不要自創資料規則，必須以 `reasonix` 的結論為準。

先讀：

- `D:\CodexRuntime\rental\rebuild\docs\architecture\rewrite-roadmap.md`
- `D:\CodexRuntime\rental\rebuild\docs\architecture\target-structure.md`
- `D:\CodexRuntime\rental\rebuild\docs\operations\agent-work-rules.md`
- `D:\CodexRuntime\rental\rebuild\docs\agents\open.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-architecture-decision.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-data-contract-audit.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-dependency-map.md`

直接填寫這些檔案：

- `D:\CodexRuntime\rental\rebuild\docs\reports\open-route-template-matrix.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-schema-inventory.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-cleanup-candidates.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-module-mapping.md`

可參考模板：

- `D:\CodexRuntime\rental\rebuild\docs\reports\open-route-template-matrix-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-schema-inventory-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-cleanup-candidates-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-module-mapping-template.md`

你必須先整理清楚：

- 每個 route 對應哪個 template
- 每個報表/列表主要依賴哪些 query 與資料表
- 舊專案哪些檔案可封存、可重寫成正式 script、或疑似死碼
- 舊模組應映射到新版哪個 module

工作記錄要求：

- 開工前更新 `D:\CodexRuntime\rental\rebuild\coordination\progress\open.md`
- 每完成一份盤點文件更新 `D:\CodexRuntime\rental\rebuild\coordination\completed\open.md`

若遇到以下情況，立即回報：

- 舊系統實際結構與 `reasonix` 契約衝突
- 無法判定 route/template/schema 真實對應
- 發現高風險邏輯但無法安全分類

回報方式：

- 在 `D:\CodexRuntime\rental\rebuild\coordination\incidents\` 新增 incident 檔
- 把 `progress\open.md` 狀態改成 `BLOCKED`

## 給 mimo

你現在負責 UI 欄位來源盤點、測試情境與回歸檢查表。不要自己發明欄位語義，必須依 `reasonix` 契約與 `open` 的盤點結果工作。

先讀：

- `D:\CodexRuntime\rental\rebuild\docs\architecture\rewrite-roadmap.md`
- `D:\CodexRuntime\rental\rebuild\docs\architecture\target-structure.md`
- `D:\CodexRuntime\rental\rebuild\docs\operations\agent-work-rules.md`
- `D:\CodexRuntime\rental\rebuild\docs\agents\mimo.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reporting-contract-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-architecture-decision.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-route-template-matrix.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-schema-inventory.md`

直接填寫這些檔案：

- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-ui-field-matrix.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-test-scenarios.md`
- `D:\CodexRuntime\rental\rebuild\evidence\mimo-regression-checklist.md`

可參考模板：

- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-ui-field-matrix-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-test-scenarios-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-regression-checklist-template.md`

你必須先整理清楚：

- 每個頁面欄位對應哪個來源欄位
- 哪些頁面顯示規則有空值、錯值、雙重來源風險
- 關鍵情境：空房、待修、新簽約、退租、未繳、溢繳、共用電表、共用水表

工作記錄要求：

- 開工前更新 `D:\CodexRuntime\rental\rebuild\coordination\progress\mimo.md`
- 每完成一份驗證文件更新 `D:\CodexRuntime\rental\rebuild\coordination\completed\mimo.md`

若遇到以下情況，立即回報：

- 欄位來源不唯一
- 同頁面存在多套資料語義
- 找不到支撐畫面欄位的正式資料來源

回報方式：

- 在 `D:\CodexRuntime\rental\rebuild\coordination\incidents\` 新增 incident 檔
- 把 `progress\mimo.md` 狀態改成 `BLOCKED`

## 給 box

你現在只負責封閉型小任務、腳本索引、README 樣板與小型補件。不要接核心架構、資料契約或跨模組決策。

先讀：

- `D:\CodexRuntime\rental\rebuild\docs\architecture\rewrite-roadmap.md`
- `D:\CodexRuntime\rental\rebuild\docs\architecture\target-structure.md`
- `D:\CodexRuntime\rental\rebuild\docs\operations\agent-work-rules.md`
- `D:\CodexRuntime\rental\rebuild\docs\agents\box.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-architecture-decision.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-cleanup-candidates.md`

直接填寫這些檔案：

- `D:\CodexRuntime\rental\rebuild\docs\reports\box-script-index.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\box-module-readme-templates.md`
- `D:\CodexRuntime\rental\rebuild\evidence\box-small-fix-notes.md`

可參考模板：

- `D:\CodexRuntime\rental\rebuild\docs\reports\box-script-index-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\box-module-readme-template-template.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\box-small-fix-notes-template.md`

你只能接這類任務：

- 整理 `check_*` / `fix_*` / `debug_*` / `verify_*` / `bak*` 索引
- 建立樣板
- 做已經切割清楚的小修補件

工作記錄要求：

- 開工前更新 `D:\CodexRuntime\rental\rebuild\coordination\progress\box.md`
- 每完成一個封閉輸出更新 `D:\CodexRuntime\rental\rebuild\coordination\completed\box.md`

若遇到以下情況，立即回報：

- 任務已超出小修補件邊界
- 需要跨模組決策
- 需要自行解釋資料契約

回報方式：

- 在 `D:\CodexRuntime\rental\rebuild\coordination\incidents\` 新增 incident 檔
- 把 `progress\box.md` 狀態改成 `BLOCKED`
