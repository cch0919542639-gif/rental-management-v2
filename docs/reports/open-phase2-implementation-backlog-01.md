# Phase 2 Implementation Backlog — Gap-to-Task Breakdown

Author: open
Branch: `agent/open-phase2-implementation-backlog-01`
Date: 2026-06-28
Based on: `open-phase2-gap-audit-02.md`

---

## 0. Overview

此 backlog 將 gap audit 中的 22 個缺口、2 個 blocking dependency、1 個 incident 整理成可派發的 task packet。

**核心原則：**
- 不碰 billing create/generate 主幹實作（由 Codex 主控）
- 不修改資料契約 / `app/models`
- 不自行實作第二套 billing/payment 流程
- 每個 task 標註 owner 建議、依賴關係、風險級別、是否需要 Codex 主控

---

## 1. 分類框架

| Tier | Category | Count | Risk | Dependency |
|------|----------|-------|------|------------|
| **T1** | Billing create/generate (Codex 主控) | 4 items | HIGH | 無 upstream，但 blocking T2 |
| **T2** | Post-to-monthly bridge (electricity/water) | 2 items | HIGH | Blocked by T1 |
| **T3** | Low-risk CRUD 補齊 | 3 items | LOW | 無 |
| **T4** | Nested creation routes | 2 items | MEDIUM | 無 |
| **T5** | Electricity property-specific detail | 4 items | MEDIUM | 建議等 T1 完成後 |
| **T6** | Integrations 前置工作 | 6 items | LOW-MEDIUM | 獨立 |
| **T7** | Phase 3 延期 | 2 items | LOW | 無 |

---

## 2. T1 — Billing Create/Generate（Codex 主控，本次不碰）

| ID | Gap | Route | Risk | Owner | Note |
|----|-----|-------|------|-------|------|
| T1.1 | 批次產生月帳單 | `POST /billing/generate` | **HIGH** | **Codex** | Core monthly workflow — 所有 active contract 批次產生 MonthlyBill |
| T1.2 | 手動建立月帳單 | `GET,POST /billing/create` | **HIGH** | **Codex** | 單一 contract 手動建立 MonthlyBill |
| T1.3 | 編輯月帳單 (含 total recalc) | `GET,POST /billing/<id>/edit` | **HIGH** | **Codex** | 月帳單欄位編輯 + `calculate_total` 回寫 |
| T1.4 | 批次輸入 (multi-contract) | `GET,POST /bill/batch_entry` | **HIGH** | **Codex** | 舊有 batch_entry flow，目前無對應 |

**依賴：** 無 upstream dependency（但為 T2 之前置條件）
**檔案範圍：** `app/modules/billing/routes.py` + `forms.py` + `services/billing_service.py`（新增 method）
**禁止：** 不可改 `MonthlyBill` model、不可改 data contract
**風險：** 若 T1 未完成，electricity/water post flow **完全無法運作**

---

## 3. T2 — Post-to-Monthly Bridge（Blocked by T1）

| ID | Gap | Current Behavior | Risk | Owner | Note |
|----|-----|------------------|------|-------|------|
| T2.1 | `electricity/bills/<id>/post` 無法取得有效 `monthly_bill_id` | route 存在但 form 無有效 MonthlyBill 可選 | **HIGH** | open / box | 需要 T1 完成後才能測試 |
| T2.2 | `water/<id>/post` 同 electricity 問題 | route 存在但相同 blocking | **HIGH** | open / box | 同上 |

**依賴：** Blocked by T1.all
**風險：** 現有 route 已實作、service 已實作，僅 missing MonthlyBill。T1 完成後可立即驗證。
**建議：** 在 T1 完成後，open 或 box 補 2 支 integration test 驗證 post flow。

---

## 4. T3 — Low-Risk Delete CRUD（可立即開發）

| ID | Gap | Route | Risk | Owner | File Pattern | 舊有範例 |
|----|-----|-------|------|-------|-------------|----------|
| T3.1 | 刪除房東 | `POST /landlords/<id>/delete` | **LOW** | open 或 box | `landlords/routes.py` + `landlords/` services | `landlords/<id>/delete` → redirect |
| T3.2 | 刪除承租人 | `POST /tenants/<id>/delete` | **LOW** | open 或 box | `tenants/routes.py` + services | `tenants/<id>/delete` → redirect |
| T3.3 | 刪除水費單 | `POST /water/bills/<id>/delete` | **LOW** | open 或 box | `water/routes.py` + services | `water/bills/<id>/delete` → redirect |

