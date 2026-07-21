# 退租結清報表工作紀錄

日期：2026-07-20  
狀態：已完成備份副本驗收；等待正式上線決策  
範圍：退租結清明細報表、房東可見範圍、房東端狀態語意與匯出

## 本次完成項目

### 報表功能與驗收

- 完成退租結清明細報表及 CSV／XLSX 匯出：
  - 路由：`/reports/move-out-settlements`
  - 匯出：`/reports/move-out-settlements/export?format=csv|xlsx`
  - 篩選：退租月份、可見物件、結算狀態。
- 管理者視角完成驗收：
  - 2026-04 的已結算資料 1 筆。
  - 2026-05 的已結算資料 4 筆。
  - 已核對退款支付費用、建議實付退款與應收餘額；結果符合演練資料。
  - 畫面明確提示「已結算」代表退款分攤已確認，不代表已付款或已退款。
- 房東視角完成權限驗收：
  - 僅顯示所屬物件與資料。
  - CSV／XLSX 匯出連結自動受可見物件限制。
  - 以非所屬物件參數直接存取時回應 `403 Forbidden`。

### 房東端狀態語意調整

- 房東端僅顯示並可篩選：`全部`、`已結算`、`未結算`。
- 內部狀態維持給管理端使用：`draft`、`settled`、`voided`、`cancelled`。
- 房東端的未結算原因映射：
  - `draft` → 尚待完成結算資料。
  - `voided` → 此結算已作廢。
  - `cancelled` → 此結算已取消。
  - 未知的非已結算狀態 → 尚待確認結算原因。
- 房東端不得以網址傳入內部狀態；會回應 `403`。
- 房東匯出改用房東語意欄位 `landlord_status` 與 `unsettled_reason`，不再以原始內部狀態作為狀態欄。

## 主要變更檔案

- `app/modules/reports/routes.py`
- `app/services/report_service.py`
- `app/repositories/report_repository.py`
- `app/templates/reports/move_out_settlements.html`
- `tests/integration/test_move_out_settlement_report.py`

## 驗證紀錄

- `pytest -q tests\\integration\\test_move_out_settlement_report.py tests\\integration\\test_move_out_settlements.py tests\\integration\\test_reporting_expansion.py`
  - 結果：`13 passed`。
- 使用獨立本機 Flask 驗收服務並明確指向備份資料庫完成畫面驗收。
- 正式資料庫 `runtime-real.db` 未寫入；SHA-256 維持：
  - `2e43fa710e4330985a8dca89310f9dea589754be3f0248c331cc59f9b7a3a04c`

## 備份副本與帳號處理

- 演練／驗收資料庫：`backups/runtime_20260719_143424.db`。
- 為登入與房東權限驗收，僅在備份副本更新管理者測試憑證、建立一個房東測試帳號；未在正式資料庫建立或變更帳號。
- 帳號名稱、密碼與個人資料不記錄於本文件。

## 2026-07-22：歷史帳務 staging 重建（4–6 月）

- 以最初 Google 月清單為帳單金額與房態主來源，與 Google「轉帳房東紀錄」的 2026-04 至 2026-06 收租明細逐房比對：
  - 房東紀錄覆蓋 90 間房；與主清單重疊的有效租客姓名一致。
  - 2026-04 永泰84巷5樓 17 號的房態衝突，以主清單較新的「待修」標記為準。
  - 房東紀錄未覆蓋的 63–64 間房，仍保留主清單資料。
- 已建立新的隔離 staging 資料庫 `staging/runtime-google-rebuild-through-202606-v4.db`：
  - 僅含 2026-04、2026-05、2026-06；未匯入 7 月。
  - 共 154 房、133 租客、139 租約、361 筆租客帳單。
  - 每月租客帳單合計：2026-04 555,645 元、2026-05 811,086 元、2026-06 757,152 元。
  - SQLite `integrity_check` 結果為 `ok`。
- 已將可確認的退租尾款歸屬回前房客：王麗美、黃文櫻、黃泰祥、王儷靜。
- 昌裕街71巷之空房維修／額外電費，以及無歷史租客可歸屬的非租客費用，共 7 筆、1,810 元，保留在 staging 稽核檔但不建立租客帳單。
- 正式資料庫 `runtime-real.db` 未寫入；SHA-256 維持不變：
  - `2e43fa710e4330985a8dca89310f9dea589754be3f0248c331cc59f9b7a3a04c`

## 下一步執行規劃

1. 整理正式上線前決策資料：列出正式資料庫遷移、首批正式建單、驗收資料清理及回復方案。
2. 待使用者補強並確認 2026-07 資料後，另行建立包含 7 月的 staging 版本與比對結果。
3. 提交使用者決策：是否執行正式資料庫遷移與首批正式建單。
4. 只有取得明確授權後，才對 `runtime-real.db` 執行遷移或建單；執行前後均計算 SHA-256、保留備份與驗證報表結果。
5. 正式上線後，以管理者及至少一個房東帳號重做精簡驗收：可見範圍、已結算／未結算語意、CSV／XLSX 匯出。

## 未決事項

- 是否將房東端 XLSX 匯出流程加入 Google Sheets 上傳／轉檔操作指引。
- 是否在正式上線前移除或保留備份副本中的驗收帳號與獨立本機驗收服務。
