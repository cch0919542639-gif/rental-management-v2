# R3 報表上線後唯讀驗證報告

- **執行者**: AAA agent
- **日期**: 2026-07-19
- **工作目錄**: `D:\CodexRuntime\rental\rebuild-main`
- **Git 分支**: `agent/box-property-expense-verify-01`
- **HEAD commit**: `9da72a4be8a3d79f51a7ca1cfaef89037e134f6c` ("docs: record R3 migration execution")
- **類型**: 唯讀驗證 (read-only verification)

---

## 1. Migration 腳本確認

| 檔案 | 存在 |
|---|---|
| `scripts/migration/apply_20260717_000005_property_expenses.py` | 是 |

---

## 2. Migration 狀態

### `run_migrations.py --list` 輸出

```
20260701_000001_phase4_baseline_marker [pending]
20260701_000002_alembic_bridge [pending]
20260703_000003_utility_policy_codes [pending]
20260712_000004_monthly_bill_previous_balance [pending]
20260717_000005_property_expenses [applied]
```

`20260717_000005_property_expenses` 狀態: **applied**

### Dry-run rerun

```
> py -3 scripts\migration\run_migrations.py --id 20260717_000005_property_expenses

Mode: DRY-RUN
Skip 20260717_000005_property_expenses: already applied
```

**確認: already applied，不會重複執行。**

### 正式資料庫 (runtime.db) `schema_migration_log`

| Migration ID | 時間 |
|---|---|
| `20260717_000005_property_expenses` | 2026-07-19 04:19:08 |

### 正式資料庫 (runtime.db) `property_expenses` table

- 14 欄位，結構正確（`id`, `property_id`, `transaction_date`, `category`, `amount`, `payee`, `reference_no`, `notes`, `record_status`, `created_by_id`, `voided_at`, `void_reason`, `updated_at`, `created_at`）
- 筆數: **0**

---

## 3. 測試結果

### 報表與支出整合測試

```
> py -3 -m pytest tests/integration/test_reporting_expansion.py tests/integration/test_property_expense_crud_states.py -q

10 passed in 2.38s
```

### 完整測試套件

```
> py -3 -m pytest -q

134 passed, 15 skipped in 85.09s
```

| 指標 | 預期基線 | 實際 |
|---|---|---|
| passed | 133 | **134** |
| skipped | 15 | 15 |
| 總收集 | 148 | **149** |

實際 passed 比預期基線多 1，總收集多 1。差異來源為本分支新增的 migration dry-run 唯讀回歸測試。

---

## 4. posted 支出狀態

`runtime.db` 中 `property_expenses` 資料表筆數為 **0**。

**判定: 無實際 posted 支出可驗收。** 未以任何方式建立測試資料。

---

## 5. 合規檢查

| 項目 | 狀態 |
|---|---|
| 未修改 runtime.db | 通過 |
| 未修改 runtime-real.db | 通過 |
| 未執行 --execute | 通過 |
| 未刪除/移動/歸檔 migration 腳本 | 通過 |
| 未修改 app/、scripts/migration/ 或測試程式 | 通過 |