**依賴：** 無
**注意事項：**
- 若 data contract 設計為 soft-delete / archived，需先確認業務邏輯
- 模組已有相同風格的 CRUD route，可複製 pattern
- 建議新增 delete button 到對應 list/detail template

---

## 5. T4 — Nested Creation Routes（UX 改善，Medium Risk）

| ID | Gap | Route | Risk | Owner | Note |
|----|-----|-------|------|-------|------|
| T4.1 | 在房東頁面下直接新增物業 | `GET,POST /landlords/<lid>/properties/create` | **MEDIUM** | mimo 或 open | parent-context creation shortcut |
| T4.2 | 在物業頁面下直接新增房間 | `GET,POST /properties/<pid>/rooms/create` | **MEDIUM** | mimo 或 open | 同上 |

**依賴：** 無（需確認 `properties/create` 和 `rooms/create` 現有 route 是否可 reuse form）
**風險：** UI 層級調整，不影響資料完整性
**建議：** mimo 主導 template UI，open 或 box 補 route

---

## 6. T5 — Electricity Property-Specific Detail（可先準備，建議等 T1）

| ID | Gap | Route | Risk | Owner | Note |
|----|-----|-------|------|-------|------|
| T5.1 | 依物業篩選電費單 | `GET /electricity/property/<id>/bills` | **MEDIUM** | open 或 box | Filter by property |
| T5.2 | 物業級電費單建立 | `GET,POST /electricity/property/<id>/new-bill` | **MEDIUM** | open 或 box | Property-scoped bill creation |
| T5.3 | 快速抄表 | `GET,POST /electricity/property/<id>/quick-reading` | **LOW** | mimo 或 box | Fast meter reading UX |
| T5.4 | 抄表歷史 | `GET /electricity/property/<id>/reading-log` | **LOW** | mimo 或 box | Reading history display |

**依賴：** T5.2 之 post flow 需要 T1（MonthlyBill 存在）
**建議排列：** T5.1 (獨立，可先做) → T5.4 (獨立，可先做) → T5.3 (獨立，可先做) → T5.2 (建議等 T1)

---

## 7. T6 — Integrations 前置工作（獨立，不阻塞核心）

| ID | Gap | Route | Risk | Owner | Note |
|----|-----|-------|------|-------|------|
| T6.1 | LINE Bot Webhook | `POST /callback` | **LOW** | box | External webhook — 需 infra 設定 |
| T6.2 | OCR 收據分析 API | `POST /api/analyze-receipt` | **MEDIUM** | Codex 或 reasonix | 需要 OCR engine 整合 |
| T6.3 | PaymentRecords API | `GET,POST /api/payment-records` | **LOW** | open 或 box | API variant（UI 已存在） |
| T6.4 | OCR + payment 分析 | `POST /api/payment-records/<id>/analyze` | **LOW** | Codex 或 reasonix | Receipt-to-payment |
| T6.5 | OCR 電費單 | `POST /api/electricity/create-from-ocr` | **LOW** | Codex | OCR → electricity bill |
| T6.6 | Google Sheets 匯入 | `GET,POST /sheets/import` | **LOW** | box | Data import pipeline |

**依賴：** 無（但 OCR engine 需要 `app/integrations/` 目錄擴充）
**風險：** LINE webhook 與 Sheets import 外部依賴，若無實際使用需求可延後
**建議：** T6.3 可優先做（已有對應 service/repository）；T6.1/T6.6 可等 Phase 2 尾聲

---

## 8. T7 — 延期到 Phase 3

| ID | Gap | Route | Risk | Owner | Note |
|----|-----|-------|------|-------|------|
| T7.1 | 錯誤頁面 HTML template | `error/404.html` `error/500.html` | **LOW** | mimo | 目前僅回傳 JSON/text |
| T7.2 | 水費預覽 | `POST /water/preview` | **LOW** | mimo 或 box | UX convenience — 可等正式水費流程穩定後 |

**理由：** 不影響核心功能；可在 Phase 2 尾聲或 Phase 3 一次性補齊。

---

## 9. Incidents 摘要

| Incident | File | Status | 影響 |
|----------|------|--------|------|
| Billing Cycle Block | `coordination/incidents/2026-06-28_1545_open_billing-cycle-block.md` | **OPEN** | Blocking T2、影響 electricity/water post flow |

**無需新增 incident** — 本次 backlog 為 planning 層級，不涉及衝突改動。

---

## 10. Task Board 派發建議

### Phase 2.1 — Codex 主控 (先決條件)

| Task | Backlog File | 建議移至 |
|------|-------------|----------|
| T1.1-T1.4 Billing create/generate/batch | `ready/2026-06-28_P2_codex_billing-create-generate.md` | `ready/` |
| 驗收與 troubleshooting | — | `review/` → `done/` |

