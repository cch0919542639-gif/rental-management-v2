# mimo 任務書

## 角色

UI 欄位盤點、驗證情境、回歸清單主責。

## 先讀

- `../architecture/rewrite-roadmap.md`
- `../architecture/target-structure.md`
- `../operations/agent-work-rules.md`
- `../reports/reporting-contract-template.md`

## 你現在要先做

1. 定義新版每個頁面的欄位來源
2. 建立關鍵流程測試情境
3. 整理手工驗收與回歸檢查表

## 你的必交文件

- `docs/reports/mimo-ui-field-matrix.md`
- `docs/reports/mimo-test-scenarios.md`
- `evidence/mimo-regression-checklist.md`

## 輸出模板

- `docs/reports/mimo-ui-field-matrix-template.md`
- `docs/reports/mimo-test-scenarios-template.md`
- `docs/reports/mimo-regression-checklist-template.md`

要求：

- 頁面欄位、測試情境、回歸清單都依模板輸出
- 風險分級統一用 `P0/P1/P2`

## 記錄要求

- 開工前更新 `coordination/progress/mimo.md`
- 每完成一份驗證文件，更新 `coordination/completed/mimo.md`
- 若發現畫面欄位找不到唯一來源，立即開 incident
