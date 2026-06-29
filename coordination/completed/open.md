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

## 2026-06-29 (Session 3)

### Completed: Low-Risk CRUD Round 2
- Branch: `agent/open-low-risk-crud-02`
- Task card: `in_progress/2026-06-29_phase2_open_low-risk-crud-01.md`

### T3.1 — Delete landlord
- Route: `POST /landlords/<id>/delete`
- Safety check: refuses if landlord has properties
- Template: delete button added to `landlords/list.html`

### T3.2 — Delete tenant
- Route: `POST /tenants/<id>/delete`
- Safety check: refuses if tenant has contracts
- Template: delete button added to `tenants/list.html`

### T3.3 — Delete water bill
- Route: `POST /water/<id>/delete`
- Direct delete (no dependent records)
- Template: delete button added to `water/list.html`

### T5.1 — Electricity property filter
- Route: `GET /electricity/property/<id>/bills`
- Template: `electricity/property_bills.html`
- Links from electricity dashboard for property drill-down

### Files Modified
- `app/modules/landlords/routes.py` — add delete route
- `app/modules/tenants/routes.py` — add delete route
- `app/modules/water/routes.py` — add delete route
- `app/modules/electricity/routes.py` — add property filter route
- `app/services/landlord_service.py` — add `delete_landlord`
- `app/services/tenant_service.py` — add `delete_tenant`
- `app/services/water_service.py` — add `delete_water_bill`
- `app/repositories/landlord_repository.py` — add `delete`
- `app/repositories/tenant_repository.py` — add `delete`
- `app/repositories/water_repository.py` — add `delete`
- `app/repositories/electricity_repository.py` — add `list_by_property`
- `app/templates/landlords/list.html` — add delete button
- `app/templates/tenants/list.html` — add delete button
- `app/templates/water/list.html` — add delete button
- `app/templates/electricity/property_bills.html` — new template
- `tests/integration/test_low_risk_crud.py` — 5 tests

### Verification
- `pytest tests/integration -q` → 34 passed, 15 skipped (no regressions)
- All 5 new tests pass
- Routes registered and returning correct status codes

### Backlog Items Closed
- T3.1 (delete landlord) — ✅
- T3.2 (delete tenant) — ✅
- T3.3 (delete water bill) — ✅
- T5.1 (electricity property filter) — ✅
