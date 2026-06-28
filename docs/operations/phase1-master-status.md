# Phase 1 Master Status

Last Updated: 2026-06-28 11:20
Owner: Codex

## Purpose

這份文件是 Phase 1 的主控恢復入口。若對話、agent 或服務中斷，請先讀這份，再接著讀 `coordination/progress/codex.md`。

## Frozen Decisions

- Rebuild 策略：`Parallel Rebuild`
- `year_month`：DB `YYYYMM`，UI/API `YYYY-MM`
- 正式 user 表：`user`
- 正式付款流程：`PaymentRecord`
- 空房/待修不可用虛擬 tenant 名稱表示

## Implemented Now

- Core
- `app/core/config`
- `app/core/db`
- `app/core/errors`
- `app/core/logging`
- `app/core/security`
- `app/core/year_month.py`
- Models
- `user`
- `landlords`
- `properties`
- `rooms`
- `tenants`
- `contracts`
- `monthly_bills`
- `payment_records`
- `water_bills`
- `calc_methods`
- `electricity_meters`
- `electricity_bills`
- `electricity_readings`
- Modules
- `auth`
- `dashboard`
- `billing`
- `rooms`
- `contracts`
- `tenants`
- `properties`

## Verified Flows

- 未登入保護正常
- `auth/login` 可登入
- `dashboard` 可載入 summary
- `billing` 可依月份顯示帳單
- `rooms` 可建立
- `contracts` 可建立與終止，且會同步 `Room.status`
- `properties` 可建立與列表
- `tenants` 可建立與列表

## Not Yet Implemented

- `landlords` module
- `payments` module
- `electricity` module
- `water` module
- `maintenance` module
- 報表與匯出
- migration / seed / smoke test 腳本正式化

## Recommended Work Split

- Codex：主幹模組實作與整合
- reasonix：規格審查與 decision guardrail
- open：`landlords`、`payments` 或其他 route-heavy 模組
- mimo：UI field alignment、template 回歸、手動驗收證據
- box：smoke tests、runbook、低風險腳本與文件

## Crash Recovery Procedure

1. 先讀本檔確認目前 Phase 1 進度。
2. 讀 `coordination/progress/codex.md` 看主控中的工作與下一步。
3. 讀 `coordination/progress/*.md` 檢查各 agent 最後狀態。
4. 若有異常或中斷，讀 `coordination/incidents/`。
5. 開工前再讀相關 module 的 README 與 Phase 0 凍結文件。

## Recovery Confidence

- 目前已具備可恢復主控紀錄
- 即使對話中斷，也可從以上三層文件恢復：
- Phase status
- Codex 主控進度
- 各 agent 個別進度
