# Phase 2 Gap Recheck — Round 6

Author: open
Date: 2026-06-29
Baseline: `codex-phase2-mainline-01` (HEAD)
Previous: `open-phase2-merge-closeout-05.md`
Tests: `38 passed, 15 skipped`

---

## 1. Executive Summary

自 closeout-05 以來，Codex 已補回大量先前未進主幹的功能。本報告以 `codex-phase2-mainline-01` 最新 HEAD 為準，重新盤點 Phase 2 尚未落地的缺口。

**關鍵變化：**
- `nested creation`、`maintenance Phase 2B`、`electricity property detail / new-bill / quick-reading / reading-log` — **已全數進主幹**（closeout-05 時標為未開始）
- Phase 2 落地的功能比例從 closeout-05 的約 60% 提升到約 **90%**
- 剩餘缺口集中在 3 個領域：integrations、error pages、migration entry points

---

## 2. 已完成項目 vs 尚未完成項目

### 2.1 自 closeout-05 後新增進主幹的項目

| 領域 | 項目 | Routes / 說明 |
|------|------|---------------|
| Nested creation | 房東下新增物業 | `GET,POST /properties/landlord/<id>/create` |
| Nested creation | 物業下新增房間 | `GET,POST /rooms/property/<id>/create` |
| Maintenance 2B | Open list | `GET /maintenance/open` |
| Maintenance 2B | Room-scoped list | `GET /maintenance/rooms/<room_id>` |
| Maintenance 2B | Maintenance report | `GET,POST /reports/maintenance` |
| Maintenance 2B | Legacy scan script | `scripts/migration/maintenance_legacy_scan.py` |
| Electricity detail | Property overview | `GET /electricity/property/<id>` |
| Electricity detail | Property new bill | `GET,POST /electricity/property/<id>/new-bill` |
| Electricity detail | Quick reading | `GET,POST /electricity/property/<id>/quick-reading` |
| Electricity detail | Reading log | `GET /electricity/property/<id>/reading-log` |

### 2.2 仍不在主幹的項目

| 領域 | 項目 | 目前狀態 |
|------|------|---------|
| **Integrations** | route placeholder / service boundary / API | 僅 `app/integrations/README.md`，無 route 無 service |
| **Error pages** | 404 / 500 HTML templates | 完全不存在（目前僅回傳 JSON/text） |
| **Migration** | 正式 migration entry point | `scripts/migration/` 僅有 `maintenance_legacy_scan.py` + README |
| **Water preview** | `POST /water/preview` | 不存在 |
| **API variants** | `/api/*` routes | 完全不存在 |

---

## 3. 尚未完成缺口分級

| 優先序 | 領域 | 項目 | 風險 | 工作量估計 | 依賴 |
|--------|------|------|------|-----------|------|
| **P1** | Error pages | 404/500 HTML templates | LOW | 2 templates, < 50 行 | 無 |
| **P2** | Integrations | LINE webhook placeholder | LOW | 1 route + 1 service stub | 需 infra 設定 |
| **P2** | Integrations | API payment-records | LOW | 1 route (service/repo 已存在) | 無 |
| **P2** | Integrations | OCR receipt analyze placeholder | MEDIUM | 1 route stub | 需 OCR engine 決定 |
| **P3** | Migration | docs / runbook entry point | LOW | 文件更新 | 需先確認 migration scope |
| **P3** | Water preview | `POST /water/preview` | LOW | 1 route + 1 template | 無 |
| **P3** | Integrations | Google Sheets import | LOW | 1 route stub | 外部依賴 |
| **P3** | Integrations | OCR electricity bill | LOW | 1 route stub | 需 OCR engine |

---

## 4. 可直接由 Codex 主幹實作的項目

以下項目**無需 agent branch，可直接在 `codex-phase2-mainline-01` 上實作**：

| 項目 | 實作方式 | 預估工時 |
|------|---------|---------|
| 404/500 HTML templates | 新增 `app/templates/errors/404.html`、`500.html` + 更新 error handlers | 30 min |
| Water preview route | 新增 `POST /water/preview` route + `water/bill_result.html` template | 30 min |
| PaymentRecords API | 新增 `/api/payment-records` GET/POST route（reuse existing service/repo） | 30 min |
| LINE webhook placeholder | 新增 `POST /callback` route 回傳 200 | 15 min |

以上 4 項為純新增檔案，不修改現有 model/service/repository。

---

## 5. 可再分派給其他 agent 的項目

| 項目 | 建議 agent | 前提 |
|------|-----------|------|
| 404/500 HTML templates | **mimo**（UI 擅長） | 無 |
| Water preview template + route | **mimo** 或 **box** | 無 |
| Migration docs / runbook entry | **box**（runbook 擅長） | 需 Codex 確認 migration scope |
| Integration tests 補強 | **box** | 無 |
| API payment-records tests | **box** | route 完成後 |

---

## 6. 依賴關係圖

```
codex-phase2-mainline-01 (目前)
│
├── P1: error pages ───── 無依賴，可直接做
├── P2: integrations ──── 部分需外部 infra 決定
├── P2: API variants ──── 無依賴 (service/repo 已就位)
├── P3: migration docs ── 需先確認 scope
└── P3: water preview ─── 無依賴
```

無互鎖阻塞。P1 和部分 P2 可立即進行。

---

## 7. Summary Statistics

| Metric | Value |
|--------|-------|
| closeout-05 時未進主幹的項目 | 9 (T4x2 + T5x3 + T6x6 - T5.1 - T6.3) |
| 本次確認已新進主幹 | 8 (nested x2 + maintenance 2B x4 + electricity detail x4 - 共同項) |
| 本次確認仍不在主幹 | 8 (見 §2.2 + §3) |
| 其中 P1（可直接做） | 1 (error pages) |
| 其中 P2（可做但有外部依賴） | 3 (integrations routes) |
| 其中 P3（可延後） | 4 (migration docs + water preview + OCR/sheets) |

---

## 8. 與 closeout-05 的差異說明

closeout-05 基於較舊的 `codex-phase2-mainline-01` HEAD。本次 recheck 確認：
- T4 (nested creation) — 已從 ❌ 未開始 → ✅ 進主幹
- T5.2–5.4 (electricity detail) — 已從 ❌ 未開始 → ✅ 進主幹
- maintenance Phase 2B (filters / open list / room list / report) — 新確認已進主幹
- 測試數從 34 passed → 38 passed

Phase 2 已完成度從約 60% 提升到約 90%。

---

*End of report — no models touched, no data contracts modified, no formula rewritten.*
