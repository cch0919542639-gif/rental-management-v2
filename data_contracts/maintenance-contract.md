# Maintenance Contract

## Scope

- `MaintenanceRequest`
- 維修狀態機
- 維修與 `Room` / `Contract` 的邊界

## Purpose

新版 `maintenance` 模組負責承載「待修 / 維修中 / 已修復」等語義，避免再把這些狀態塞進：

- `Room.status`
- `Tenant.name`
- `Contract.status`

## Formal Entity

`MaintenanceRequest`

正式欄位：

- `id`
- `room_id`
- `status`
- `issue_category`
- `priority`
- `title`
- `description`
- `reported_by_name`
- `reported_at`
- `assigned_to_name`
- `started_at`
- `resolved_at`
- `closed_at`
- `estimated_cost`
- `actual_cost`
- `notes`
- `created_at`
- `updated_at`

## Minimum Schema Rules

- `room_id` 不可為空，必須 FK 指向 `rooms.id`
- `status` 不可為空
- `title` 不可為空
- `reported_at` 建議預設為建立時間
- `estimated_cost` / `actual_cost` 不可為負值

## Recommended Enums

### `status`

- `reported`
- `assigned`
- `in_progress`
- `resolved`
- `closed`
- `cancelled`

### `issue_category`

- `electricity`
- `water`
- `facility`
- `cleaning`
- `appliance`
- `other`

### `priority`

- `low`
- `medium`
- `high`
- `urgent`

## State Machine

建議轉換：

- `reported -> assigned`
- `assigned -> in_progress`
- `in_progress -> resolved`
- `resolved -> closed`
- `reported -> cancelled`
- `assigned -> cancelled`

限制：

- 不可從 `closed` 回到 `in_progress`
- 不可從 `cancelled` 回到 `reported`
- 若需要重新處理，應建立新 request 或顯式 reopen ADR

## Room / Contract Boundary

### `Room.status`

- 仍只允許：
- `vacant`
- `occupied`

- `maintenance` 狀態不得污染 `Room.status`

### `Contract.status`

- 不因 maintenance 直接改變
- 若維修影響入住/退租，應由業務流程另外決定

## UI / Workflow Expectations

第一版最小流程：

1. 建立維修單
2. 指派處理人
3. 開始施工
4. 標記已解決
5. 關單

第一版不做：

- 附件 / 照片上傳
- 定期保養排程
- LINE / OCR / 外部整合
- 多房間合併工單

## Query Expectations

第一版至少應支援：

- 依房間查詢 maintenance list
- 依 `status` 過濾
- 依 `priority` 過濾
- 查詢 open requests（`reported` / `assigned` / `in_progress`）

## Reporting Rules

- 報表若顯示房間維修狀態，來源必須來自 `MaintenanceRequest`
- 不可再依 `tenant.name` 或 `Room.status` 補推維修狀態

## Migration Guidance

- 舊資料若有 `tenant.name = 待修`，不得直接搬成 tenant
- 需在 migration 階段轉成：
- 正常 `Room.status`
- 獨立 `MaintenanceRequest`

## Not In This Round

- reopen workflow
- SLA / due date
- vendor management
- invoice attachment
