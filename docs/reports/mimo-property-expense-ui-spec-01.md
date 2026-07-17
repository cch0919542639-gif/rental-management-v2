# PropertyExpense UI / Regression Spec

- **Agent**: mimo
- **Branch**: `agent/mimo-property-expense-ui-spec-01`
- **Base**: `codex-phase2-mainline-01`
- **Date**: 2026-07-17
- **Type**: UI 規格 + 回歸驗收情境（不含 app 程式碼）

---

## 1. 模組定位

PropertyExpense 管理物件層級支出（非房客帳單），涵蓋修繕、保養、保險、稅金、管理費等。
與 MonthlyBill（房客應收）互補，完整呈現物件營運成本。

## 2. 狀態機

```
draft ──入帳──▶ posted
draft ──刪除──▶ (移除)
posted ──作廢──▶ voided
```

- **draft**：可編輯、可入帳、可刪除
- **posted**：唯讀，僅可作廢
- **voided**：唯讀，不可任何操作

## 3. 畫面規格

### 3.1 清單頁 `/property-expenses/`

| 欄位 | 桌面 | 手機 | 中文文案 | 格式 |
|------|------|------|----------|------|
| ID | ✓ | ✗ | ID | 整數 |
| 物件名稱 | ✓ | ✓ | 物件 | — |
| 房東 | ✓ | ✗ | 房東 | — |
| 日期 | ✓ | ✓ | 日期 | YYYY-MM-DD |
| 分類 | ✓ | ✓ | 分類 | 下拉選項 |
| 摘要 | ✓ | ✗ | 摘要 | 最多 200 字 |
| 金額 | ✓ | ✓ | 金額 | 整數（無小數） |
| 憑證編號 | ✓ | ✗ | 憑證編號 | — |
| 狀態 | ✓ | ✓ | 狀態 | draft/posted/voided |
| 備註 | ✓ | ✗ | 備註 | — |
| 操作 | ✓ | ✓ | 操作 | 按鈕群 |

**分類選項**：修繕、保養、保險、稅金、管理費、水電費、仲介費、其他

**固定表頭**：`position: sticky; top: 0; z-index: 1;`

**整數金額**：所有金額欄位使用 `money_int` filter，無小數點。

**手機欄位隱藏**：≤720px 隱藏 ID、房東、摘要、憑證編號、備註，保留物件、日期、分類、金額、狀態、操作。

**空狀態**：「尚無物件支出記錄」

**篩選**：物件（下拉）、分類（下拉）、狀態（下拉）、日期範圍（起迄）

**彙總卡片**：筆數、draft 合計金額、posted 合計金額、voided 合計金額

### 3.2 建立頁 `/property-expenses/create`

| 欄位 | 表單控件 | 中文文案 | 必填 | 驗證 |
|------|----------|----------|------|------|
| property_id | SelectField | 物件 | ✓ | DataRequired |
| expense_date | DateField | 日期 | ✓ | DataRequired |
| category | SelectField | 分類 | ✓ | DataRequired |
| amount | IntegerField | 金額 | ✓ | DataRequired, NumberRange(min=1) |
| description | StringField | 摘要 | ✗ | Optional, max=200 |
| receipt_number | StringField | 憑證編號 | ✗ | Optional, max=100 |
| notes | TextAreaField | 備註 | ✗ | Optional |
| submit | SubmitField | 儲存 | — | — |

**預設狀態**：draft

**表單標題**：「新增物件支出」

**表單佈局**：`max-width: 760px`，垂直排列（沿用 maintenance/form.html 模式）。

### 3.3 編輯頁 `/property-expenses/<id>/edit`

與建立頁相同欄位 + 表單標題「編輯物件支出」。
僅 `status=draft` 可進入編輯頁；其他狀態重導向清單頁並 flash「僅 draft 狀態可編輯」。

### 3.4 入帳（POST） `/property-expenses/<id>/post`

- 方法：POST
- 僅 `status=draft` 可執行
- 動作：`status → posted`
- flash：「已入帳」
- 重導向：清單頁

