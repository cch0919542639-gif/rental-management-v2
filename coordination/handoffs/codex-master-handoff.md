# Handoff: codex -> codex/next-session

Timestamp: 2026-06-28 11:20

## Context

- Phase 0 全部完成，結論已凍結於 reasonix / open / mimo / box 文件
- 目前進入 Phase 1，採 `Parallel Rebuild`
- 新版實作根目錄：`D:\CodexRuntime\rental\rebuild\app`

## Work Already Done

- 完成 core skeleton：
- `app_factory`、`config`、`db`、`errors`、`logging`、`security`、`year_month`
- 完成 models skeleton：
- `User`、`Landlord`、`Property`、`Room`、`Tenant`、`Contract`
- `MonthlyBill`、`PaymentRecord`、`WaterBill`
- `CalcMethod`、`ElectricityMeter`、`ElectricityBill`、`ElectricityReading`
- 完成 modules skeleton：
- `auth`
- `dashboard`
- `billing`
- `rooms`
- `contracts`
- `tenants`
- `properties`
- 已完成最小流程驗證，主幹可啟動並跑基本 CRUD

## Files To Read First

- `D:\CodexRuntime\rental\rebuild\docs\operations\phase1-master-status.md`
- `D:\CodexRuntime\rental\rebuild\coordination\progress\codex.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-architecture-decision.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\open-module-mapping.md`

## Risks

- `payments`、`electricity`、`water` 尚未完成，實作時不得自行發明新資料契約
- `year_month` 必須維持 DB `YYYYMM`、UI/API `YYYY-MM`
- 付款流程只能走 `PaymentRecord`，不得回引舊 `/payment/*` 死碼
- Room occupancy 只能靠 `Room.status` + `Contract.status`，禁止虛擬 tenant 名稱

## Exact Next Step

- 先做 `landlords` 最小 CRUD
- 接著做 `payments` 最小列表/建立/狀態更新骨架
- 完成後補 smoke test 與 phase1 status 更新
