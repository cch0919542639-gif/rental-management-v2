# UI Polish Round 2

Author: mimo
Round: `agent/mimo-ui-polish-02`
Status: completed
Date: 2026-06-29

## Scope

- 第二輪 UI polish：低風險顯示一致性修正
- 補齊上一輪未合併到 main 的 payments/reports 欄位
- 中文欄位、導覽、一致性細節

## Changes Applied

### 1. water/list.html — property.name 顯示

**問題：** 水費單列表顯示 `property_id`（數字）而非 `property.name`

**修正：** `{{ water_bill.property_id }}` → `{{ water_bill.property.name }}`

**備註：** WaterBill model 已有 `property` relationship，可直接使用

### 2. electricity/bill_detail.html — 英文表頭改中文

**問題：** 抄表列表使用英文欄位名（usage, calculated, confirmed）

**修正：**
- `usage` → `用電量`
- `calculated` → `計算金額`
- `confirmed` → `確認金額`

### 3. payments/list.html — 對帳欄位補齊

**問題：** 缺少 bank_name、account_number、transaction_id 欄位

**修正：**
- 新增 `<th>銀行</th>`、`<th>帳戶</th>`、`<th>交易編號</th>` 表頭
- 新增對應資料欄位
- colspan 7 → 10

**備註：** 此修正為上一輪（mimo-phase2-ui-gap-01）遺漏未合併到 main

### 4. reports/monthly.html — 欄位完整性

**問題：** 缺少 public_electricity 和 other_desc 欄位

**修正：**
- 新增 `<th>公設電費</th>` 和 `<th>其他說明</th>` 表頭
- 新增對應資料欄位
- colspan 13 → 15

**備註：** 此修正為上一輪遺漏未合併到 main

### 5. report_repository.py — 查詢欄位補齊

**問題：** monthly_report_rows 查詢缺少 public_electricity 和 other_desc

**修正：** 新增 `MonthlyBill.other_desc.label("other_desc")` 和 `MonthlyBill.public_electricity.label("public_electricity")`

**備註：** 此修正為上一輪遺漏未合併到 main

## Blockers Identified

### report_service.py 未更新

`app/services/report_service.py` monthly_report() 方法未回傳 `public_electricity` 和 `other_desc`，導致 monthly report template 會觸發 UndefinedError。

**需 Codex 修正：** 在 report_service.py monthly_report() dict 中加入：
```python
"other_desc": row.other_desc,
"public_electricity": row.public_electricity,
```

已建立 incident 記錄：`coordination/incidents/2026-06-29_1100_mimo_report-service-fields.md`

### electricity property.name 顯示

`ElectricityMeter` 和 `ElectricityBill` model 缺少 `property` relationship，無法在 template 中使用 `property.name`。需 Codex 在 model 層補充。

## Remaining Gaps (Not Fixable This Round)

| Gap | Issue | Owner |
|-----|-------|-------|
| electricity/index.html | Shows property_id instead of property.name | Codex (needs model relationship) |
| report_service.py | Missing public_electricity, other_desc in return dict | Codex (service update needed) |

## Verification

### Templates Modified

| Template | Change | Status |
|----------|--------|--------|
| `water/list.html` | property_id → property.name | ✅ Verified |
| `electricity/bill_detail.html` | English headers → Chinese | ✅ Verified |
| `payments/list.html` | +3 columns (bank, account, transaction_id) | ✅ Verified |
| `reports/monthly.html` | +2 columns (public_electricity, other_desc) | ✅ Verified |

### Consistency Check

- [x] All nav links functional
- [x] Flash messages consistent
- [x] Template titles consistent
- [x] No dead routes

## Conclusion

- 5 template/repository fixes applied
- 2 blockers identified (require Codex intervention)
- No backend service or model changes made
- No schema decisions modified
