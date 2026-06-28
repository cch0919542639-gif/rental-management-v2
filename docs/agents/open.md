# open 任務書

## 角色

快速掃描、清單化、低風險整理主責。

## 先讀

- `../architecture/rewrite-roadmap.md`
- `../architecture/target-structure.md`
- `../operations/agent-work-rules.md`

## 你現在要先做

1. 盤點舊系統 route、template、table、script
2. 把可以轉成正式模組的功能列清楚
3. 把危險殘骸與死碼候選列出

## 你的必交文件

- `docs/reports/open-route-template-matrix.md`
- `docs/reports/open-schema-inventory.md`
- `docs/reports/open-cleanup-candidates.md`

## 輸出模板

- `docs/reports/open-route-template-matrix-template.md`
- `docs/reports/open-schema-inventory-template.md`
- `docs/reports/open-cleanup-candidates-template.md`
- `docs/reports/open-module-mapping-template.md`

要求：

- 優先直接依模板產出，不要自創欄位
- 風險分級統一用 `P0/P1/P2`

## 記錄要求

- 開工前更新 `coordination/progress/open.md`
- 每完成一張盤點清單，更新 `coordination/completed/open.md`
- 若發現舊案與新契約矛盾，立即開 incident