### 3.5 作廢（POST） `/property-expenses/<id>/void`

- 方法：POST
- 僅 `status=posted` 可執行
- 動作：`status → voided`
- flash：「已作廢」
- 重導向：清單頁

### 3.6 刪除 draft（POST） `/property-expenses/<id>/delete`

- 方法：POST
- 僅 `status=draft` 可執行
- 動作：刪除記錄
- flash：「已刪除」
- 重導向：清單頁

## 4. 各狀態按鈕與操作

| 狀態 | 編輯 | 入帳 | 作廢 | 刪除 |
|------|------|------|------|------|
| draft | ✓ | ✓ | ✗ | ✓ |
| posted | ✗ | ✗ | ✓ | ✗ |
| voided | ✗ | ✗ | ✗ | ✗ |

**按鈕文案**：

| 操作 | 按鈕文字 | 觸發方式 |
|------|----------|----------|
| 編輯 | 編輯 | `<a href>` 連結 |
| 入帳 | 入帳 | `<form method="post">` + `<button>` |
| 作廢 | 作廢 | `<form method="post">` + `<button>` |
| 刪除 | 刪除 | `<form method="post">` + `<button>` + onclick 確認 |

## 5. 桌面 / 手機保留欄位

### 清單頁

| 欄位 | 桌面 (≥721px) | 手機 (≤720px) |
|------|---------------|---------------|
| ID | ✓ | ✗ |
| 物件 | ✓ | ✓ |
| 房東 | ✓ | ✗ |
| 日期 | ✓ | ✓ |
| 分類 | ✓ | ✓ |
| 摘要 | ✓ | ✗ |
| 金額 | ✓ | ✓ |
| 憑證編號 | ✓ | ✗ |
| 狀態 | ✓ | ✓ |
| 備註 | ✓ | ✗ |
| 操作 | ✓ | ✓ |

### 桌面規格

- `min-width: 1100px`（清單頁 `<table>`）
- 固定表頭：`position: sticky; top: 0; z-index: 1; box-shadow: 0 1px 0 #cbd5e1;`
- 整數金額：`money_int` filter（無小數）

### 手機規格

- ≤720px：`th, td { padding: 6px 8px; font-size: 0.82rem; }`
- 捲軸容器：`max-height: calc(100vh - 320px); overflow: auto;`

## 6. 憑證編號顯示

- 清單頁：隱藏欄位（手機不顯示），桌面顯示為純文字
- 編輯/建立表單：`<input type="text">`，placeholder「選填」
- 空值顯示：`-`

## 7. 驗收情境（25 項）

