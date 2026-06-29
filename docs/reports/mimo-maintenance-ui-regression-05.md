# Maintenance Phase 2B UI Regression 05

Author: mimo
Round: `agent/mimo-maintenance-ui-regression-05`
Status: completed
Date: 2026-06-29
Base: `codex-phase2-mainline-01`

## Scope

- Maintenance Phase 2B 新增 UI focused regression
- Filter UI, open view, room-scoped list, summary cards, maintenance report

## Pages Checked

| Page | Route | Status | Notes |
|------|-------|--------|-------|
| Maintenance Index | /maintenance/ | ✅ Fixed | Status labels now Chinese |
| Maintenance Open | /maintenance/open | ✅ Fixed | Open statuses only, Chinese labels |
| Room-Scoped | /maintenance/rooms/<id> | ✅ Fixed | Correct room data, Chinese labels |
| Maintenance Create | /maintenance/create | ✅ Normal | Form with all fields |
| Maintenance Edit | /maintenance/<id>/edit | ✅ Normal | Form with all fields |
| Maintenance Report | /reports/maintenance | ✅ Fixed | Totals/property/status summary |

## Changes Applied

### 1. maintenance/index.html — Status labels Chinese

**問題：** Status column and breakdown cards showed English status values

**修正：**
- Status column: `{{ request.status }}` → Chinese mapping
- Breakdown cards: `{{ item.status }}` → Chinese mapping
- Transition buttons: English → Chinese (指派/開始處理/標記已解決/關單)

### 2. reports/maintenance.html — Status labels Chinese

**問題：** Status column showed English status values

**修正：** Status column: `{{ row.status }}` → Chinese mapping

### 3. maintenance/forms.py — Filter status choices Chinese

**問題：** Filter dropdown showed English status labels

**修正：** Status choices: English → Chinese (已通報/已指派/處理中/已解決/已關閉/已取消)

### 4. reports/forms.py — Report filter status choices Chinese

**問題：** Report filter dropdown showed English status labels

**修正：** Status choices: English → Chinese (已通報/已指派/處理中/已解決/已關閉/已取消)

## Verification

### Filter UI

- [x] Status filter dropdown shows Chinese labels
- [x] Priority filter dropdown shows Chinese labels (低/中/高/緊急)
- [x] Room filter dropdown shows property.name / room_number
- [x] Date range filter works
- [x] "套用篩選" button submits correctly
- [x] "清除篩選" link resets to index

### Open View

- [x] `/maintenance/open` shows only reported/assigned/in_progress
- [x] Scope label shows "Open 維修單"
- [x] Filter works on open view

### Room-Scoped View

- [x] `/maintenance/rooms/<id>` shows correct room data
- [x] Scope label shows "房間維修單：{property.name} / {room_number}"
- [x] Filter preset to room_id

### Summary Cards

- [x] 筆數 (request_count) displays correctly
- [x] 預估成本 (estimated_total) displays correctly
- [x] 實際成本 (actual_total) displays correctly
- [x] Status breakdown cards show Chinese labels

### Maintenance Report

- [x] Totals card: 維修單數/Open/預估成本/實際成本
- [x] Property summary table: 房東/物件/維修單數/Open/預估成本/實際成本
- [x] Status summary table: 狀態/維修單數/預估成本/實際成本
- [x] Filter form: 物件/狀態/通報起日/通報迄日

### Status Transition Buttons

- [x] reported → 指派 (assigned)
- [x] assigned → 開始處理 (in_progress)
- [x] in_progress → 標記已解決 (resolved)
- [x] resolved → 關單 (closed)

### Navigation

- [x] "新增維修單" link works
- [x] "全部維修單" link works
- [x] "Open 維修單" link works
- [x] "查看維修單" link in room snapshot works
- [x] "編輯" link works

## Test Results

- `pytest tests\integration -q` → **35 passed, 15 skipped**
- Tests maintain previous baseline (34→35 passed, +1)

## Conclusion

- 4 files modified (templates + forms)
- All Phase 2B maintenance UI verified normal
- Status labels now consistent Chinese throughout
- No blockers found
- No incidents created
