# Reporting Expansion UI Regression — Read-Only Acceptance

- **Agent**: mimo
- **Branch**: `agent/mimo-reporting-expansion-ui-regression-01`
- **Base**: `codex-phase2-mainline-01`
- **Date**: 2026-07-15
- **Scope**: Read-only template / code review of 4 new report pages
- **Mode**: Static analysis — no server started, no browser rendering

---

## 1. Pages Under Test

| Page | Route | Template | Form |
|------|-------|----------|------|
| 物件收租明細 | `/reports/collection` | `reports/collection.html` | `PropertyReportMonthForm` |
| 物件收款彙總 | `/reports/property-settlement` | `reports/property_settlement.html` | `PropertyReportMonthForm` |
| 新增房客明細 | `/reports/new-tenants` | `reports/new_tenants.html` | `PropertyReportMonthForm` |
| 物件年度月別統計 | `/reports/property-yearly` | `reports/property_yearly.html` | `PropertyReportYearForm` |

---

## 2. Verification Matrix

### 2.1 篩選與多物件選擇

| Check | Collection | Settlement | New Tenants | Yearly | Verdict |
|-------|-----------|------------|-------------|--------|---------|
| Month/Year filter field | `year_month` StringField | `year_month` StringField | `year_month` StringField | `year` IntegerField | PASS |
| Multi-property SelectMultipleField | `property_ids(size=6)` | `property_ids(size=6)` | `property_ids(size=6)` | `property_ids(size=6)` | PASS |
| Form submit button | "查詢" | "查詢" | "查詢" | "查詢" | PASS |
| GET fallback populates form defaults | `form.year_month.data = year_month` | same | same | `form.year.data = year` | PASS |
| `_selected_property_ids` fallback → all visible | line 39: `requested_ids or list(visible_ids)` | same | same | same | PASS |
| 403 on out-of-scope property_id | line 40–41 | same | same | same | PASS |

### 2.2 空資料狀態

| Page | Empty State Text | Colspan | Verdict |
|------|-----------------|---------|---------|
| Collection | "符合條件的收租資料尚無資料" | colspan="18" (matches 18 cols) | PASS (wording P2) |
| Settlement | "符合條件的物件彙總尚無資料" | colspan="12" (matches 12 cols) | PASS |
| New Tenants | "符合條件的新增房客尚無資料" | colspan="12" (matches 12 cols) | PASS |
| Yearly | "符合條件的年度物件統計尚無資料" | colspan="12" (matches 12 cols) | PASS |

### 2.3 寬表橫向捲動

| Check | Detail | Verdict |
|-------|--------|---------|
| `div.report-table-scroll` wrapper | All 4 templates wrap `<table>` in `<div class="report-table-scroll">` | PASS |
| `overflow: auto` on scroll container | `_report_table_style.html` line 6 | PASS |
| `min-width` on `<table>` | Collection: 1740px, Settlement: 1510px, New Tenants: 1280px, Yearly: 1430px | PASS |
| Horizontal scroll activates when viewport < min-width | CSS `overflow: auto` + `min-width` combination | PASS |

### 2.4 固定表頭

| Check | Detail | Verdict |
|-------|--------|---------|
| `position: sticky; top: 0` on `<th>` | `_report_table_style.html` line 7 | PASS |
| `z-index: 1` on sticky header | same line | PASS |
| `box-shadow` separator on scroll | `0 1px 0 #cbd5e1` | PASS |
| `white-space: nowrap` prevents header wrap | same line | PASS |

### 2.5 手機寬度 (≤720px)

| Check | Detail | Verdict |
|-------|--------|---------|
| Media query exists | `@media (max-width: 720px)` adjusts `max-height` | PASS |
| Horizontal scroll still works | `overflow: auto` is not overridden | PASS |
| Sticky header on narrow viewport | `position: sticky` not overridden at 720px | P1 — header may overlap content on very small screens; no width reduction or column hiding |
| No responsive column hiding | All columns always visible; user must scroll horizontally | P1 — degraded UX on ≤720px |

### 2.6 金額無小數

| Check | Detail | Verdict |
|-------|--------|---------|
| `money_int` filter defined | `factory.py` line 23–26: `Decimal.quantize(Decimal('1'), ROUND_HALF_UP)` → `:,.0f` | PASS |
| All money fields use `money_int` | collection: 10 fields, settlement: 9 fields, new_tenants: 2 fields, yearly: 9 fields — all piped through `money_int` | PASS |
| Tfoot totals also use `money_int` | collection: 3 totals, settlement: 9 totals, yearly: 9 totals | PASS |
| Export uses `export_money_rows` | Same `ROUND_HALF_UP` to integer rule applied to CSV/XLSX | PASS |

### 2.7 超額付款未收不為負

