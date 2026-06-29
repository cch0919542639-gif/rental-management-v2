# Phase 2 UI Regression 05

Author: mimo
Round: `agent/mimo-phase2-ui-regression-05`
Status: completed
Date: 2026-06-29
Base: `codex-phase2-mainline-01`

## Scope

- Phase 2 UI regression focused on new workflows
- electricity property detail / new-bill / quick-reading / reading-log
- billing / payments / maintenance status labels

## Pages Checked

| Page | Route | Status | Notes |
|------|-------|--------|-------|
| Electricity Index | /electricity/ | ✅ Normal | property.name with fallback |
| Electricity Bill Detail | /electricity/bills/<id> | ✅ Normal | Chinese headers |
| Electricity Property Detail | /electricity/property/<id> | ✅ Fixed | Summary cards now Chinese |
| Electricity Reading Log | /electricity/property/<id>/reading-log | ✅ Fixed | Headers now Chinese |
| Water List | /water/ | ✅ Normal | property.name displayed |
| Payments List | /payments/ | ✅ Fixed | Status labels now Chinese |
| Reports Monthly | /reports/monthly | ✅ Normal | public_electricity + other_desc |
| Billing List | /billing/ | ✅ Fixed | Title and contract link now Chinese |
| Maintenance Index | /maintenance/ | ✅ Normal | Full CRUD + status transitions |

## Changes Applied

### 1. property_detail.html — Summary cards Chinese

**問題：** Summary cards showed English status names (pending, calculated, posted)

**修正：**
- pending → 待處理
- calculated → 已計算
- posted → 已回寫

### 2. reading_log.html — Headers Chinese

**問題：** Table headers showed English (Reading ID, Bill ID)

**修正：**
- Reading ID → 抄表編號
- Bill ID → 帳單編號

### 3. billing/list.html — Title and contract link Chinese

**問題：** Title "Billing" and contract link "Contract {{ id }}" showed English

**修正：**
- Billing → 帳單管理
- Contract {{ id }} → 合約 {{ id }}

### 4. payments/list.html — Status labels Chinese

**問題：** Status column showed English (pending, verified, linked, rejected)

**修正：**
- pending → 待審核
- verified → 已驗證
- linked → 已連結
- rejected → 已駁回

## Not Changed (Test Compatibility)

### electricity/bill_detail.html — Status display

**Observation：** Status column and button text "標記 calculated" remain English

**Reason：** Integration test `test_electricity_calculate_and_view` checks for "calculated" in response

**Recommendation：** Test should be updated to check Chinese text, then template can be localized

### electricity/index.html — Bill status display

**Observation：** Bill status column remains English

**Reason：** Consistency with bill_detail.html, potential test dependencies

## Test Results

- `pytest tests\integration -q` → **41 passed, 15 skipped**
- All tests maintain baseline (no regressions)

## Verification Checklist

- [x] 中文標題 / 中文按鈕 / 中文狀態文字
- [x] property / room 顯示是否優先用名稱而不是裸 ID
- [x] 空列表 / 無資料頁是否可讀
- [x] flash message 是否合理
- [x] year_month 畫面顯示是否仍為 YYYY-MM
- [x] electricity property detail 三個快捷入口是否清楚
- [x] reading-log 欄位是否足夠辨識 bill / meter / room / usage / amount

## Conclusion

- 4 files modified (templates only)
- All new workflow pages verified normal
- Status labels now consistent Chinese where test-safe
- No blockers found
- No incidents created
