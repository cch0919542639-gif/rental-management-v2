# Reporting Mobile Fix — UI Regression Evidence

- **Agent**: mimo
- **Branch**: `agent/mimo-reporting-mobile-fix-01`
- **Base**: `codex-phase2-mainline-01` (latest HEAD)
- **Date**: 2026-07-17
- **Type**: P1 mobile responsiveness fix (body + footer)

---

## 1. Problem Statement

At ≤720px viewport width, report tables had two issues:
1. All columns visible — 18-column collection required 4.6x horizontal scroll
2. `tfoot` used `colspan`, so `nth-child()` misaligned footer cells with body columns

## 2. Changes Made

### 2.1 CSS: `_report_table_style.html`

Added `@media (max-width: 720px)` rules:

| Rule | Effect |
|------|--------|
| `th, td { padding: 6px 8px; font-size: 0.82rem }` | Compact sticky header |
| `select[multiple] { min-width: 0; width: 100% }` | Filter dropdown fills mobile width |
| `.hide-mobile { display: none }` | Utility class for footer cell hiding |
| `[data-table="collection"] nth-child(2,6-15)` | Hides 11 body columns |
| `[data-table="settlement"] nth-child(1,4-9)` | Hides 7 body columns |
| `[data-table="new-tenants"] nth-child(4,7,9,10,12)` | Hides 5 body columns |
| `[data-table="yearly"] nth-child(4-9)` | Hides 6 body columns |
| `.tfoot-desktop { display: none }` | Hides desktop footer row on mobile |
| `.tfoot-mobile { display: table-row }` | Shows mobile footer row on mobile |
| `.tfoot-mobile th:not(.show-mobile) { display: none }` | Hides non-show-mobile cells in mobile footer |

Added `@media (min-width: 721px)`:
- `.tfoot-mobile { display: none }` — hides mobile footer on desktop

### 2.2 Templates: `data-table` Attributes

Added `data-table="<name>"` to `<table>` for CSS targeting:
- `collection.html`: `data-table="collection"`
- `property_settlement.html`: `data-table="settlement"`
- `new_tenants.html`: `data-table="new-tenants"`
- `property_yearly.html`: `data-table="yearly"`

### 2.3 Templates: Mobile Footer Rows

Added `.tfoot-desktop` / `.tfoot-mobile` rows to `<tfoot>` in 3 templates:

| Table | Mobile footer columns |
|-------|----------------------|
| collection | 合計 / 應收總額 / 已繳 / 未收 |
| settlement | 合計 / 帳單數 / 應收總額 / 已繳 / 未收 |
| yearly | 全年合計 / 帳單數 / 應收總額 / 已繳 / 未收 |

## 3. Mobile Column Visibility

### Collection (18 → 7 columns)

| # | Column | Desktop | Mobile |
|---|--------|---------|--------|
| 1 | 月份 | ✓ | ✓ |
| 2 | 房東 | ✓ | ✗ |
| 3 | 物件 | ✓ | ✓ |
| 4 | 房號 | ✓ | ✓ |
| 5 | 房客 | ✓ | ✓ |
| 6 | 電話 | ✓ | ✗ |
| 7 | 起租 | ✓ | ✗ |
| 8 | 到約 | ✓ | ✗ |
| 9 | 租金 | ✓ | ✗ |
| 10 | 電費 | ✓ | ✗ |
| 11 | 公設電費 | ✓ | ✗ |
| 12 | 水費 | ✓ | ✗ |
| 13 | 其他 | ✓ | ✗ |
| 14 | 其他說明 | ✓ | ✗ |
| 15 | 前期未收 | ✓ | ✗ |
| 16 | 應收總額 | ✓ | ✓ |
| 17 | 已繳 | ✓ | ✓ |
| 18 | 未收 | ✓ | ✓ |

### Settlement (12 → 5 columns)

| # | Column | Desktop | Mobile |
|---|--------|---------|--------|
| 1 | 房東 | ✓ | ✗ |
| 2 | 物件 | ✓ | ✓ |
| 3 | 帳單數 | ✓ | ✓ |
| 4–9 | 租金..前期未收 | ✓ | ✗ |
| 10 | 應收總額 | ✓ | ✓ |
| 11 | 已繳 | ✓ | ✓ |
| 12 | 未收 | ✓ | ✓ |

### New Tenants (12 → 7 columns)

| # | Column | Desktop | Mobile |
|---|--------|---------|--------|
| 1 | 物件 | ✓ | ✓ |
| 2 | 房號 | ✓ | ✓ |
| 3 | 房客 | ✓ | ✓ |
| 4 | 電話 | ✓ | ✗ |
| 5 | 起租日 | ✓ | ✓ |
| 6 | 到期日 | ✓ | ✓ |
| 7 | 押金 | ✓ | ✗ |
| 8 | 租金 | ✓ | ✓ |
| 9 | 起始電表 | ✓ | ✗ |
| 10 | 起始水表 | ✓ | ✗ |
| 11 | 合約狀態 | ✓ | ✓ |
| 12 | 備註 | ✓ | ✗ |

### Yearly (12 → 6 columns)

| # | Column | Desktop | Mobile |
|---|--------|---------|--------|
| 1 | 月份 | ✓ | ✓ |
| 2 | 物件 | ✓ | ✓ |
| 3 | 帳單數 | ✓ | ✓ |
| 4–9 | 租金..前期未收 | ✓ | ✗ |
| 10 | 應收總額 | ✓ | ✓ |
| 11 | 已繳 | ✓ | ✓ |
| 12 | 未收 | ✓ | ✓ |

## 4. Desktop / Export Integrity

- Desktop layout: **unchanged** — no CSS rules apply above 720px
- CSV/XLSX export: **unchanged** — routes, headers, `export_money_rows` not modified
- Data model / service / database: **not modified**

## 5. Test Results

```
py -3 -m pytest tests\integration -q
117 passed, 11 failed (pre-existing cp950), 15 skipped

py -3 -m pytest tests\integration\test_reporting_expansion.py -q
5 passed
```

Baseline maintained. 11 failures are pre-existing Windows cp950 encoding issue in `test_backfill_missing_monthly_bills.py`.

## 6. Modified Files

| File | Change |
|------|--------|
| `app/templates/reports/_report_table_style.html` | Added responsive CSS rules + tfoot-desktop/mobile |
| `app/templates/reports/collection.html` | Added `data-table="collection"`, tfoot-mobile row |
| `app/templates/reports/property_settlement.html` | Added `data-table="settlement"`, tfoot-mobile row |
| `app/templates/reports/new_tenants.html` | Added `data-table="new-tenants"` |
| `app/templates/reports/property_yearly.html` | Added `data-table="yearly"`, tfoot-mobile row |