| Check | Detail | Verdict |
|-------|--------|---------|
| `_outstanding_amount` clamps to ≥ 0 | `report_service.py` line 24: `max(total - paid, Decimal("0"))` | PASS |
| Applied in `property_collection` | line 159 | PASS |
| Applied in `property_settlement` | line 182 | PASS |
| Applied in `property_yearly` | line 244 | PASS |

### 2.8 起租/到約欄位

| Check | Detail | Verdict |
|-------|--------|---------|
| Collection shows `contract_start_date` | template line 24, column 7 | PASS |
| Collection shows `contract_end_date` | template line 24, column 8 | PASS |
| Repository queries both fields | `report_repository.py` lines 109–110 | PASS |
| New Tenants shows `start_date` / `end_date` | template line 24, columns 5–6 | PASS |
| Settlement and Yearly do not show dates | Correct — they are aggregated views | PASS |

---

## 3. CSV/XLSX 欄位與畫面一致性

### 3.1 Collection Export

| UI Column | Export Header | Match |
|-----------|--------------|-------|
| 月份 | `year_month` | PASS |
| 房東 | `landlord_name` | PASS |
| 物件 | `property_name` | PASS |
| 房號 | `room_number` | PASS |
| 房客 | `tenant_name` | PASS |
| 電話 | `tenant_phone` | PASS |
| 起租 | `contract_start_date` | PASS |
| 到約 | `contract_end_date` | PASS |
| 租金 | `rent` | PASS |
| 電費 | `electricity_amount` | PASS |
| 公設電費 | `public_electricity` | PASS |
| 水費 | `water_amount` | PASS |
| 其他 | `other_charges` | PASS |
| 其他說明 | `other_desc` | PASS |
| 前期未收 | `previous_balance` | PASS |
| 應收總額 | `total` | PASS |
| 已繳 | `paid_amount` | PASS |
| 未收 | `outstanding_amount` | PASS |

**18/18 columns match.** Export applies `export_money_rows` to 9 money fields.

### 3.2 Settlement Export

| UI Column | Export Header | Match |
|-----------|--------------|-------|
| 房東 | `landlord_name` | PASS |
| 物件 | `property_name` | PASS |
| 帳單數 | `bill_count` | PASS |
| 租金 | `rent_amount` | PASS |
| 電費 | `electricity_amount` | PASS |
| 公設電費 | `public_electricity` | PASS |
| 水費 | `water_amount` | PASS |
| 其他 | `other_charges` | PASS |
| 前期未收 | `previous_balance` | PASS |
| 應收總額 | `total_amount` | PASS |
| 已繳 | `paid_amount` | PASS |
| 未收 | `outstanding_amount` | PASS |

**12/12 columns match.**

### 3.3 New Tenants Export

| UI Column | Export Header | Match |
|-----------|--------------|-------|
| 物件 | `property_name` | PASS |
| 房號 | `room_number` | PASS |
| 房客 | `tenant_name` | PASS |
| 電話 | `tenant_phone` | PASS |
| 起租日 | `start_date` | PASS |
| 到期日 | `end_date` | PASS |
| 押金 | `deposit` | PASS |
| 租金 | `rent` | PASS |
| 起始電表 | `start_electricity_reading` | PASS |
| 起始水表 | `start_water_reading` | PASS |
| 合約狀態 | `contract_status` | PASS |
| 備註 | `notes` | PASS |

**12/12 columns match.**

### 3.4 Yearly Export

| UI Column | Export Header | Match |
|-----------|--------------|-------|
| 月份 | `year_month` | PASS |
| 物件 | `property_name` | PASS |
| 帳單數 | `bill_count` | PASS |
| 租金 | `rent_amount` | PASS |
| 電費 | `electricity_amount` | PASS |
| 公設電費 | `public_electricity` | PASS |
| 水費 | `water_amount` | PASS |
| 其他 | `other_charges` | PASS |
| 前期未收 | `previous_balance` | PASS |
| 應收總額 | `total_amount` | PASS |
| 已繳 | `paid_amount` | PASS |
| 未收 | `outstanding_amount` | PASS |

**12/12 columns match.**

---

## 4. Issues Found

### INC-UI-REG-01 — P1: 手機寬度表格標頭重疊

- **Location**: `_report_table_style.html` line 7 + all 4 report templates
- **Description**: `position: sticky; top: 0` on `<th>` elements works inside `.report-table-scroll`, but at ≤720px viewport width, the fixed header occupies significant vertical space while the table body still requires full horizontal scrolling. No column collapse, hiding, or responsive reflow is implemented.
- **Impact**: On mobile devices (≤720px), the sticky header plus filter form consume most of the viewport height, leaving minimal visible data rows. Users must scroll both horizontally and vertically to read table content.
- **Reproduction**:
  1. Open any of the 4 report pages
  2. Resize browser to 375px width (iPhone SE)
  3. Observe: filter form + sticky header consume ~180px; remaining ~200px shows partial table; horizontal scroll required for all columns
