# Maintenance Schema And Flow Design

Date: 2026-06-29
Owner: Codex
Status: design ready

## Goal

在不污染 `Room.status`、`Tenant.name`、`Contract.status` 的前提下，定義 `maintenance` 模組的正式 schema 與最小可運行流程。

## Design Decision

採用：

- **獨立 `MaintenanceRequest` 表**
- 以 `room_id` FK 連到 `rooms`

不採用：

- 在 `rooms` 表加 `maintenance_status`
- 以虛擬 tenant 名稱表示待修

## Why This Design

理由：

- 符合 Phase 0 決策
- 不污染主資料
- 可擴充為多筆維修歷史
- 可獨立查 open / closed requests

## Minimum Schema

建議正式欄位如下：

| Field | Type | Required | Note |
|------|------|----------|------|
| `id` | int PK | yes | |
| `room_id` | FK rooms.id | yes | 房間主關聯 |
| `status` | varchar(20) | yes | `reported/assigned/in_progress/resolved/closed/cancelled` |
| `issue_category` | varchar(20) | no | 分類 |
| `priority` | varchar(20) | no | `low/medium/high/urgent` |
| `title` | varchar(200) | yes | 簡短標題 |
| `description` | text | no | 問題描述 |
| `reported_by_name` | varchar(100) | no | 通報人 |
| `reported_at` | datetime | yes | 預設 now |
| `assigned_to_name` | varchar(100) | no | 處理人 |
| `started_at` | datetime | no | 開始施工 |
| `resolved_at` | datetime | no | 技術解決時間 |
| `closed_at` | datetime | no | 結案時間 |
| `estimated_cost` | numeric(10,2) | no | 預估成本 |
| `actual_cost` | numeric(10,2) | no | 實際成本 |
| `notes` | text | no | 補充說明 |
| `created_at` | datetime | yes | |
| `updated_at` | datetime | yes | |

## Minimum Indexes

- `idx_maintenance_room_id`
- `idx_maintenance_status`
- `idx_maintenance_priority`
- `idx_maintenance_reported_at`

## State Machine

```text
reported -> assigned -> in_progress -> resolved -> closed
reported -> cancelled
assigned -> cancelled
```

不允許：

- `closed -> in_progress`
- `cancelled -> reported`

## Minimum Flow

### Flow 1: Report

- 使用者選房間
- 輸入標題 / 描述 / priority
- 建立 `status=reported`

### Flow 2: Assign

- 管理者填 `assigned_to_name`
- 狀態改為 `assigned`

### Flow 3: Start Work

- 狀態改為 `in_progress`
- 寫入 `started_at`

### Flow 4: Resolve

- 狀態改為 `resolved`
- 寫入 `resolved_at`
- 可寫 `actual_cost`

### Flow 5: Close

- 狀態改為 `closed`
- 寫入 `closed_at`

## Out Of Scope

- 附件/照片
- 外部廠商
- SLA
- 通知系統
- recurring maintenance

## Suggested Phase Split

### Phase 2A

- model
- repository
- service
- list/create/detail/update status

### Phase 2B

- filters
- report integration
- cost summary

### Phase 3

- attachments
- reminders
- vendors

## Implementation Notes

- `maintenance` 第一輪應由 Codex 主控
- 若進 code，需新增：
- model
- repository
- service
- forms
- routes
- templates
- tests

## Dependencies

- `data_contracts/maintenance-contract.md`
- `docs/reports/reasonix-phase2-contract-notes-01.md`