### Phase 2.2 — Parallel (T1 完成後即可啟動)

| Task | Owner | 建議移至 |
|------|-------|----------|
| T2.1-T2.2 驗證 electricity/water post flow | open + box | `ready/` |
| T3.1-T3.3 Delete CRUD | open | `ready/` |
| T4.1-T4.2 Nested creation routes | mimo + open | `ready/` |

### Phase 2.3 — 獨立開發 (可先行)

| Task | Owner | 建議移至 |
|------|-------|----------|
| T5.1, T5.4 Electricity property filter + reading log | open / box | `ready/` |
| T6.3 PaymentRecords API | open / box | `ready/` |

### Phase 2.4 — 尾聲或 Phase 3

| Task | Owner | 建議移至 |
|------|-------|----------|
| T5.2 Electricity property new bill | open / box | `backlog/` |
| T5.3 Quick reading | mimo / box | `backlog/` |
| T6.1, T6.2, T6.4-T6.6 Integrations | Codex / box | `backlog/` |
| T7.1-T7.2 Error pages + water preview | mimo | `backlog/` (Phase 3) |

---

## 11. 風險矩陣

| Risk | Items | Impact | Mitigation |
|------|-------|--------|-----------|
| T1 延遲 | T2 完全阻塞 | 高 — electricity/water post flow 無法運作 | Codex 優先處理 T1 |
| T3 soft-delete 語意不清 | 刪除後資料不一致 | 中 — 需確認 data contract 是否允許 hard delete | 開發前由 reasonix 確認 |
| T4 nested creation 影響現有 route | route 衝突 | 低 — parent-context route 為獨立 blueprint | 確認現有 route registration order |
| T6 OCR engine 未選定 | API 無法實作 | 中 — 須先決定 OCR 方案 | 延後到 Phase 2.4 或 Phase 3 |

---

## 12. 不屬於本次 backlog 的事項

- ❌ 修改 `MonthlyBill` model — 資料契約已凍結
- ❌ 修改 `app/models` 任何檔案
- ❌ 自行實作第二套 billing/payment 流程
- ❌ 修改 `app/core/year_month.py` — year_month 格式統一邏輯
- ❌ 修改 `WaterService` / `ElectricityService` post flow 簽章
- ❌ `maintenance` 正式 schema（Phase 0 reasonix 已凍結，待 Phase 3）

---

## Appendix A: 舊系統 Route 對照摘要

（完整對照表見 `docs/reports/open-phase2-gap-audit-02.md` §3）

| Category | Old Route | New Route | Tier |
|----------|-----------|-----------|------|
| Delete | `landlords/<id>/delete` | ❌ missing | T3 |
| Delete | `tenants/<id>/delete` | ❌ missing | T3 |
| Delete | `water/bills/<id>/delete` | ❌ missing | T3 |
| Nested | `landlords/<lid>/properties/create` | ❌ missing | T4 |
| Nested | `properties/<pid>/rooms/create` | ❌ missing | T4 |
| Contract billing | `contracts/<cid>/bills` | ❌ missing | T1 |
| Contract billing | `contracts/<cid>/bills/create` | ❌ missing | T1 |
| Batch billing | `bill/batch_entry` | ❌ missing | T1 |
| Generate | `bills/generate` | ❌ missing | T1 |
| Toggle paid | `bills/<id>/toggle_paid` | ❌ missing | T1 |
| Bill edit | `bills/<id>/edit` (implied) | ❌ missing | T1 |
| Electric detail | `electricity/property/<id>/bills` | ❌ missing | T5 |
| Electric detail | `electricity/property/<id>/new-bill` | ❌ missing | T5 |
| Electric detail | `electricity/property/<id>/quick-reading` | ❌ missing | T5 |
| Electric detail | `electricity/property/<id>/reading-log` | ❌ missing | T5 |
| Water preview | `water/preview` | ❌ missing | T7 |
| Integrations | `/api/analyze-receipt` | ❌ missing | T6 |
| Integrations | `/api/payment-records` | ❌ missing | T6 |
| Integrations | `/api/payment-records/<id>/analyze` | ❌ missing | T6 |
| Integrations | `/api/electricity/create-from-ocr` | ❌ missing | T6 |
| Integrations | `/callback` | ❌ missing | T6 |
| Integrations | `/sheets/import` | ❌ missing | T6 |
| Error pages | `error/404.html`, `error/500.html` | ❌ missing | T7 |

---

*End of report — all Phase 2 items classified, no billing core touched, no model modified.*
