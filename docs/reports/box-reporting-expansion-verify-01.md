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

**結果：5 passed in 1.68s**

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

**結果：128 passed, 15 skipped in 111.87s**

無失敗、無錯誤、無 traceback。

---

## 2. 功能驗證項目

### 2.1 CSV 匯出

- Route: `/reports/collection/export?year_month=2026-06&property_id={id}&format=csv`
- Content-Type: `text/csv`
- 內容包含 `paid_amount` 欄位與承租人姓名
- ✅通過

### 2.2 XLSX 匯出

- Route: `/reports/property-yearly/export?year=2026&property_id={id}&format=xlsx`
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- ✅通過

### 2.3 PaymentRecord linked amount

- Bill total=10,100，PaymentRecord linked 4,000
- Collection 頁面顯示 paid=4,000，outstanding=6,100
- ✅通過

### 2.4 未收款（溢繳上限）

- 兩筆 PaymentRecord 共 14,000（超逾 total 10,100）
- outstanding_amount=0 (不顯示負數)
- ✅通過

### 2.5 整數金額四捨五入

- `ReportService.export_money_rows`：`Decimal("100.5")` → 101
- ✅通過

### 2.6 Property 權限範圍

- landlord role 使用者（landlord_id 不同）請求其他物件的 collection → **403 Forbidden**
- ✅通過

### 2.7 多 property 篩選

- settlement、new-tenants、property-yearly 支援多 `property_id`
- 不同物件資料正確分列
- ✅通過

---

## 3. 基線對照

| 項目 | 本次 | 說明 |
|------|------|------|
| Reporting expansion tests | 5/5 passed | 新測試 |
| 全整合套件 | 128 passed, 15 skipped | baseline codex-phase2-mainline-01 |

---

## 4. 結論

**所有驗證項目通過。** 新報表功能（collection / settlement / new-tenants / property-yearly 頁面、CSV/XLSX 匯出、PaymentRecord 連結金額、溢繳上限、整數金額、property 權限閘門）均正常運作，且未對現有測試造成回歸。