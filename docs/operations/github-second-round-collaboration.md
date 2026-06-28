# GitHub 第二輪協作規範

Last Updated: 2026-06-28

## Purpose

這份文件定義第二輪 agent 與多人協作在 GitHub 上的執行方式，避免不同電腦上的工作夥伴同時改到高衝突區。

## Collaboration Principle

- 第二輪不是所有人同時亂改，而是依任務邊界並行
- 一輪只允許一個 owner 改高衝突核心
- 其餘 agent 優先做模組內閉環工作
- 所有改動都必須能從 branch、PR、工作紀錄回溯

## Recommended Second-Round Split

### `reasonix`

- 做規格審查、decision review、風險清單
- 不直接大改主幹
- 輸出 review note 或 comment-ready 文件

### `open`

- 做 `landlords`、`payments`、或其他 route-heavy 模組
- 以可運行最小骨架為目標
- 提交前要列出已實作路由與未做項目

### `mimo`

- 做 UI 欄位對齊、template 修正、回歸證據整理
- 不自行發明後端規則
- 若發現欄位與契約不一致，先提 incident

### `box`

- 做 smoke tests、runbook、seed/check/fix 類低風險支援腳本
- 不主導資料契約或主幹狀態機

### `Codex`

- 維護主幹整合
- 控制 `app/models`、`app/services`、`data_contracts` 這些高衝突區的合併順序

## Files Each Agent Should Own

- `reasonix`: `docs/reports/reasonix-*`, `coordination/progress/reasonix.md`, `coordination/completed/reasonix.md`
- `open`: 自己負責模組下的 `app/modules/<module>/`, `app/templates/<module>/`, `coordination/progress/open.md`
- `mimo`: `docs/reports/mimo-*`, template 小修正, `coordination/progress/mimo.md`
- `box`: `tests/`, `scripts/`, `docs/operations/`, `coordination/progress/box.md`

## Merge Safety Rules

- 不同 agent 不要同時改同一支 model 檔
- 不同 agent 不要同時改同一支 service 檔
- `coordination/progress/*.md` 各自只改自己的檔案
- 若 PR 涉及資料欄位、status enum、year_month、付款狀態機，必須先對齊 Phase 0 決議

## Required Evidence In Every PR

- 改了哪些檔案
- 依據哪份規格文件
- 驗證方式
- 剩餘風險
- 是否需要下一個 agent 接手

## Immediate Incident Cases

以下狀況不能直接 merge：

- 發現舊系統行為與凍結契約矛盾
- 新程式需要新增欄位但契約未定義
- PaymentRecord 流程與死碼 `/payment/*` 混用
- Room status 又被拉回虛擬 tenant 名稱表示
