# Incident: Billing Cycle Block — No Route to Create MonthlyBill

Date: 2026-06-28 15:45
Author: open (gap-audit-02)
Severity: BLOCKING (Phase 2 entry)

## Discovery Context

Gap audit cross-referencing old route matrix with current GitHub `origin/main` implementation.

## Description

`billing/` module (5 files: `__init__.py`, `routes.py`, `forms.py`, `services/billing_service.py`, `repositories/billing_repository.py`) 目前只有 **唯讀的 list 功能**：

- `routes.py` — 僅 `billing_list()` (GET)
- `forms.py` — 僅有 `BillingFilterForm`
- `billing_service.py` — 僅 `calculate_total()` (static)
- `billing_repository.py` — 有 `list_all()`, `list_for_contract()`, `get_or_404()`, `sum_total_for_month()`, `list_for_month()`

但 `electricity` 與 `water` 模組的 post flow 都**依賴已存在的 MonthlyBill**：

- `electricity/bills/<id>/post` → `ElectricityService.post_reading_to_monthly_bill(monthly_bill_id=form.monthly_bill_id.data, ...)`
- `water/<id>/post` → `WaterService.post_shared_to_monthly_bill(monthly_bill_id=form.monthly_bill_id.data, ...)` 或 `post_independent_to_monthly_bill(monthly_bill_id=..., amount=...)`

**沒有任何 route 可以建立 MonthlyBill** → `form.monthly_bill_id.data` 永遠無法取得有效值。

## Impact

| Affected Module | Route | Impact |
|----------------|-------|--------|
| electricity | `POST /electricity/bills/<id>/post` | Cannot complete — no MonthlyBill to post to |
| water | `POST /water/<id>/post` | Cannot complete — same issue |
| billing | `GET /billing/` | List works, but no create/edit/generate |

## Required Actions (Phase 2)

1. 在 `billing/routes.py` 新增以下 routes（依優先序）：
   - `POST /billing/generate` — 批次產生所有 active contract 的月帳單
   - `GET /billing/create` + `POST` — 手動建立單一月帳單
   - `GET /billing/<id>/edit` + `POST` — 編輯月帳單
2. 在 `billing/forms.py` 新增對應 form class
3. 在 `billing_service.py` 新增 `generate_monthly_bills()` 與 `create_monthly_bill()` method

## What NOT to Do

- 不可修改 `MonthlyBill` model（data_contract 已凍結）
- 不可修改 `WaterService` / `ElectricityService` 的 post flow 簽章
- 不可自行新增第二套 payment 流程
- 不可修改 `year_month` 格式統一邏輯 (`core/year_month.py`)

## Resolution

To be resolved in Phase 2. This is the single highest-priority gap from the audit.