| ID | 情境 | 前置條件 | 步驟 | 預期結果 | 優先級 |
|----|------|----------|------|----------|--------|
| AC-01 | 建立 draft 記錄 | 已登入，物件存在 | 1. 開啟 /property-expenses/create 2. 選擇物件、輸入日期/分類/金額 3. 儲存 | 建立成功，狀態為 draft，flash「已建立」，重導向清單頁 | P0 |
| AC-02 | 建立必填欄位驗證 | 已登入 | 1. 開啟建立頁 2. 不填任何欄位 3. 儲存 | 表單驗證失敗，物件/日期/分類/金額顯示必填錯誤 | P0 |
| AC-03 | 金額不可為零或負數 | 已登入 | 1. 開啟建立頁 2. 輸入金額 0 或 -100 3. 儲存 | 表單驗證失敗，金額須為正整數 | P0 |
| AC-04 | 編輯 draft 記錄 | 存在 status=draft 的記錄 | 1. 在清單頁點擊「編輯」 2. 修改金額 3. 儲存 | 更新成功，金額變更，flash「已更新」 | P0 |
| AC-05 | 編輯 posted 記錄被拒 | 存在 status=posted 的記錄 | 1. 嘗試透過 URL 進入 /property-expenses/<id>/edit | 重導向清單頁，flash「僅 draft 狀態可編輯」 | P0 |
| AC-06 | 入帳 draft → posted | 存在 status=draft 的記錄 | 1. 在清單頁點擊「入帳」 2. 確認 | 狀態變為 posted，flash「已入帳」 | P0 |
| AC-07 | 入帳按鈕僅 draft 顯示 | 清單頁有 draft 和 posted 記錄 | 1. 查看清單頁 | draft 行顯示「入帳」按鈕；posted 行不顯示「入帳」按鈕 | P0 |
| AC-08 | 作廢 posted → voided | 存在 status=posted 的記錄 | 1. 在清單頁點擊「作廢」 2. 確認 | 狀態變為 voided，flash「已作廢」 | P0 |
| AC-09 | 作廢按鈕僅 posted 顯示 | 清單頁有三種狀態記錄 | 1. 查看清單頁 | draft 行無「作廢」；posted 行有「作廢」；voided 行無「作廢」 | P0 |
| AC-10 | 刪除 draft 記錄 | 存在 status=draft 的記錄 | 1. 在清單頁點擊「刪除」 2. 確認 | 記錄移除，flash「已刪除」 | P0 |
| AC-11 | 刪除按鈕僅 draft 顯示 | 清單頁有 draft 和 posted 記錄 | 1. 查看清單頁 | draft 行顯示「刪除」；posted/voided 行不顯示「刪除」 | P0 |
| AC-12 | voided 不可任何操作 | 存在 status=voided 的記錄 | 1. 查看清單頁該行 | 無任何操作按鈕（無編輯、入帳、作廢、刪除） | P0 |
| AC-13 | 狀態中文顯示 | 三種狀態記錄皆存在 | 1. 查看清單頁狀態欄 | draft→「草稿」、posted→「已入帳」、voided→「已作廢」 | P0 |
| AC-14 | 金額整數格式 | 金額=12345 的記錄存在 | 1. 查看清單頁金額欄 | 顯示「12345」，無小數點、無千分位符號 | P0 |
| AC-15 | 憑證編號顯示 | receipt_number="INV-001" 的記錄存在 | 1. 桌面查看清單頁 | 憑證編號欄顯示「INV-001」 | P1 |
| AC-16 | 憑證編號手機隱藏 | 同上 | 1. 手機（≤720px）查看清單頁 | 憑證編號欄隱藏 | P1 |
| AC-17 | 手機欄位隱藏 | 記錄存在 | 1. 以 ≤720px 視口查看清單頁 | ID、房東、摘要、憑證編號、備註隱藏；物件、日期、分類、金額、狀態、操作可見 | P0 |
| AC-18 | 桌面固定表頭 | 記錄 ≥20 筆 | 1. 桌面查看清單頁 2. 向下捲動 | 表頭固定在視口頂端，不隨捲動消失 | P0 |
| AC-19 | 篩選 — 依物件 | 多筆不同物件記錄存在 | 1. 在清單頁選擇特定物件 2. 送出 | 僅顯示該物件的支出記錄 | P0 |
| AC-20 | 篩選 — 依分類 | 多筆不同分類記錄存在 | 1. 選擇「修繕」分類 2. 送出 | 僅顯示分類為修繕的記錄 | P1 |
| AC-21 | 篩選 — 依狀態 | 三種狀態記錄存在 | 1. 選擇「draft」狀態 2. 送出 | 僅顯示 draft 記錄 | P1 |
| AC-22 | 篩選清除 | 已套用篩選 | 1. 點擊「清除篩選」連結 | 恢復顯示全部記錄 | P1 |
| AC-23 | 彙總卡片 | 多筆記錄存在 | 1. 查看清單頁上方彙總 | 筆數、draft/posted/voided 合計金額正確 | P0 |
| AC-24 | 空狀態顯示 | 無任何記錄 | 1. 開啟清單頁 | 顯示「尚無物件支出記錄」 | P0 |
| AC-25 | 未登入存取 | 未登入狀態 | 1. 開啟 /property-expenses/ | 重導向至登入頁 | P0 |

## 8. 不修改範圍

- app 程式碼（routes, models, services, repositories）
- 模板（HTML files）
- 資料庫 migration
- CSV/XLSX 匯出

本文件為純規格交付，供 Codex 實作時對齊。