- **Suggested Fix**: Add CSS media query to reduce `th`/`td` padding, font size, and consider hiding low-priority columns (e.g., 電話, 其他說明) on narrow viewports. Alternatively, switch to a card-based layout on mobile.

### INC-UI-REG-02 — P1: 手機寬度無欄位隱藏或回流

- **Location**: All 4 report templates — no responsive column strategy
- **Description**: The collection page has 18 columns (min-width 1740px). On a 375px mobile screen, this requires 4.6x horizontal scrolling. No CSS or JS mechanism hides次要欄位 (電話, 其他說明, 前期未收) on narrow screens.
- **Impact**: Mobile usability is severely degraded. Core data (物件, 房號, 房客, 租金, 應收, 已繳, 未收) is buried behind excessive scrolling.
- **Reproduction**:
  1. Open `/reports/collection` on a 375px-wide viewport
  2. Attempt to read the table — must scroll past 月份, 房東, 物件, 房號, 房客, 電話, 起租, 到約, 租金, 電費, 公設電費, 水費, 其他, 其他說明, 前期未收 before reaching 應收總額
- **Suggested Fix**: Use `@media (max-width: 720px)` to add `.hide-mobile { display: none; }` on non-essential columns. Priority columns: 物件, 房號, 房客, 租金, 應收總額, 已繳, 未收.

### INC-UI-REG-03 — P2: Property Yearly Export 命名不一致

- **Location**: `reports/property_yearly.html` line 13
- **Description**: Export link generates `url_for('reports.property_yearly_report_export', year=year, property_id=selected_property_ids, format='csv')`. The page's filter form uses `property_ids` (plural). The export route reads `property_id` (singular). This is a naming inconsistency — not a functional break since the export route correctly reads the singular param.
- **Impact**: Developer confusion; no user-visible impact.
- **Reproduction**: Inspect export link URL vs form field name on `/reports/property-yearly`.

### INC-UI-REG-04 — P2: Collection 頁空資料文字冗贅

- **Location**: `reports/collection.html` line 28
- **Description**: Empty state text reads "符合條件的收租資料尚無資料" — the word "資料" appears twice ("收租**資料**尚無**資料**"), which is awkward Chinese.
- **Impact**: Minor UX polish. Other pages use cleaner phrasing.
- **Reproduction**: Load `/reports/collection` with a month that has no billing data.
- **Suggested Fix**: Change to "符合條件的收租明細尚無資料" or "本月尚無收租資料".

### INC-UI-REG-05 — P2: 合約日期欄位無格式化

- **Location**: `reports/collection.html` line 24 (columns 7–8)
- **Description**: `contract_start_date` and `contract_end_date` are rendered as `{{ row.contract_start_date }}` without a formatting filter. If the value is a Python `date` object, Jinja2 renders it as ISO `YYYY-MM-DD`. This is acceptable but inconsistent with the `money_int` filter used for amounts.
- **Impact**: Dates render as `2026-01-15` which is readable but not localized (e.g., no `YYYY/MM/DD` or `YYYY年MM月DD日`).
- **Reproduction**: Open `/reports/collection` with data — dates appear as `YYYY-MM-DD`.
- **Suggested Fix**: Add a `date_ui` template filter for consistent date formatting, or accept ISO format as-is.

### INC-UI-REG-06 — P2: 匯出連結在無物件選取時產生空查詢參數

- **Location**: All 4 report templates — export `<a>` links
- **Description**: When no properties are selected, `selected_property_ids` is an empty list. Flask `url_for` generates `?property_id=&property_id=` (empty values). The export route's `_selected_property_ids` falls back to all visible properties when the list is empty, so the export still works correctly. However, the URL contains empty query parameters.
- **Impact**: No functional impact — the export works. But the URL looks unclean (e.g., `...export?year_month=2026-07&property_id=&property_id=&format=csv`).
- **Reproduction**: Open any report page without selecting properties, inspect the export link URL.
- **Suggested Fix**: Filter out empty values before passing to `url_for`, or accept as cosmetic-only.

---

## 5. Summary

| Severity | Count | IDs |
|----------|-------|-----|
| P0 | 0 | — |
| P1 | 2 | INC-UI-REG-01, INC-UI-REG-02 |
| P2 | 4 | INC-UI-REG-03, INC-UI-REG-04, INC-UI-REG-05, INC-UI-REG-06 |

**P0 (Blocking)**: None found.

**P1 (Serious UX)**: Mobile responsiveness — all 4 report pages lack responsive column strategies for ≤720px viewports. The 18-column collection page is especially impacted. The sticky header, while functional, provides minimal value when the table requires 4x+ horizontal scrolling on mobile.

**P2 (Polish)**: Empty state wording, date formatting, export URL cosmetic, naming inconsistency.

**Overall**: The reporting expansion is functionally correct. Money formatting (integer, no decimals), outstanding amount clamping (≥0), multi-property filtering, sticky headers, horizontal scroll, and CSV/XLSX export field consistency all pass. The primary gap is mobile responsiveness.
