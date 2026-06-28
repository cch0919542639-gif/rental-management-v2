# Branch 命名規則 + PR 流程

Last Updated: 2026-06-28

## Main Branches

- `main`
- 穩定主幹，只接受已審查完成的合併

- `phase1/core-codex`
- 主控施工線，用於主幹整合與高衝突區收斂

## Agent Branch Naming

格式：

`agent/<agent-name>-<task>-<round>`

範例：

- `agent/reasonix-review-01`
- `agent/open-landlords-payments-01`
- `agent/mimo-ui-gap-01`
- `agent/box-smoke-docs-01`

若是人類協作者，可用：

`user/<name>-<task>-<round>`

範例：

- `user/alice-payments-ui-01`
- `user/bob-test-fixes-01`

## Branch Creation Rule

1. 先讀 `docs/operations/phase1-master-status.md`
2. 確認自己負責範圍沒有被別人占用
3. 更新自己的 `coordination/progress/<agent>.md`
4. 再建立 branch 開工

## PR Target Rule

- 一般 agent branch 預設 PR 到 `phase1/core-codex`
- 由主控整合完成後，再從 `phase1/core-codex` 合回 `main`
- `main` 不接受未整合完成的直接 PR

## PR Title Format

格式：

`[<agent>] <scope>: <short-summary>`

範例：

- `[open] payments: add minimal list and create flow`
- `[mimo] rooms-ui: align form fields with contracts`
- `[box] tests: add smoke coverage for auth and billing`

## PR Checklist

每個 PR 都必須回答：

1. 這次改動的邊界是什麼
2. 依據哪份文件施工
3. 如何驗證
4. 尚未完成什麼
5. 有沒有碰到高風險區

## Merge Order

建議順序：

1. `reasonix` review / risk note
2. `open` 模組骨架
3. `mimo` UI 對齊
4. `box` tests / docs / scripts
5. `Codex` 做最終整合

## Conflict Handling

若發現 merge conflict：

1. 不要直接覆蓋對方修改
2. 先讀對方 branch 的任務範圍與工作紀錄
3. 若屬契約衝突，先寫 incident
4. 若只是模板或文件小衝突，由主控整合

## Minimum Definition Of Done

符合以下條件才可送 PR：

- 任務範圍清楚
- 工作紀錄已更新
- 至少完成一個可驗證的子成果
- 沒有自行新增未核准的資料契約
- 已寫清楚 remaining work
