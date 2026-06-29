# Phase 2 Main Gap Reconciliation — Round 3

Author: open
Date: 2026-06-29
Baseline: `origin/main` (latest push)
Reference: `open-phase2-gap-audit-02.md`, `open-phase2-implementation-backlog-01.md`

---

## 1. Executive Summary

以最新 `origin/main` 為基準，重新核對 22 個缺口（from gap-audit-02）與 7 個 Tier（from backlog-01）的完成狀態。

**關鍵發現：**
- T1 (billing core) 已全數進入 main — Codex 已完成
- T3 (delete CRUD) + T5.1 (property filter) 僅在 `agent/open-low-risk-crud-02`，未進 main
- T4 (nested creation), T5.2–T5.4 (electricity detail), T6 (integrations), T7 (polish) 皆未開始
- 其他 agent branch (`mimo-ui-regression-02`, `reasonix-review-02`, `reasonix-phase2-contract-notes-01`) 都是過時 base，無法直接 cherry-pick

---

## 2. 各 Tier 完成狀態

### 2.1 T1 — Billing Core (4 items) ✅ 已進 main

| ID | Gap | Route | Status | Note |
|----|-----|-------|--------|------|
| T1.1 | 批次產生月帳單 | `POST /billing/generate` → `POST /billing/batch` | ✅ **main** | Route registered as `/billing/batch` |
| T1.2 | 手動建立月帳單 | `GET,POST /billing/create` | ✅ **main** | |
| T1.3 | 編輯月帳單 | `GET,POST /billing/<id>/edit` | ✅ **main** | |
| T1.4 | 批次輸入 | `GET,POST /bill/batch_entry` | ✅ **main** | Covered by `/billing/batch` |

**結論：** T1 完全解除。Codex 已完成此區塊。

### 2.2 T2 — Post-to-Monthly Bridge (2 items) ✅ 可運作

| ID | Gap | Route | Status | Note |
|----|-----|-------|--------|------|
| T2.1 | Electricity post | `POST /electricity/bills/<id>/post` | ✅ **main** | Route exists + MonthlyBill exists |
| T2.2 | Water post | `POST /water/<id>/post` | ✅ **main** | Route exists + MonthlyBill exists |

**結論：** T1 解除後阻塞已消失。Post flow 可正常運作。

### 2.3 T3 — Delete CRUD (3 items) ❌ 僅在 branch

| ID | Gap | Route | Status | Action |
|----|-----|-------|--------|--------|
| T3.1 | 刪除房東 | `POST /landlords/<id>/delete` | ❌ **branch only** | Cherry-pick from `agent/open-low-risk-crud-02` |
| T3.2 | 刪除承租人 | `POST /tenants/<id>/delete` | ❌ **branch only** | Cherry-pick from `agent/open-low-risk-crud-02` |
| T3.3 | 刪除水費單 | `POST /water/<id>/delete` | ❌ **branch only** | Cherry-pick from `agent/open-low-risk-crud-02` |

**Branch diff:** `d8639ec` — 11 files (routes + services + repos + templates + tests)。

### 2.4 T4 — Nested Creation Routes (2 items) ❌ 未開始

| ID | Gap | Route | Risk | Note |
|----|-----|-------|------|------|
| T4.1 | 房東下新增物業 | `GET,POST /landlords/<lid>/properties/create` | MEDIUM | 可 reuse `properties/create` form |
| T4.2 | 物業下新增房間 | `GET,POST /properties/<pid>/rooms/create` | MEDIUM | 可 reuse `rooms/create` form |

**依賴：** 無。可隨時開始。

### 2.5 T5 — Electricity Detail (4 items)
❌ T5.1 僅在 branch；T5.2–T5.4 未開始

| ID | Gap | Route | Status | Action |
|----|-----|-------|--------|--------|
| T5.1 | 依物業篩選電費單 | `GET /electricity/property/<id>/bills` | ❌ **branch only** | Cherry-pick from `agent/open-low-risk-crud-02` |
| T5.2 | 物業級電費單建立 | `GET,POST /electricity/property/<id>/new-bill` | ❌ **未開始** | 建議等 T5.1 進 main 後進行 |
| T5.3 | 快速抄表 | `GET,POST /electricity/property/<id>/quick-reading` | ❌ **未開始** | |
| T5.4 | 抄表歷史 | `GET /electricity/property/<id>/reading-log` | ❌ **未開始** | |

