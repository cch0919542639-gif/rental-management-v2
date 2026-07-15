# box-reporting-expansion-verify-01

Date: 2026-07-14
Author: box
Branch: `agent/box-reporting-expansion-verify-01`
Baseline: `codex-phase2-mainline-01`

---

## 1. 執行命令

### 1.1 Reporting Expansion Tests

```bash
cd D:\CodexRuntime\rental\rebuild-main
py -3 -m pytest tests\integration\test_reporting_expansion.py -q --tb=long
```

**結果：5 passed in 1.45s**

| Test | Status |
|------|--------|
| `test_property_collection_filters_and_uses_linked_payment_amount` | ✅ PASS |
| `test_property_summary_new_tenants_and_yearly_support_multiple_properties` | ✅ PASS |
| `test_reporting_expansion_exports_csv_and_xlsx` | ✅ PASS |
| `test_property_reports_reject_property_outside_landlord_scope` | ✅ PASS |
| `test_property_collection_caps_overpayment_and_rounds_export_money` | ✅ PASS |

### 1.2 Full Integration Suite

```bash
py -3 -m pytest tests\integration -q --tb=long
```

**結果：128 passed, 15 skipped in 125.33s**

無失敗、無錯誤、無 traceback。

---

## 2. 功能驗證項目

### 2.1 CSV / XLSX 匯出可下載

- **collection/export?format=csv**: `Content-Type: text/csv`，包含 `paid_amount` 欄位與承租人姓名
- **property-yearly/export?format=xlsx**: `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- 驗證通過 ✅

### 2.2 PaymentRecord linked amount

- `test_property_collection_filters_and_uses_linked_payment_amount`: 4000 元 PaymentRecord linked 至 bill 後，collection 報表顯示 paid_amount=4,000、outstanding=6,100
- 驗證通過 ✅

### 2.3 未收款（outstanding_amount）

- 多筆 PaymentRecord 累加：14000 元總付款，outstanding_amount 為 0（溢繳不顯示負數）
- 驗證通過 ✅

### 2.4 整數金額（export_money_rows）

- `Decimal("100.5")` → 101（四捨五入至整數）
- 驗證通過 ✅

### 2.5 Property 權限範圍

- 使用 `role=landlord` 且 `landlord_id` 不屬於該物件的使用者登入後請求 collection → **403 Forbidden**
- 驗證通過 ✅

### 2.6 多 property 篩選

- Settlement / new-tenants / property-yearly 均支援多 `property_id` 參數
- 不同物件的資料正確分列顯示
- 驗證通過 ✅

---

## 3. 基線對照

| 項目 | 本次 | 前次水準 |
|------|------|----------|
| Reporting expansion tests | 5/5 passed | — |
| Full integration suite | 128 passed, 15 skipped | 122 passed, 15 skipped (+6, 含 5 新 reporting + 1) |
| Failure / traceback | 0 | 0 |

---

## 4. 結論

**所有驗證項目通過。** 新報表功能（collection / settlement / new-tenants / property-yearly 頁面、CSV/XLSX 匯出、PaymentRecord 連結金額、溢繳上限、整數金額、property 權限閘門）均正常運作，且未對現有測試造成回歸。

可合併至 `codex-phase2-mainline-01`。