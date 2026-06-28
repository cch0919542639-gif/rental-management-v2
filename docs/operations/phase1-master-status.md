# Phase 1 Master Status

Last Updated: 2026-06-29 00:18
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
- `landlords`
- `payments`
- `electricity`
- `water`
- `reports`
- `maintenance`

## Verified Flows

- 未登入保護正常
- `auth/login` 可登入
- `dashboard` 可載入 summary
- `billing` 可依月份顯示帳單
- `billing` 可建立、編輯、切換已繳、依合約產生、批次產生月帳單
- `rooms` 可建立
- `contracts` 可建立與終止，且會同步 `Room.status`
- `properties` 可建立與列表
- `tenants` 可建立與列表
- `landlords` 可建立、編輯與列表
- `payments` 可建立、驗證、駁回、連結帳單
- `electricity` 可建立電表、電費單、抄表、標記 calculated、回寫月帳單
- `water` 可建立水費單、編輯、以 shared / independent 模式回寫月帳單
- `reports` 可查看月報表、房東彙總、年度總覽
- `maintenance` 已建立模組入口與邊界頁，但正式資料 schema 尚未凍結
- `tests` 已有 16 passed / 7 skipped 的 integration coverage
- `scripts/seed_demo_data.py` 可建立 demo data
- `docs/operations/dev-runbook.md` 已提供其他電腦接手流程
- `scripts/run_smoke_tests.ps1` 可直接執行 smoke tests

## Not Yet Implemented

- 本機最新主幹尚未 push 到 GitHub
- deeper algorithm 與正式 maintenance schema
- migration 與正式資料導入

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
