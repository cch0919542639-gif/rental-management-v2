# Phase 1 UI Regression 02

Author: mimo
Round: `agent/mimo-ui-regression-02`
Status: completed summary backfill
Date: 2026-06-28

## Scope

- Phase 1 已完成頁面的 UI 欄位對齊與回歸檢查

## Delivered Files

- `app/models/electricity.py`
- `app/templates/electricity/index.html`
- `app/templates/electricity/bill_detail.html`
- `app/templates/water/list.html`
- `coordination/progress/mimo.md`

## P1 Fixes Applied

1. `ElectricityMeter` 加入 `property` relationship
2. `ElectricityBill` 加入 `property` relationship
3. `electricity/index.html`：電表 list 與電費單 list 改顯示 `property.name`
4. `electricity/bill_detail.html`：表頭改中文（用電量 / 計算金額 / 確認金額），並加入物件名稱
5. `water/list.html`：改顯示 `property.name`

## P2 Pending Decisions

- 共 10 項 P2 gap
- 已知待決策項目包括：
- `billing list` 補 `public_electricity` / `other_charges`
- `monthly report` 補 `public_electricity` / `other_desc`
- `payments list` 補 `bank / account / transaction_id`
- `maintenance schema` 凍結

## Manual Regression Result

- 11 個頁面正常顯示
- 10 個 flash 訊息正確
- 所有導覽連結正常
- 所有欄位名稱對齊 `data_contracts`

## Conclusion

- P1 問題已修正
- P2 問題不阻擋目前主幹，但建議於後續階段逐項處理
