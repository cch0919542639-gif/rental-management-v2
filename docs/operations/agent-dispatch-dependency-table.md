# 四個 Agent 的派工順序與交付依賴表

本表用來控制 `reasonix`、`open`、`mimo`、`box` 的進場順序、依賴關係與可交接節點，避免平行作業時互相覆蓋結論。

## 總原則

- 先定義規格，再做盤點，再做驗證，再做補件
- 核心契約未凍結前，不讓下游 agent 自行決定資料語義
- `box` 只接封閉小任務，不參與核心架構決策

## 派工順序總表

| 順序 | Agent | 主要任務 | 開工前必讀 | 必要前置依賴 | 主要交付物 | 完成後交給誰 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | reasonix | 架構決策、資料契約、切分邊界 | `rewrite-roadmap.md`, `target-structure.md`, `agent-work-rules.md` | 無 | 架構決策書、資料契約稽核、依賴圖 | open, mimo, box |
| 2 | open | 舊系統盤點、route/template/schema 清單、模組映射 | 同上 + `reasonix` 初版結論 | `reasonix` 至少完成初版契約方向 | route/template matrix、schema inventory、cleanup candidates、module mapping | mimo, box, Codex |
| 3 | mimo | UI 欄位對照、測試情境、回歸檢查表 | 同上 + reporting contract + `reasonix/open` 交付 | `reasonix` 契約、`open` 路由與 schema 盤點 | UI field matrix、test scenarios、regression checklist | Codex, 後續工程 agent |
| 4 | box | 封閉型小任務、腳本索引、README 樣板、局部補件 | 同上 + `reasonix/open` 交付 | 任務必須已被上游切割清楚 | script index、small fix notes、module readme templates | Codex |

## 分階段派工

### Stage A: 規格凍結前

只派：

- `reasonix`

理由：

- 這個階段的核心是回答「新版到底怎麼拆、資料格式怎麼定、哪些舊規則不能留」。
- 如果先讓 `open` 或 `mimo` 大量展開，容易建立在錯誤契約上。

### Stage B: 初版規格已出

派：

- `open`

條件：

- `reasonix` 已經至少交出：
  - `reasonix-architecture-decision.md`
  - `reasonix-data-contract-audit.md`
  - `reasonix-dependency-map.md`

理由：

- `open` 的工作是把舊案全面清點，但它不應自己發明資料規則。

### Stage C: 盤點結果已出

派：

- `mimo`

條件：

- `reasonix` 已凍結主要資料語義
- `open` 已經指出 route/template/schema 對應與高風險區

理由：

- `mimo` 要建立 UI 欄位對照與驗證情境，必須知道欄位真實來源。

### Stage D: 補件與封閉任務

派：

- `box`

條件：

- 任務已被切成單點可驗收工作
- 不需要 `box` 自己做跨模組判斷

理由：

- `box` 額度有限，應用在整理、樣板、小修、索引最划算。

## 交付依賴表

### reasonix -> open

`open` 開工前至少要讀：

- `docs/reports/reasonix-architecture-decision.md`
- `docs/reports/reasonix-data-contract-audit.md`
- `docs/reports/reasonix-dependency-map.md`
- `data_contracts/`

`reasonix` 必須先回答：

- `year_month` 正式格式是什麼
- `user/users` 如何處理
- 付款流程保留哪一條主路徑
- 空房/待修是否還能留在 tenant 名稱邏輯

### open -> mimo

`mimo` 開工前至少要讀：

- `docs/reports/open-route-template-matrix.md`
- `docs/reports/open-schema-inventory.md`
- `docs/reports/open-cleanup-candidates.md`
- `docs/reports/open-module-mapping.md`

`open` 必須先交代：

- 每個頁面 route 對應哪個 template
- 每個報表和列表主要資料來源
- 哪些欄位是高風險或來源不唯一

### reasonix/open -> box

`box` 開工前至少要讀：

- `docs/reports/reasonix-architecture-decision.md`
- `docs/reports/open-cleanup-candidates.md`
- 指派給它的明確 task 說明

`box` 只在以下條件下進場：

- 任務範圍只有 1 到 3 個封閉輸出
- 不需要再做架構判斷
- 不需要變動核心資料契約

## 建議交辦格式

### 給 reasonix

目標：

- 先完成架構決策與資料契約凍結

要填的檔案：

- `docs/reports/reasonix-architecture-decision.md`
- `docs/reports/reasonix-data-contract-audit.md`
- `docs/reports/reasonix-dependency-map.md`

### 給 open

目標：

- 根據 `reasonix` 結論，完成舊系統盤點與重寫映射

要填的檔案：

- `docs/reports/open-route-template-matrix.md`
- `docs/reports/open-schema-inventory.md`
- `docs/reports/open-cleanup-candidates.md`
- `docs/reports/open-module-mapping.md`

### 給 mimo

目標：

- 根據契約與盤點結果，完成 UI 欄位與驗證情境

要填的檔案：

- `docs/reports/mimo-ui-field-matrix.md`
- `docs/reports/mimo-test-scenarios.md`
- `evidence/mimo-regression-checklist.md`

### 給 box

目標：

- 做封閉型整理與小修補件

要填的檔案：

- `docs/reports/box-script-index.md`
- `docs/reports/box-module-readme-templates.md`
- `evidence/box-small-fix-notes.md`

## 阻塞條件表

| Agent | 應停止並回報的情況 | 回報方式 |
| --- | --- | --- |
| reasonix | 無法唯一決定資料契約、發現核心流程互相衝突 | incident + progress 改 `NEEDS-DECISION` |
| open | 發現舊系統實際結構與 `reasonix` 契約衝突 | incident + progress 改 `BLOCKED` |
| mimo | 欄位來源不唯一、同頁面有多套資料語義 | incident + progress 改 `BLOCKED` |
| box | 任務已超出小修補件邊界、需要跨模組決策 | incident + progress 改 `BLOCKED` |

## 最推薦的實際派工順序

1. 先派 `reasonix`，只做規格與決策，不碰大量修補。
2. `reasonix` 交出初版後，派 `open` 做系統盤點與新舊映射。
3. `open` 完成主要盤點後，派 `mimo` 補 UI 驗證與測試情境。
4. 最後才派 `box`，把上面切好的小任務收尾。

## Codex 接手點

當以下任一條件成立時，由我接手整合：

- `reasonix` 已凍結核心契約
- `open` 已完成模組映射
- `mimo` 已完成回歸場景
- `box` 已完成腳本/模板補件

之後可進入下一階段：

- 建立可執行新版程式骨架
- 開始將 `app/modules` 逐步實作
