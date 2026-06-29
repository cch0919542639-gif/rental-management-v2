# Water Preview UI Regression 01

Author: mimo
Round: `agent/mimo-water-preview-ui-01`
Status: completed
Date: 2026-06-29
Base: `codex-phase2-mainline-01`

## Scope

- Water preview page `/water/<id>/preview`
- Flow: water list → preview → post
- Copy, fields, empty state consistency

## Flow Verified

### 1. Water List (`/water/`)

| Item | Status | Notes |
|------|--------|-------|
| Title | ✅ | "水費單" (Chinese) |
| Table headers | ✅ | ID, 物件, 帳期, 總額 |
| Property display | ✅ | Uses `water_bill.property.name` |
| Action links | ✅ | 編輯, 預覽分攤, 回寫月帳單 |
| Empty state | ✅ | "尚無水費單" |

### 2. Water Preview (`/water/<id>/preview`)

| Item | Status | Notes |
|------|--------|-------|
| Title | ✅ | "水費預覽" |
| Bill info | ✅ Fixed | "水費單 #{{ id }} / {{ property.name }}" |
| Form fields | ✅ | 月帳單 ID, 分攤模式, 獨立水表金額 |
| Mode labels | ✅ Fixed | "按居住天數分攤", "獨立水表" |
| Submit button | ✅ | "預覽分攤" |
| Preview results | ✅ | 模式, 月帳單, 合約, 預覽水費金額, 預覽用水量 |
| Shared mode details | ✅ | 合約居住天數, 物件總居住天數, 總用量 |
| Post link | ✅ | "確認後前往回寫月帳單" |

### 3. Water Post Form (`/water/<id>/post`)

| Item | Status | Notes |
|------|--------|-------|
| Title | ✅ | "回寫月帳單" |
| Bill info | ✅ Fixed | "水費單 #{{ id }}" |
| Preview link | ✅ | "先看預覽結果" |
| Form fields | ✅ | 月帳單 ID, 分攤模式, 獨立水表金額 |
| Submit button | ✅ | "回寫月帳單" |

## Changes Applied

### 1. preview.html — Bill info Chinese

**問題：** "Water Bill #{{ id }}" showed English

**修正：** "Water Bill" → "水費單"

### 2. post_form.html — Bill info Chinese

**問題：** "Water Bill #{{ id }}" showed English

**修正：** "Water Bill" → "水費單"

### 3. water/forms.py — Mode labels Chinese

**問題：** Mode choices showed English (shared_by_stay_days, independent_meter)

**修正：**
- shared_by_stay_days → 按居住天數分攤
- independent_meter → 獨立水表

## Empty State Verification

| Page | Empty State | Status |
|------|-------------|--------|
| Water List | "尚無水費單" | ✅ |
| Water Preview | Form still functional | ✅ |
| Water Post Form | Form still functional | ✅ |

## Navigation Consistency

- [x] Water list → preview link works
- [x] Preview → post link works
- [x] Post → preview link works
- [x] All back links functional
- [x] Flash messages consistent

## Test Results

- `pytest tests\integration -q` → **46 passed, 15 skipped**
- All tests maintain baseline (no regressions)

## Conclusion

- 3 files modified (2 templates + 1 form)
- All water preview pages verified normal
- Flow: list → preview → post works correctly
- No blockers found
- No incidents created
