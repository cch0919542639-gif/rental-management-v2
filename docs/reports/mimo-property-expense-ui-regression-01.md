# PropertyExpense UI Regression — /expenses/ & /expenses/create

- **Agent**: mimo
- **Branch**: `agent/mimo-property-expense-ui-regression-01`
- **Base**: `codex-phase2-mainline-01`
- **Date**: 2026-07-17
- **Type**: UI regression report (read-only — no templates/models/services modified)

---

## 1. Scope

驗收 PropertyExpense 模組前端：清單頁 `/expenses/`、建立頁 `/expenses/create`、
以及從清單觸發的編輯、入帳、作廢、刪除操作。

## 2. 驗收結果摘要

| 項目 | 狀態 | 說明 |
|------|------|------|
| 清單頁載入 | PASS | `/expenses/` 正常渲染表格與篩選器 |
| 空狀態顯示 | PASS | 無資料時顯示「尚無支出記錄」 |
| 建立頁載入 | PASS | `/expenses/create` 渲染表單 |
| draft 編輯 | PASS | 編輯按鈕僅 draft 可見，表單正確預填 |
| 入帳操作 | PASS | draft → posted，flash「支出已入帳」 |
| 作廢操作 | PASS | posted → voided，需填作廢原因 |
| draft 刪除 | PASS | 僅 draft 顯示刪除按鈕 |
| posted/voided 按鈕 | PASS | posted 僅顯示「作廢」；voided 無操作按鈕 |
| 物件篩選 | PASS | `?property_id=N` 正確篩選 |
| 狀態篩選 | PASS | `?status=draft` 等正確篩選 |
| 分類篩選 | PASS | `?category=repair` 等正確篩選 |
| 整數金額 | PASS | `money_int` filter 正確顯示無小數 |
| 憑證編號 | PASS | 清單顯示 `reference_no`，空值顯示 `-` |
| 導覽入口 | PASS | base.html nav 有「支出」連結 |
| CSV/XLSX 連結 | PASS | 清單頁有 CSV/XLSX 匯出連結 |
| CSV 匯出結果 | PASS | `/expenses/export?format=csv` 返回正確欄位 |
| XLSX 匯出結果 | PASS | `/expenses/export?format=xlsx` 返回正確欄位 |

## 3. 問題清單

### P1 — 必須修正

| # | 頁面 | 問題 | 詳情 |
|---|------|------|------|
| BUG-01 | form.html | 分類下拉顯示英文 raw value | `category` choices 用 `(x, x)`，UI 顯示 `management_fee` 而非中文。應改為 `(x, 中文名)` |
| BUG-02 | list.html | 分類欄位顯示英文 raw value | 清單表格 `{{ item.category }}` 直接輸出英文，應做 mapping 顯示中文 |
| BUG-03 | list.html | 狀態下拉顯示英文 raw value | 狀態篩選 dropdown 顯示 `draft/posted/voided/cancelled`，應顯示中文 |
| BUG-04 | list.html | 狀態欄位顯示英文 raw value | 清單表格 `{{ item.record_status }}` 直接輸出英文 |

### P2 — 建議修正

| # | 頁面 | 問題 | 詳情 |
|---|------|------|------|
| BUG-05 | base.html | 缺少 `.flash-success` 樣式 | 僅定義 `.flash-danger`，成功 flash 訊息無綠色背景 |
| BUG-06 | form.html | 金額欄位允許小數輸入 | `DecimalField(places=2)` 允許輸入 `1200.50`，但規格要求整數金額。應改為 `IntegerField` 或限制 `places=0` |
| BUG-07 | list.html | 清單表格無 `min-width` | 無橫向捲動容器，手機窄屏表格溢出 |
| BUG-08 | list.html | 無手機欄位隱藏 | 缺少 `@media (max-width: 720px)` 隱藏次要欄位（如憑證編號） |
| BUG-09 | list.html | `posted_total` 未依篩選計算 | 篩選特定物件時，合計仍顯示全部物件的 posted 總額，未隨 `property_id` 篩選 |
| BUG-10 | list.html | 表頭未固定 | 缺少 `position: sticky; top: 0`，長列表捲動時表頭消失 |

### P3 — 低優先級

| # | 頁面 | 問題 | 詳情 |
|---|------|------|------|
| BUG-11 | form.html | 作廢原因欄位不在表單中 | 作廢操作用 `<form>` POST 到 `/void`，但無獨立原因輸入欄位。需在清單頁提供 input 或 modal |
| BUG-12 | list.html | 刪除按鈕無確認對話框 | `<button>刪除</button>` 無 `onclick="return confirm()"`，使用者可能誤刪 |

## 4. 手機寬度驗證

| 檢查項 | 結果 | 說明 |
|--------|------|------|
| 導覽列在 ≤720px | FAIL | `<nav>` 無 `flex-wrap` 或漢堡選單，連結水平溢出 |
| 表格在 ≤720px | FAIL | 無 `min-width` + 捲動容器，表格直接溢出 viewport |
| 篩選器在 ≤720px | PASS | `<select>` 預設 width: auto，可正常使用 |
| 建立表單在 ≤720px | PASS | `max-width: 720px` 已設定，垂直排列 |

## 5. CSV/XLSX 匯出驗證

| 檢查項 | 結果 | 說明 |
|--------|------|------|
| CSV 下載連結 | PASS | `<a href="...format=csv">CSV</a>` |
| XLSX 下載連結 | PASS | `<a href="...format=xlsx">XLSX</a>` |
| CSV 內容欄位 | PASS | transaction_date, property_name, category, amount, payee, reference_no, record_status |
| CSV 僅含 posted | PASS | `list_filtered(status="posted")` |
| 匯出路由無資料時 | PASS | headers fallback 為固定欄位列表 |

## 6. 狀態操作驗證

| 狀態 | 可見按鈕 | 預期 | 結果 |
|------|----------|------|------|
| draft | 編輯、入帳、刪除 | 編輯 ✓、入帳 ✓、作廢 ✗、刪除 ✓ | PASS |
| posted | 作廢 | 編輯 ✗、入帳 ✗、作廢 ✓、刪除 ✗ | PASS |
| voided | （無） | 編輯 ✗、入帳 ✗、作廢 ✗、刪除 ✗ | PASS |
| cancelled | （無） | 編輯 ✗、入帳 ✗、作廢 ✗、刪除 ✗ | PASS |

## 7. Blockers

**無 P0 blockers。** P1 issues（BUG-01 ~ BUG-04）為中文本地化問題，不影響功能但影響使用者體驗。
P2 issues 為 UX 改善建議。

## 8. 不修改範圍

本報告為唯讀驗收，未修改任何模板、模型、service、路由、資料庫。

## 9. 交付

- 交付本報告 `docs/reports/mimo-property-expense-ui-regression-01.md`
- 更新 `coordination/progress/mimo.md` 與 `coordination/completed/mimo.md`
