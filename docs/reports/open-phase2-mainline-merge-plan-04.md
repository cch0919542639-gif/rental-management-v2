# Phase 2 Mainline Merge Plan — Round 4

Author: open
Date: 2026-06-29
Baseline: `codex-phase2-mainline-01` (local + remote)
Reference: `open-phase2-main-gap-reconcile-03.md`, `open-phase2-implementation-backlog-01.md`

---

## 1. Executive Summary

以 `codex-phase2-mainline-01` 為唯一比較基準，核對 12 個 agent branch 的內容，判定哪些仍值得整併進主幹。

**核心發現：全部 12 個 agent branch 已被 mainline 吸收或超車。** 沒有任何 branch 包含 mainline 尚未具備的核心功能代碼。唯一殘存價值為少數模板、測試與協作文件。

---

## 2. 各 Branch 狀態總表

| Branch | Type | 相對於 mainline 的 new files | 結論 |
|--------|------|-----------------------------|------|
| `agent/open-low-risk-crud-02` | code | 2 app files + 8 coordination/docs | **大部分已進 mainline**；剩 1 個模板 + 1 個測試可選用 |
| `agent/mimo-ui-regression-03` | code | 0 | **完全過時** — diff 全為負數（欲刪除 mainline 已加的功能） |
| `agent/box-tests-runbook-04` | code | 0 | 同上 |
| `agent/box-phase2-tests-runbook-01` | code | 0 | 同上 |
| `agent/box-test-runbook-02` | code | 0 | 同上 |
| `agent/box-tests-runbook-03` | code | 0 | 同上 |
| `agent/mimo-phase2-ui-gap-01` | code | 0 | 同上 |
| `agent/mimo-ui-polish-02` | code | 2 coordination/docs | 僅 task card + 報告，無 code 價值 |
| `agent/reasonix-maintenance-review-02` | docs | 6 coordination/docs | 僅 task card + review 報告 |
| `agent/reasonix-phase2-contract-notes-01` | docs | 0 | 完全過時 |
| `agent/reasonix-maintenance-migration-guard-03` | docs | 1 report | 新報告 `reasonix-maintenance-migration-guard-03.md` |
| `agent/open-gap-audit-02` | docs | *(已 base 在 main 前)* | 已被 reconcile-03/04 取代 |
| `agent/open-phase2-implementation-backlog-01` | docs | *(已 base 在 main 前)* | 已被 reconcile-03/04 取代 |

---

## 3. 尚有殘餘價值的檔案

### 3.1 從 `agent/open-low-risk-crud-02`

| 檔案 | 價值說明 | 建議 |
|------|---------|------|
| `app/templates/electricity/property_bills.html` | 專用 property filter 頁面模板（28 行）。Mainline 使用共用 `index.html` + `selected_property` 參數，功能等價。 | **可選用** — 如偏好獨立頁面 UX 則 cherry-pick，否則可捨棄 |
| `tests/integration/test_low_risk_crud.py` | 涵蓋 delete CRUD + property filter 的整合測試（87 行，5 項 test） | **建議整併** — mainline 目前缺少此範圍的測試覆蓋 |
| `docs/reports/open-low-risk-crud-round2.md` | 低風險 CRUD round 2 實作報告 | 可整併進 coordination |
| `coordination/task-board/review/2026-06-29_phase2_open_low-risk-crud-01.md` | 任務卡狀態 | 應移至 `done/` 或保留 |

### 3.2 從 `agent/reasonix-maintenance-migration-guard-03`

| 檔案 | 價值說明 | 建議 |
|------|---------|------|
| `docs/reports/reasonix-maintenance-migration-guard-03.md` | Migration guard 報告（174 行） | **建議整併** — 對 maintenance 正式 migration 有參考價值 |

### 3.3 從 `agent/reasonix-maintenance-review-02`

| 檔案 | 價值說明 | 建議 |
|------|---------|------|
| `docs/reports/reasonix-maintenance-review-02.md` | 維護契約 review 報告（277 行） | **建議整併** — 提供 Phase 0 契約審查記錄 |

### 3.4 從 `agent/mimo-ui-polish-02`

| 檔案 | 價值說明 | 建議 |
|------|---------|------|
| `docs/reports/mimo-ui-polish-02.md` | UI polish 報告（111 行） | **建議整併** — 記錄已完成 UI 修正 |

---

## 4. 分類結果

### 4.1 可直接 cherry-pick（需篩選檔案）

| 檔案 | 來源 Branch | 建議 owner |
|------|------------|-----------|
| `tests/integration/test_low_risk_crud.py` | `agent/open-low-risk-crud-02` | open |
| `app/templates/electricity/property_bills.html` | `agent/open-low-risk-crud-02` | Codex（決定 UX 方向） |

### 4.2 僅 docs/reports，可直接整併

| 檔案 | 來源 Branch |
|------|------------|
| `docs/reports/reasonix-maintenance-migration-guard-03.md` | `agent/reasonix-maintenance-migration-guard-03` |
| `docs/reports/reasonix-maintenance-review-02.md` | `agent/reasonix-maintenance-review-02` |
| `docs/reports/mimo-ui-polish-02.md` | `agent/mimo-ui-polish-02` |

### 4.3 應放棄（完全過時，無殘餘價值）

| Branch | 原因 |
|--------|------|
| `agent/mimo-ui-regression-03` | base 為 Phase 1 前主幹，diff 全為負數。Mainline 已有更完整實作 |
| `agent/box-tests-runbook-04` | 同上 |
| `agent/box-phase2-tests-runbook-01` | 同上 |
| `agent/box-test-runbook-02` | 同上 |
| `agent/box-tests-runbook-03` | 同上 |
| `agent/mimo-phase2-ui-gap-01` | 同上 |
| `agent/reasonix-phase2-contract-notes-01` | 同上 |
| `agent/open-gap-audit-02` | 已被後續 reconcile 報告取代 |
| `agent/open-phase2-implementation-backlog-01` | 已被後續 reconcile 報告取代 |

---

## 5. 建議順序

### Step 1 — 整併殘餘檔案（立即）

| 項目 | Owner |
|------|-------|
| cherry-pick `test_low_risk_crud.py` 進 mainline | open 或 Codex |
| 決定 `property_bills.html` 是否取代共用模板方案 | Codex |
| cherry-pick reasonix/mimo 報告進 mainline | Codex |

### Step 2 — 清理過時 branch

| 項目 | Owner |
|------|-------|
| 通知各 agent owner 其 branch 已過時，可刪除 | Codex |
| 在 GitHub 上刪除過時遠端 branch | Codex |

### Step 3 — 剩餘 Phase 2 缺口（已 backlog 但未開始）

| Tier | 項目 | 依賴 |
|------|------|------|
| T4 | Nested creation routes | 無 |
| T5.2-5.4 | Electricity property detail | T5.1 已在 mainline |
| T6 | Integrations | 外部依賴 |
| T7 | Error pages + water preview | 無 |

---

## 6. Summary Statistics

| Metric | Value |
|--------|-------|
| 核對 branch 總數 | 12 |
| 完全過時（應放棄） | 9 |
| 有殘餘文件價值 | 3 (`open-low-risk-crud-02`, `reasonix-maintenance-review-02`, `mimo-ui-polish-02`) |
| 有殘餘代碼價值 | 1 (`open-low-risk-crud-02`: 1 模板 + 1 測試) |
| 整併後仍缺口 | 9（T4 x2 + T5 x3 + T6 x6 - T5.1 - T6.3 = 9） |

---

*End of report — no models touched, no data contracts modified, no billing/payments/maintenance core re-examined.*
