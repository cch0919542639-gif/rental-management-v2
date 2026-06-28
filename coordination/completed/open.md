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
