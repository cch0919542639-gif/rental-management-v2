# reasonix 任務書

## 角色

架構決策與資料契約主責。

## 先讀

- `../architecture/rewrite-roadmap.md`
- `../architecture/target-structure.md`
- `../operations/agent-work-rules.md`

## 你現在要先做

1. 在 `data_contracts/` 建立核心表契約初稿
2. 在 `docs/reports/` 或 `evidence/` 建立依賴圖與狀態機說明
3. 判斷新版是否保留現有 DB schema 還是需要 migration-first

## 你的必交文件

- `data_contracts/core-entities.md`
- `data_contracts/billing-contract.md`
- `data_contracts/status-machines.md`
- `docs/reports/reasonix-architecture-decision.md`

## 輸出模板

- `docs/reports/reasonix-architecture-decision-template.md`
- `docs/reports/reasonix-data-contract-audit-template.md`
- `docs/reports/reasonix-dependency-map-template.md`

要求：

- 優先直接依模板產出，不要自行改格式
- 若需要增章節，可追加，但不要刪核心段落

## 記錄要求

- 開工前更新 `coordination/progress/reasonix.md`
- 每完成一份契約或決策文件，更新 `coordination/completed/reasonix.md`
- 若出現契約衝突，立即新增 incident 檔
