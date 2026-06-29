# Phase 2 Branch Merge Closeout

Author: open
Date: 2026-06-29
Baseline: `codex-phase2-mainline-01`

---

## 1. Executive Summary

Phase 2 的 branch 整併階段正式結束。

經過三輪盤點（reconcile-03 → merge-plan-04 → closeout-05），結論一致且明確：**`codex-phase2-mainline-01` 已吸收全部 12 個 agent branch 的核心功能。** 沒有任何 branch 還包含主幹尚未具備的關鍵代碼。

Phase 2 不再以 branch 整併為主工作軸。後續開發應直接以 `codex-phase2-mainline-01` 為基底進行。

---

## 2. 已完成吸收的核心能力

以下功能原散落在各 agent branch，現已全數整合進 `codex-phase2-mainline-01`：

| 能力 | 來源 Agent | Routes / 檔案 |
|------|-----------|---------------|
| Billing create/edit/toggle-paid | Codex | `/billing/create`, `/billing/<id>/edit`, `/billing/<id>/toggle-paid` |
| Batch / per-contract generate | Codex | `/billing/batch`, `/billing/contracts/<id>/generate` |
| Per-contract bill list | Codex | `/billing/contracts/<id>` |
| Electricity meter/bill/reading CRUD | Codex | `/electricity/meters/*`, `/electricity/bills/*` |
| Electricity calculate + post-to-monthly | Codex | `/electricity/bills/<id>/calculate`, `/electricity/bills/<id>/post` |
| Water bill CRUD + post | Codex | `/water/create`, `/water/<id>/edit`, `/water/<id>/post` |
| Reports monthly / yearly / landlord summary | Codex | `/reports/monthly`, `/reports/yearly`, `/reports/landlord-summary` |
| Delete landlord / tenant / water bill | open | `/landlords/<id>/delete`, `/tenants/<id>/delete`, `/water/<id>/delete` |
| Electricity property filter | open | `/electricity/property/<id>/bills` |
| Maintenance create/edit/transition | Codex | `/maintenance/create`, `/maintenance/<id>/edit`, `/maintenance/<id>/transition/*` |
| Maintenance model / contract | reasonix | `app/models/maintenance.py`, `data_contracts/maintenance-contract.md` |
| UI field alignment + template fixes | mimo | `app/templates/payments/list.html`, `app/templates/reports/monthly.html` 等 |
| Integration smoke / coverage tests | box | `tests/integration/test_*.py`（共 16 支） |
| Demo seed / runbook / smoke scripts | box + Codex | `scripts/*`, `docs/operations/*` |

---

## 3. 可放棄 branch 清單

以下 12 個 branch 經確認無殘餘核心功能價值。其中 9 個 diff 全為負數（base 過舊，欲刪除 mainline 已加功能），3 個僅有已過時或被取代的協作文件：

### 3.1 完全無殘值（9 branch）

| Branch | 原因 |
|--------|------|
| `agent/mimo-ui-regression-03` | base 為 Phase 1 前主幹，diff 全負 |
| `agent/box-tests-runbook-04` | 同上 |
| `agent/box-phase2-tests-runbook-01` | 同上 |
| `agent/box-test-runbook-02` | 同上 |
| `agent/box-tests-runbook-03` | 同上 |
| `agent/mimo-phase2-ui-gap-01` | 同上 |
| `agent/reasonix-phase2-contract-notes-01` | 同上 |
| `agent/open-gap-audit-02` | 已被 03/04/05 取代 |
| `agent/open-phase2-implementation-backlog-01` | 已被 03/04/05 取代 |

### 3.2 協作文件可選擇性吸收（3 branch）

以下 3 個 branch 的**代碼已全部過時**，但其報告文件對後續開發仍有參考價值：

| Branch | 可選檔案 | 主題 |
|--------|---------|------|
| `agent/open-low-risk-crud-02` | `tests/integration/test_low_risk_crud.py` | Delete + filter 整合測試 |
| `agent/open-low-risk-crud-02` | `app/templates/electricity/property_bills.html` | Property filter 專用模板（vs 共用模板二選一） |
| `agent/open-low-risk-crud-02` | `docs/reports/open-low-risk-crud-round2.md` | 實作記錄 |
| `agent/reasonix-maintenance-review-02` | `docs/reports/reasonix-maintenance-review-02.md` | 維護契約審查 |
| `agent/reasonix-maintenance-migration-guard-03` | `docs/reports/reasonix-maintenance-migration-guard-03.md` | Migration guard 分析 |
| `agent/mimo-ui-polish-02` | `docs/reports/mimo-ui-polish-02.md` | UI polish 記錄 |

這些檔案**不是必整併項目**，僅在後續開發過程中按需 cherry-pick。

---

## 4. 為什麼後續應 direct-on-mainline

1. **Branch 基礎已全面過時。** 12 個 branch 全部 base 在 Phase 1 的 `main`（或更舊），而非 `codex-phase2-mainline-01`。從這些 branch cherry-pick 需要逐檔比對，成本高於直接在主幹撰寫新功能。

2. **Mainline 已包含所有 agent 交付。** Billing core、delete CRUD、property filter、maintenance routes、UI fixes、tests — 全部已在主幹。不需要再從 branch 搬運核心功能。

3. **剩餘缺口不依賴 branch 內容。** Phase 2 未完成的 T4（nested creation）、T5.2–5.4（electricity detail）、T6（integrations）、T7（polish）均可直接在主幹上開發，無需參考舊 branch。

4. **協作流程簡化。** Agent 交付應以 `codex-phase2-mainline-01` 為基底開新 branch，完成後直接 PR 進主幹，不再經過多人 branch 相互 cherry-pick。

---

## 5. 建議後續工作模式

```
Phase 2 之前：main ← agent/A ← agent/B ← agent/C  (branch 散落)
Phase 2 之後：codex-phase2-mainline-01 ← agent/D (PR) ← agent/E (PR)
```

- 所有新 branch 一律以 `codex-phase2-mainline-01` 為 base
- 交付完成後直接開 PR 合併回主幹
- 已過時的 agent branch 可擇期刪除（`git branch -d` + GitHub delete）

---

## 6. 剩餘 Phase 2 缺口摘要（僅列項，不盤點）

| Tier | 項目 | 建議階段 |
|------|------|---------|
| T4 | Nested creation routes | Phase 2 可繼續 |
| T5.2–5.4 | Electricity property detail | Phase 2 可繼續 |
| T6 | Integrations (6 項) | Phase 2 尾聲或 Phase 3 |
| T7 | Error pages + water preview | Phase 3 |

---

## 7. 文件記錄

| 報告 | 日期 | 主題 |
|------|------|------|
| `open-phase2-gap-audit-02.md` | 06-28 | 原始缺口盤點（22 項） |
| `open-phase2-implementation-backlog-01.md` | 06-28 | backlog 分類（7 Tier） |
| `open-phase2-main-gap-reconcile-03.md` | 06-29 | 以 `main` 為基準核對 |
| `open-phase2-mainline-merge-plan-04.md` | 06-29 | 以 `codex-phase2-mainline-01` 為基準核對 12 branch |
| **`open-phase2-merge-closeout-05.md`** | **06-29** | **Phase 2 branch 整併正式結案** |

---

*End of closeout — no code modified, no models touched, no data contracts changed, no new gap inventory performed.*
