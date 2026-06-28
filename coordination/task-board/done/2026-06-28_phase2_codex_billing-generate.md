# Title

Phase 2 Billing Generate Baseline

## Owner

Codex

## Phase

Phase 2

## Goal

補 `billing create / generate / batch` 最小可運行主幹，解除 electricity / water post 對既有 MonthlyBill 的 blocking 依賴。

## Allowed Files

- `app/modules/billing/*`
- `app/services/*`
- `app/repositories/*`
- `app/templates/billing/*`
- `tests/integration/*`
- `docs/operations/phase1-master-status.md`
- `coordination/progress/codex.md`

## Do Not Touch

- `data_contracts/*`
- `maintenance` schema
- integrations

## Acceptance

- 可建立單筆 `MonthlyBill`
- 可依 contract + month 產生帳單
- 至少一個 batch generate 入口
- smoke/integration tests 通過

## Dependencies

- `open-phase2-gap-audit-02.md`

## Status

DONE
