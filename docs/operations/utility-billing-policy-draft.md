# Utility Billing Policy Draft

Date: 2026-07-03
Owner: Codex
Status: Draft for implementation planning

## Purpose

這份文件把舊系統的水電計算規則轉成新版主幹可實作的策略模型。  
目標不是立刻重寫全部演算法，而是先凍結：

- 允許的計算方式
- 套用層級
- 必要參數
- 匯入時該如何保存設定

## Scope

本文件涵蓋：

- 電費策略
- 水費策略
- 預設套用規則
- 匯入時的最低保存要求

本文件不涵蓋：

- 正式 DB schema 變更
- UI 設定頁最終樣式
- 全部歷史資料回補腳本

## Policy Hierarchy

策略套用優先順序：

1. `contract` override
2. `room` override
3. `property` default
4. 系統 fallback

說明：

- 同一個物件通常共用同一策略
- 少數房間例外時，允許房間或合約覆蓋
- 若沒有任何覆蓋，則吃物件預設

## Electricity Policies

### 1. `electricity_fixed_rate`

- 適用情境：固定每度單價，例如 `5` 或 `6`
- 必要參數：
  - `rate`
- 公式：
  - `room_usage * rate`

### 2. `electricity_bill_usage_ratio`

- 適用情境：整期電費按房客用電度數比例分攤
- 必要參數：
  - `bill_total_amount`
  - `total_tenant_usage`
  - `room_usage`
- 公式：
  - `(bill_total_amount / total_tenant_usage) * room_usage`

### 3. `electricity_bill_usage_ratio_plus_public_share`

- 適用情境：有大樓公電，需先均攤公電，再分攤房內電費
- 必要參數：
  - `bill_total_amount`
  - `public_electricity_amount`
  - `total_tenant_usage`
  - `active_contract_room_count`
  - `room_usage`
- 公式：
  - `(public_electricity_amount / active_contract_room_count) + ((bill_total_amount - public_electricity_amount) / total_tenant_usage) * room_usage`

## Water Policies

### 1. `water_fixed_monthly`

- 適用情境：固定每月金額，例如 `100`
- 必要參數：
  - `fixed_amount`

### 2. `water_free`

- 適用情境：不收水費
- 必要參數：無
- 結果：
  - `0`

### 3. `water_bill_by_stay_days`

- 適用情境：整期水費按居住天數分攤
- 必要參數：
  - `bill_total_amount`
  - `total_stay_days`
  - `contract_stay_days`
- 公式：
  - `(bill_total_amount / total_stay_days) * contract_stay_days`

## Import Rules

### Core Rule

匯入時不要強迫把所有策略壓平成單一 `rate` 數值。

### First-Batch Allowed

第一批核心資料匯入可接受：

- 固定電費單價
- 固定水費月費
- 免費水費
- 其餘策略先記錄在 mapping / exception report

### Second-Batch Required

第二批水電匯入前，至少要能記錄：

- strategy code
- fixed rate / fixed amount（若策略需要）
- 是否有 public electricity
- property default
- room / contract override

## UI / Ops Requirements

至少要支援這些操作：

1. 以 `property` 套用預設策略
2. 以 `room` 覆蓋少數例外
3. 顯示該房當前策略來源：
   - contract override
   - room override
   - property default
4. 匯入報告需列出無法自動判定策略的物件/房間

## Risks

1. 若把動態分攤策略錯當固定單價，帳單會整批算錯
2. 若忽略公電均攤，電費會系統性低估
3. 若水費按居住天數分攤沒有正確取期間，結果會偏差
4. 若策略只設在物件層，少數例外房間會被覆寫錯

## Recommended Next Step

1. 先讓 `open` 或 `Codex` 整理舊系統實際有哪些策略樣本
2. 凍結策略 enum 名稱
3. 再做 schema / settings / UI 設計
4. 最後才做正式水電歷史資料匯入
