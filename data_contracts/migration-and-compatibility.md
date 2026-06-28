# Migration And Compatibility Contract

## 目標

定義新版與舊版資料相容、遷移與回滾原則。

## 基本策略

- 優先保留既有商業資料
- 先建立相容層，再逐步清理歷史異常
- 每個 migration 都必須可驗證、可回滾、可重跑或具備冪等策略

## 第一批遷移議題

### 1. `user` / `users` 雙表

- 需要決定正式來源表
- 需要比對筆數、欄位與實際引用

### 2. `MonthlyBill.year_month`

- 舊 DB 已用 `YYYYMM`
- 舊 ORM 註解與 UI 輸入為 `YYYY-MM`
- 新版需保留 DB `YYYYMM`，建立統一 helper

### 3. 虛擬 tenant 名稱

- 需盤點 `空房`、`待修`、`待補` 等資料
- 新版不可再依賴此種資料表示 occupancy

### 4. 付款流程雙軌

- 需釐清 `PaymentRecord` 與未完成 `Payment` 路徑
- 新版只保留單一路徑

## Migration 交付要求

每支 migration / repair script 都必須記錄：

- 輸入資料
- 目標輸出
- 驗證方式
- 回滾方式
- 風險說明

## 相容層原則

- UI 與 API 可短期接受 `YYYY-MM`
- repository 寫入 DB 時統一轉成 `YYYYMM`
- 不允許多個層級各自轉換

## Incident 觸發條件

發現以下狀況必須立即開 incident：

- 遷移後可能覆寫原始資料
- 無法唯一決定正式來源表
- 舊資料與契約衝突且無法自動修復
