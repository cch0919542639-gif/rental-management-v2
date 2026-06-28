# 新版目錄結構草案

```text
rebuild/
  README.md
  docs/
    architecture/
      rewrite-roadmap.md
      target-structure.md
    agents/
      reasonix.md
      open.md
      mimo.md
      box.md
    operations/
      agent-work-rules.md
      progress-template.md
      completed-template.md
      incident-template.md
      handoff-template.md
    reports/
      reporting-contract-template.md
  coordination/
    progress/
    completed/
    incidents/
    handoffs/
  app/
    core/
    models/
    modules/
    services/
    repositories/
    templates/
    static/
    integrations/
    migrations/
  tests/
    unit/
    integration/
    e2e/
  scripts/
    repair/
    migration/
  data_contracts/
  evidence/
```

## 結構原則

- `docs/`
  - 規格、路線、操作規則，只寫人類與 agent 要讀的說明
- `coordination/`
  - 工作記錄與即時回報中心
- `app/`
  - 新版正式程式碼
- `tests/`
  - 單元、整合、端對端
- `scripts/`
  - 正式維修與遷移腳本，不再散落 `fix_*`、`check_*`
- `data_contracts/`
  - 表結構、欄位定義、狀態機、相容策略
- `evidence/`
  - 驗證結果、對帳證據、手工測試記錄

## app 模組切分建議

- `core/`
  - app factory、config、db、auth、exceptions、logging
- `models/`
  - ORM model 與 schema 定義
- `modules/`
  - `auth/`
  - `landlords/`
  - `properties/`
  - `rooms/`
  - `tenants/`
  - `contracts/`
  - `billing/`
  - `electricity/`
  - `water/`
  - `payments/`
  - `reports/`
- `services/`
  - 計費、對帳、報表彙總、資料驗證
- `repositories/`
  - 集中查詢與資料存取
- `integrations/`
  - line、ocr、sheet import 等外部整合

## 交付規則

- 文件先進 `docs/` 或 `coordination/`
- 可執行實作才進 `app/`、`tests/`、`scripts/`
- 每個模組在開工前先有 README 或任務單
