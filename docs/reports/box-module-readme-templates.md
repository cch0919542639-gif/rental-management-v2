# Module README Templates

可重複使用的模組 README 樣板（供後續工程模組撰寫）。

---

# <module> README Template

## Responsibility

- 本模組負責哪些「封閉且可驗收」的能力。
- 明確描述與其他模組的邊界（例如：只產生資料/只驗證/只提供查詢，不直接做 UI/route）。

## Inputs

- 觸發來源：API/service 呼叫/批次腳本/匯入事件。
- 關鍵輸入參數或資料：
  - 例如：contract_id / year_month / room_id / tenant_id
  - 例如：OCR/表單輸入（若適用）

## Outputs

- 產出內容與形狀：
  - 例如：寫入哪些 DB 表（或更新哪些欄位）
  - 例如：回傳哪些查詢結果欄位
- 狀態機/流程結果（若適用）：例如 maintenance 狀態、payment_records.record_status。

## Dependencies

- 依賴的「內部」模組/層：
  - models / repositories / services / templates
- 依賴的「外部」系統：
  - OCR、LINE webhook、Google Sheets、單元測試資料源等。

## Risks

- 資料一致性風險（P0/P1/P2）：
  - 例如：year_month 格式不一致、status 值非允許集合、跨模組推導與契約脫鉤。
- 計算/轉換風險：
  - 例如：YYYYMM ↔ YYYY-MM 的唯一轉換點。
- 併發/重放風險（若有）：
  - 例如 Parallel Rebuild 下的幂等性。

## Tests

- 單元測試（unit）：測什麼純函式/規則。
- 整合測試（integration）：測 DB 寫入/查詢/關聯。
- e2e/回歸（若適用）：需對應 mimo 回歸清單或 regression checklist。
- 測試資料準備方式：使用 fixtures/seed 或 mock DB。

---

# 可選附加章節（依模組類型）

## billing / electricity / water

- 計費計算規則：
  - 公式來源、rounding 規則、rate_type/契約優先序。
- year_month：
  - 說明 DB 固定 `YYYYMM`，UI/API 用 `YYYY-MM`，轉換集中在 helper。

## payments

- PaymentRecord 唯一性與狀態機：pending/verified/rejected/linked
- 對帳/連結邏輯：
  - 何時寫入 payment_records，何時同步 monthly_bills.paid。

## reports

- 查詢範圍與過濾條件（property/landlord/room/tenant/year_month）
- 報表一致性：與 payments/billing 的字段對齊策略

## integrations

- 外部 API/事件：Webhook/匯入/批次
- 失敗重試/錯誤處理：如何確保資料可重放（idempotency）

