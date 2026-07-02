# Real Data Manual Fields Checklist

Date: 2026-07-02
Owner: Codex
Status: Draft gate document

## Purpose

這份文件把真實資料匯入前必須人工確認的欄位集中成單一清單。  
來源依據：

- `open-real-data-mapping-01` 摘要：共有 16 個人工確認欄位（M1-M16）
- `reasonix-real-data-import-guard-01` 摘要：需先處理 `user/users`、`year_month`、`Room.status`、虛擬 tenant 污染
- `mimo-real-data-regression-checklist-01`：匯入後驗收頁面與數值核對矩陣

## Usage Rule

- 沒有完成本表的欄位，不可直接執行正式 `--execute` 匯入。
- 本表完成後，才可進入 [real-data-import-gate-checklist.md](D:/CodexRuntime/rental/rebuild/docs/operations/real-data-import-gate-checklist.md) 的 Gate B。
- 若某欄位最終決定「允許先空值」，必須在「處理決議」欄明確記錄。

## Decision Legend

- `REQUIRED`：未確認不得匯入
- `ALLOW_EMPTY`：可先匯入空值，但需有後補計畫
- `MAP_DEFAULT`：可用固定 mapping 或預設值匯入
- `MANUAL_POST`：不在本輪自動匯入，改人工建立或匯入後補登

## Manual Fields Register

| ID | Priority | Target Table | Column / Topic | Why Manual Review Is Needed | Source Needed | Decision | Owner | Notes |
|---|---|---|---|---|---|---|---|---|
| M1 | P0 | `landlords` | 待補明細 | open 對映報告未併入主幹，需補逐欄名稱 | 業務資料 / 舊系統 | REQUIRED | Business | 待從原始報告回填 |
| M2 | P0 | `properties` | 待補明細 | 同上 | 業務資料 / 舊系統 | REQUIRED | Business | 待回填 |
| M3 | P0 | `rooms` | `status` 相關人工語義 | 只允許 `vacant` / `occupied` | 舊系統 + 業務確認 | REQUIRED | Business + Codex | 非法值不得直接入庫 |
| M4 | P0 | `tenants` | 虛擬 tenant 判定 | `空房/待修/待補/倉庫/鐵皮` 禁止直接作為正式 tenant | 舊系統 + 業務確認 | REQUIRED | Business + Codex | 需改走 maintenance / room cleanup |
| M5 | P0 | `contracts` | `status` mapping | 過期 / 非正式狀態值需先 mapping | 舊系統 + 業務確認 | REQUIRED | Business + Codex | 不可產生重複 active |
| M6 | P0 | `monthly_bills` | `year_month` 格式 | 必須全部是 `YYYYMM` 且非 NULL | CSV / DB audit | REQUIRED | Codex | 先跑 `year_month_audit.py` |
| M7 | P0 | `monthly_bills` | 極端值風險 `R06` | 已知存在 `-33646` 極端值，需查是否髒資料 | 月報 CSV / Google Sheet | REQUIRED | Business + Codex | 未釐清不得匯入該筆 |
| M8 | P1 | `monthly_bills` | 其他費用描述 / 金額語義 | 需確認 `other_charges` / `other_desc` 的來源欄位 | 月報 CSV | REQUIRED | Business | 影響帳單總額與月報 |
| M9 | P1 | `electricity_bills` | 歷史帳單期間與月份對應 | 需確認 `period_end` / `year_month` 對齊 | 電費資料 / PDF | REQUIRED | Business | Phase 2 水電批次 |
| M10 | P1 | `electricity_readings` | 抄表來源可信度 | 需確認抄表來源是否完整 | PDF / OCR / 舊系統 | ALLOW_EMPTY | Business | 可延後，先不匯空表以外內容 |
| M11 | P1 | `water_bills` | 分攤模式語義 | `shared_by_stay_days` / `independent_meter` 需人工判定 | 水費資料 | REQUIRED | Business | Phase 2 水費匯入前完成 |
| M12 | P1 | `payment_records` | 是否建立歷史付款 | PaymentRecord 可不匯；若匯需對齊 transaction 資訊 | 舊系統 / 銀行資料 | MANUAL_POST | Business | 可延後，非首批 blocker |
| M13 | P1 | `maintenance_requests` | 舊待修資料承接 | 舊資料需從虛擬 tenant / room status 轉承接，不可直接寫 tenant | 舊系統 + 業務確認 | MANUAL_POST | Business + Codex | 需另走 maintenance migration |
| M14 | P2 | `user` | 正式帳號來源 | `user/users` 未合併前禁止自動匯入 | 舊系統 DB audit | REQUIRED | Business + Codex | 先跑 `user_table_audit.py` |
| M15 | P2 | `calc_methods` | 水費計算方法對照 | 若舊系統未明確記錄，需人工指定預設 | 水費規則 | MAP_DEFAULT | Business | 可用正式 enum 預設 |
| M16 | P2 | Cross-cutting | Google Sheet / 月報 CSV 差異處理 | 同一欄位若多來源不一致，需指定主來源 | Sheet + CSV + 舊系統 | REQUIRED | Business | 匯入前決定 source of truth |

## Immediate Pre-Import Questions

以下 6 題必須在正式匯入前被填完：

1. `R06` 極端值 `-33646` 是資料錯誤、沖銷、還是公式轉置錯？
2. 舊系統中的 `待修` 是要轉成 `MaintenanceRequest`，還是僅做歷史標記？
3. `user` 與 `users` 何者才是正式資料來源？
4. 首批匯入是否只做核心資料，不帶 `payment_records` / `maintenance_requests`？
5. 水費模式若舊資料沒有明記，預設是否允許先用單一 mapping？
6. Google Sheet 與舊系統月報若數字不一致，哪一邊是最終準據？

## Supporting Scripts

匯入前至少要跑以下 read-only 腳本並保存輸出：

```powershell
py -3 .\scripts\repair\year_month_audit.py
py -3 .\scripts\repair\room_status_audit.py
py -3 .\scripts\repair\user_table_audit.py
py -3 .\scripts\migration\maintenance_legacy_scan.py
```

## Exit Criteria

本文件可視為完成的條件：

- M1-M16 全部有明確決議
- 所有 `REQUIRED` 項目都不是空白
- `R06` 已定位
- `user/users` 正式來源已決定
- `Room.status` 與虛擬 tenant 清洗規則已凍結
