# box-property-expense-verify-01

Date: 2026-07-14
Author: box
Branch: `agent/box-property-expense-verify-01`
Baseline: `codex-phase2-mainline-01`

---

## 1. 測試結果

### 1.1 R3 PropertyExpense Tests

```bash
cd D:\CodexRuntime\rental\rebuild-main && py -3 -m pytest tests\integration\test_property_expense_crud_states.py -q --tb=long
```

**結果：3 passed in 0.73s**

| Test | Status |
|------|--------|
| `test_property_expense_draft_post_void_and_immutability` | ✅ PASS |
| `test_property_expense_delete_draft_and_export_only_posted` | ✅ PASS |
| `test_property_expense_rejects_non_positive_amounts` | ✅ PASS |

### 1.2 Full Integration Suite

```bash
py -3 -m pytest tests\integration -q --tb=long
```

**結果：131 passed, 15 skipped in 91.84s**

無失敗、無錯誤、無 traceback。Baseline 為 128 passed (+3 property expense tests)。

---

## 2. 逐項驗證

### 2.1 Migration dry-run / execute idempotency

- Dry-run `run_migrations.py --id 20260717_000005_property_expenses` → 正確顯示 existing table 狀態
- Execute → 建立 property_expenses table，記錄到 migration_log
- Re-run → 正確略過（already applied）
- ✅通過

### 2.2 Draft 建立、編輯、刪除

- `PropertyExpenseService.create()` → draft 狀態
- `PropertyExpenseService.update()` → 可編輯（僅限 draft）
- `PropertyExpenseService.delete()` → 僅限 draft
- ✅通過（測試 cover）

### 2.3 Draft → Posted → Voided；作廢必填原因

- draft → posted → OK
- posted → 禁止編輯/硬刪除（ValueError）
- posted → voided（無原因）→ ValueError
- posted → voided（有原因）→ OK，void_reason 儲存
- cancelled → posted → ValueError
- ✅通過

### 2.4 Posted / Voided / Cancelled 禁止編輯與硬刪除

| 狀態 | update | delete |
|------|--------|--------|
| posted | ValueError | ValueError |
| voided | ValueError（by trans. guard） | ValueError |
| cancelled | ValueError（by trans. guard） | ValueError |
- ✅通過

### 2.5 分類非法值、金額 ≤ 0 拒絕

- Invalid category `bogus` → `ValueError: Invalid expense category`
- 8 個有效類別全數通過
- 建立或編輯的 amount ≤ 0 → `ValueError: Expense amount must be positive`
- ✅通過

### 2.6 物件／狀態／分類篩選

- Route `GET /expenses/?status=posted&category=repair` → 200
- Route `GET /expenses/?property_id=<id>` → 200
- `PropertyExpenseRepository.list_filtered()` 存在，支援 property_id/status/category 參數
- ✅通過

### 2.7 Posted 合計與 CSV/XLSX 僅含 posted

- CSV export: 僅 posted 狀態的 expense 出現（draft 被刪除不出現）
- CSV Content-Type: `text/csv`，包含金額
- XLSX export: Content-Type `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- ✅通過

---

## 3. 缺陷

**無。** 全部測試與手動驗證項目通過。

---

## 4. 結論

所有 R3 PropertyExpense 驗收項目通過。功能正常，無回歸，可合併至 `codex-phase2-mainline-01`。
