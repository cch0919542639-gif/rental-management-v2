# Agent 工作規範

## 所有 agent 必做

1. 開工前讀：
- `docs/architecture/rewrite-roadmap.md`
- `docs/architecture/target-structure.md`
- 自己的 agent 任務書

2. 開工前登記：
- 更新 `coordination/progress/<agent>.md`

3. 每完成一個明確子任務：
- 更新 `coordination/completed/<agent>.md`

4. 遇到錯誤或阻塞：
- 立即新增 `coordination/incidents/<timestamp>_<agent>_<topic>.md`

5. 需要別的 agent 接手：
- 新增 `coordination/handoffs/<timestamp>_<from>_to_<to>.md`

## 進行中工作紀錄格式

- 目前任務
- 影響範圍
- 已完成步驟
- 下一步
- 風險或阻塞
- 最後更新時間

## 完成工作紀錄格式

- 完成項目
- 輸出檔案
- 驗證方式
- 尚未完成事項
- 可交接對象

## 即時錯誤回報規則

發生以下任一情況，必須立即回報：

- 無法確認資料契約
- 發現會破壞既有資料的修改
- 計算公式與舊資料不一致
- 付款、報表、電費、水費出現邏輯衝突
- 需要改動其他 agent 正在處理的範圍

## 錯誤回報給我怎麼做

1. 先在 `coordination/incidents/` 建立 incident 檔
2. 在自己的 `coordination/progress/<agent>.md` 最上方新增 `BLOCKED` 或 `NEEDS-DECISION`
3. 寫清楚：
- 問題是什麼
- 卡在哪裡
- 已做過哪些嘗試
- 需要我決定什麼
- 若不處理，風險是什麼

## 禁止事項

- 不得直接修改舊系統 `D:\rental` 當作正式方案
- 不得跳過工作記錄
- 不得把推測當成規格
- 不得在未記錄的情況下更改跨模組契約
