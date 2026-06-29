# 給 mimo 的派工指令

你現在負責 **Phase 2 UI Regression 新一輪驗證**。  
這次重點是已進主幹的新流程，尤其是 `electricity property workflows`。你可以修 template / 顯示層，但不要改 service 規則或資料契約。

## 你的目標

驗證目前主幹以下頁面與流程是否可正常操作、顯示一致、中文文案完整、空資料狀態可接受：

- `billing`
- `payments`
- `maintenance`
- `electricity/property detail`
- `electricity/property/<id>/new-bill`
- `electricity/property/<id>/quick-reading`
- `electricity/property/<id>/reading-log`

## 先讀

- `D:\CodexRuntime\rental\rebuild\coordination\progress\codex.md`
- `D:\CodexRuntime\rental\rebuild\docs\operations\phase2-parallel-dispatch-index-2026-06-29.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-phase2-ui-regression-04.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-ui-polish-02.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-phase2-contract-notes-01.md`

## 直接交付

請直接建立並填寫：

- `D:\CodexRuntime\rental\rebuild\docs\reports\mimo-phase2-ui-regression-05.md`

若有低風險 UI 修正，可直接修改 template，但僅限：

- `app/templates/*`
- 必要時表單 choices 顯示文字

## 必查項目

至少檢查：

1. 中文標題 / 中文按鈕 / 中文狀態文字
2. property / room 顯示是否優先用名稱而不是裸 ID
3. 空列表 / 無資料頁是否可讀
4. flash message 是否合理
5. `year_month` 畫面顯示是否仍為 `YYYY-MM`
6. `electricity property detail` 三個快捷入口是否清楚
7. `reading-log` 欄位是否足夠辨識 bill / meter / room / usage / amount

## 明確限制

- 不要改 model
- 不要改 repository/service 核心邏輯
- 不要自己定義新欄位
- 不要自行新增新資料契約

## 驗收標準

你的報告至少要包含：

- 已驗證頁面清單
- 發現問題分級
- 已直接修正項目
- 仍需 Codex 處理的 blocker
- 驗證後的測試結果或操作結果摘要

## 工作紀錄要求

- 開工前更新 `D:\CodexRuntime\rental\rebuild\coordination\progress\mimo.md`
- 完成後更新 `D:\CodexRuntime\rental\rebuild\coordination\completed\mimo.md`

## 如果卡住

只要遇到以下情況就回報：

- 畫面缺欄位但來源不清楚
- 需要後端 service 才能修
- 同頁面有雙語義或顯示規則不一致

回報方式：

- 新增 `D:\CodexRuntime\rental\rebuild\coordination\incidents\<timestamp>_mimo_<topic>.md`
- 把 `progress/mimo.md` 狀態改成 `BLOCKED`

