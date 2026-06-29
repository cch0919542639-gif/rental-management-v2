# open Completed Log

## 2026-06-28

### Completed: Route Template Matrix
- Output: `docs/reports/open-route-template-matrix.md`
- Scope: 全部 route（app.py 35 routes + electricity_bp 6 routes + water_bill 4 routes + landlord_report 1 route + 2 error handlers）
- 標記 5 個 Payment 死碼 route (P0)
- 標記所有 template 對應、missing/orphaned templates
- 記錄 year_month 格式不一致、meter_id 硬編碼等高風險發現

### Completed: Schema Inventory
- Output: `docs/reports/open-schema-inventory.md`
- Scope: 全部 16 個資料表，雙表衝突，欄位不一致，格式差異
- 以 reasonix data-contract-audit 為基礎補充舊系統實際結構
- 列出 cleanup priority 排序

### Completed: Cleanup Candidates
- Output: `docs/reports/open-cleanup-candidates.md`
- Scope: 52 個外部腳本分類（archive / convert / dead code / low-risk fix）
- 發現 landlord_report.py Blueprint 從未被任何 app variant 註冊（新發現，非 reasonix 已知）

### Completed: Module Mapping
- Output: `docs/reports/open-module-mapping.md`
- Scope: 舊功能全部映射到新版 11 個 modules + core + services + repositories + integrations
- 列出 6 大 cross-module tangle（含雙向耦合、公式散落、year_month 格式脫鉤）
- 給出 5 項 suggested first moves

### Verification
- 所有資料以 reasonix 三份報告為最終依據，無自創規則
- 舊系統實際結構與 reasonix 結論一致，無矛盾
- 發現 1 項新資訊（landlord_report.py 未註冊）已記錄於 cleanup-candidates 報告

### Not Completed / Handoff
- 無未完成事項
- 可交接對象：mimo（參考 module mapping 開始建 modules）、box（參考 schema inventory 開始 migration scripts）

## 2026-06-28 (Session 2)

### Completed: Phase 2 Implementation Backlog
- Output: `docs/reports/open-phase2-implementation-backlog-01.md`
- Branch: `agent/open-phase2-implementation-backlog-01`
- Scope: 將 gap audit 中 22 個缺口 + 2 個 blocking dependency 拆成 7 個 Tier（T1-T7）
- 明確標註：
  - T1 (Codex 主控): billing create/generate — 不碰主幹，僅文件描述
  - T2: post-to-monthly bridge (blocked by T1)
  - T3: low-risk delete CRUD (可立即開發)
  - T4: nested creation routes
  - T5: electricity property detail
  - T6: integrations 前置工作
  - T7: 延期到 Phase 3
- 所有項目標註 owner 建議、依賴關係、風險級別、是否需要 Codex 主控

### Updated: Progress tracking
- `coordination/progress/open.md` → 更新為 IN_PROGRESS，記錄 backlog 工作
- Task board 派發建議已內嵌於 backlog 報告 §10

### Verification
- 未修改任何 `app/models` 檔案
- 未觸及 billing create/generate 主幹程式碼
- 未修改資料契約
- 未自行實作第二套 billing/payment 流程

### Not Completed / Handoff
- T1 (billing create/generate) 需 Codex 主控接手
- T2 (post-to-monthly bridge) 待 T1 完成後方可驗證

## 2026-06-29 (Session 8)

### Completed: Phase 3 Kickoff Gap Check
- Output: `docs/reports/open-phase3-kickoff-gap-check-01.md`
- Baseline: `codex-phase2-mainline-01` HEAD
- Scope: water preview / payment API / migration write path 前置盤點

### Key Findings
- Water preview ✅ complete（`/water/<id>/preview` route + service + template + test）
- Payment API service/repo 已就緒，唯一缺口為薄 route 層（`/api/payment-records`）
- Migration write path 尚未正式啟動，建議 Phase 3 先補 convention + scaffold
- 46 passed / 15 skipped
- 無 blocking gap，無需 incident

### Verification
- 未修改任何 `app/models`、資料契約、核心公式

## 2026-06-29 (Session 7)

### Completed: Integrations Gap Check (Round 7)
- Output: `docs/reports/open-phase2-integrations-gap-check-07.md`
- Baseline: `codex-phase2-mainline-01` HEAD
- Scope: 僅盤點 `app/integrations/`、相關 route、docs、runbook

### Key Findings
- OCR/sheets interfaces ✅、LINE webhook placeholder ✅、error pages ✅、migration entry ✅、repair scripts ✅
- 44 passed / 15 skipped
- 剩餘 6 項均符合 Phase 2 defer rule，不阻擋結案
- 無 blocking gap，無需 incident

### Verification
- 未修改任何 `app/models` 檔案
- 未觸及 billing/payments/maintenance 主流程
- 未修改資料契約

## 2026-06-29 (Session 6)

### Completed: Phase 2 Gap Recheck (Round 6)
- Output: `docs/reports/open-phase2-gap-recheck-06.md`
- Baseline: `codex-phase2-mainline-01` HEAD
- Scope: 以最新主幹重新盤點 Phase 2 尚未落地的缺口

### Key Findings vs closeout-05
- `nested creation`、`maintenance Phase 2B`、`electricity detail/new-bill/quick-reading/reading-log` — 已全數進主幹
- Phase 2 完成度從約 60% → 約 90%
- 剩餘缺口：error pages (P1)、integrations (P2)、migration docs (P3)、water preview (P3)

### Verification
- 未修改任何 `app/models` 檔案
- 未觸及 billing/payments/maintenance 主流程
- 未修改資料契約

### open Phase 2 Deliverables (complete)
1. `open-route-template-matrix.md` — 舊系統 route 矩陣
2. `open-schema-inventory.md` — schema 盤點
3. `open-cleanup-candidates.md` — 清理候選
4. `open-module-mapping.md` — 模組映射
5. `open-phase2-gap-audit-02.md` — 缺口審計
6. `open-phase2-implementation-backlog-01.md` — backlog 分類
7. `open-low-risk-crud-round2.md` — 低風險 CRUD 實作
8. `open-phase2-main-gap-reconcile-03.md` — 主幹核對
9. `open-phase2-mainline-merge-plan-04.md` — 整併計畫
10. `open-phase2-merge-closeout-05.md` — 正式結案
11. `open-phase2-gap-recheck-06.md` — **最終缺口重檢**