### 2.6 T6 — Integrations (6 items) ❌ 未開始

全數未開始。除 T6.3 (PaymentRecords API) 可考慮提前外，其餘建議延至 Phase 3。

### 2.7 T7 — Phase 3 (2 items) ❌ 未開始

| ID | Gap | Note |
|----|-----|------|
| T7.1 | error/404.html, error/500.html | 目前僅回傳純文字 |
| T7.2 | water/preview | UX convenience |

---

## 3. Branch 衝突清單

### 3.1 可直接 cherry-pick 進 main

| Branch | Commits | Type | 可否直接 cherry-pick |
|--------|---------|------|---------------------|
| `agent/open-low-risk-crud-02` | `d8639ec` (routes + services + repos + templates + tests) | **Code** | ✅ 但需確認不攜帶外來檔案（`report_repository.py`、`bill_detail.html`、`payments/list.html`、`reports/monthly.html` 為其他 agent 內容） |
| `remotes/origin/agent/reasonix-maintenance-review-02` | `f37dc01` | **Docs only** | ✅ 僅 coordination + reports，無 code |

### 3.2 需人工重做（base 過舊）

| Branch | Reason |
|--------|--------|
| `remotes/origin/agent/mimo-ui-regression-02` | base 為 Phase 1 前，diff 大量負數（移除已存在的 main 內容）。不可直接 cherry-pick。 |
| `remotes/origin/agent/reasonix-review-02` | 同上，base 過舊。 |
| `remotes/origin/agent/reasonix-phase2-contract-notes-01` | 同上。 |

### 3.3 應放棄的項目

- **無**。所有 backlog 缺口仍是有效需求。

---

## 4. 建議順序與 Owner

### Step 1 — 低風險整併（Codex 或 open）

| 項目 | 方法 | 建議 owner | 風險 |
|------|------|-----------|------|
| T3.1–T3.3 (delete CRUD) | Cherry-pick `d8639ec`（需篩選檔案） | Codex | LOW |
| T5.1 (property filter) | Cherry-pick `d8639ec`（同上） | Codex | LOW |
| reasonix-maintenance-review-02 docs | Cherry-pick `f37dc01` | Codex | LOW |
| 清理過時 branch | 通知各 agent owner | Codex | LOW |

### Step 2 — 中等風險（open 或 box）

| 項目 | 方法 | 建議 owner | 依賴 |
|------|------|-----------|------|
| T4.1 (nested property) | 從零實作 | open 或 box | 無 |
| T4.2 (nested room) | 從零實作 | open 或 box | 無 |
| T5.4 (reading log) | 從零實作 | open 或 box | 無 |
| T6.3 (PaymentRecords API) | 從零實作 | open 或 box | 已有 service/repo |

### Step 3 — 延後到 Phase 2 尾聲或 Phase 3

| 項目 | 原因 |
|------|------|
| T5.2 (property new-bill) | 需要 post flow 穩定 |
| T5.3 (quick-reading) | UX convenience |
| T6.1–T6.2, T6.4–T6.6 (integrations) | 外部依賴 |
| T7.1–T7.2 (error pages + water preview) | 不影響核心功能 |

---

## 5. 依賴關係圖

```
T1 (billing core) ──[✅ main]──┐
                                ├── T2 (post bridge) ──[✅ main]
                                │
T3 (delete CRUD) ──[❌ branch]──┤
T5.1 (filter) ────[❌ branch]──┤
T4 (nested) ──────[❌ not started]
T5.2-5.4 (detail) ─[❌ not started]
T6 (integrations) ─[❌ not started]
T7 (polish) ───────[❌ not started]
```

無互鎖阻塞。T3、T5.1 可獨立 cherry-pick。

---

## 6. Summary Statistics

| Metric | Value |
|--------|-------|
| 原始缺口總數 | 22 |
| 已進 main | 6 (T1 all 4 + T2 both 2) |
| 僅在 branch | 4 (T3 all 3 + T5.1) |
| 完全未開始 | 12 |
| 可直接 cherry-pick 的 branch | 2 (`open-low-risk-crud-02`, `reasonix-maintenance-review-02`) |
| 需人工重做的 branch | 3 (`mimo-ui-regression-02`, `reasonix-review-02`, `reasonix-phase2-contract-notes-01`) |

---

*End of report — no models touched, no data contracts modified, no billing core re-examined.*
