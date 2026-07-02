# Utility Policy Minimum Schema Plan

Date: 2026-07-03
Owner: Codex
Status: Implementation planning draft

## Purpose

這份文件把 `utility billing policy` 拆成三個落地層級：

1. 現有 schema 可直接承接
2. 第二批水電匯入前一定要補的最小欄位
3. 可延後到 Phase 3+ 的 custom module

依據：

- [utility-billing-policy-draft.md](D:/CodexRuntime/rental/rebuild/docs/operations/utility-billing-policy-draft.md)
- [open-utility-policy-mapping-01.md](D:/CodexRuntime/rental/rebuild/docs/reports/open-utility-policy-mapping-01.md)

## Current State Audit

目前主幹已存在的相關欄位：

- `landlords.electricity_rate_type`
- `landlords.electricity_rate`
- `landlords.water_rate_type`
- `landlords.water_rate`
- `properties.electricity_meter_type`
- `properties.water_meter_type`
- `properties.billing_rule`
- `contracts.electricity_rate`
- `contracts.water_rate`
- `electricity_bills.calc_method_id`
- `calc_methods`

目前缺口：

- 沒有正式的 `property-level utility policy enum`
- 沒有 `room-level override`
- 沒有 `contract-level override enum`
- 沒有 `public_electricity allocation mode`
- 沒有 `custom strategy code` 可承接 `single_meter_proportional / ct_meter_proportional / dual_meter_tou`

## Classification Outcome

### Batch 1 — Existing Schema Can Cover

可先靠現有 schema 承接，不需要新欄位：

- `electricity_fixed_rate`
- `water_free`

原因：

- 電費固定單價可先用 `landlords.electricity_rate_type='fixed'` + `landlords.electricity_rate`
- 合約個別例外可先用 `contracts.electricity_rate`
- 水費免費可先用 `landlords.water_rate_type='fixed'` + `water_rate=0`

對應物件：

- 電費固定單價：6 個物件（11, 13-16, 22）
- 水費免費：13 個物件

### Batch 2 — Needs Minimum Enum / Config

第二批水電匯入前最少要支援：

- `electricity_bill_usage_ratio`
- `electricity_bill_usage_ratio_plus_public_share`
- `water_bill_by_stay_days`

原因：

- 這些不是單一數值欄位可表達
- 匯入後若沒有 strategy code，系統無法正確重算或編輯

對應物件：

- 電費比例分攤：1, 2, 3, 4, 6, 21
- 電費含公電：5
- 水費按居住天數：1-10, 20, 22

### Batch 3+ — Needs Custom Module

下列策略不能只靠最小 enum 完成：

- `single_meter_proportional`
- `ct_meter_proportional`
- `dual_meter_tou`

對應物件：

- 7, 8, 9, 10

先 defer，不阻擋核心資料與 Batch 2 一般案例。

## Minimum Schema Proposal

### Property-level defaults

在 `properties` 增加：

- `electricity_policy_code` `String(50)` nullable
- `water_policy_code` `String(50)` nullable

用途：

- 記錄物件預設策略
- 大多數案例都在這層解決

允許值：

- `electricity_fixed_rate`
- `electricity_bill_usage_ratio`
- `electricity_bill_usage_ratio_plus_public_share`
- `water_fixed_monthly`
- `water_free`
- `water_bill_by_stay_days`
- `custom_single_meter_proportional`
- `custom_ct_meter_proportional`
- `custom_dual_meter_tou`

### Room-level override

在 `rooms` 增加：

- `electricity_policy_code` `String(50)` nullable
- `water_policy_code` `String(50)` nullable

用途：

- 承接少數房間例外
- 已知案例：Property 20 / Room 432

### Contract-level override

暫不新增 enum 欄位。

理由：

- open 報告確認 ~200 份舊合約全部 `electricity_rate=NULL`、`water_rate=NULL`
- 舊系統沒有 contract-level strategy override 的實證
- 第一輪只保留既有 `contracts.electricity_rate / water_rate` 作為固定費率覆蓋值

若未來出現明確 contract-level strategy，再補欄位。

## Minimum Config Proposal

### Keep

保留現有欄位：

- `landlords.electricity_rate_type`
- `landlords.electricity_rate`
- `landlords.water_rate_type`
- `landlords.water_rate`
- `contracts.electricity_rate`
- `contracts.water_rate`

### Re-interpretation

- `landlords.*rate*`：
  只作為 `fixed` 類策略的預設參數
- `contracts.*rate*`：
  只作為固定費率 override，不代表完整策略
- `properties.billing_rule`：
  暫不當正式 enum，視為 legacy/free-text 欄位

## Service Layer Changes Needed

最小服務變更：

1. 新增 `UtilityPolicyResolver`
   - resolve property default
   - apply room override
   - fallback to fixed-rate compatibility path

2. 調整 `RatePolicyService`
   - 目前只會回傳單一 rate
   - 需限制在 `fixed` 類策略才使用

3. ElectricityService / WaterService
   - 第二批才接正式策略分派
   - 第一批不動核心演算法

## Migration Scope

### Safe in next round

- 新增 `properties.electricity_policy_code`
- 新增 `properties.water_policy_code`
- 新增 `rooms.electricity_policy_code`
- 新增 `rooms.water_policy_code`

### Not yet

- 不改 `contracts` schema
- 不改 `monthly_bills` schema
- 不刪除 `billing_rule`
- 不刪除 `calc_methods`

## Recommended Batch Plan

### Round 1

- 凍結 enum 名稱
- 加 4 個 policy_code 欄位
- 寫 migration
- 只做 property default + room override 骨架

### Round 2

- 匯入 1st/2nd batch 可判定的物件策略
- fixed / ratio / ratio+public / water_free / stay_days

### Round 3

- 針對 7, 8, 9, 10 做 custom module
- 處理 12, 17-20, 23-25 的 manual cases

## Decision

最小可行方案是：

- **新增 4 個 policy_code 欄位**
- **不新增 contract-level strategy 欄位**
- **固定費率仍沿用現有 rate 欄位**
- **custom module 延後**

這樣可以讓：

- 第一批核心資料繼續前進
- 第二批一般水電資料有落點
- 複雜舊案不會阻擋主幹
