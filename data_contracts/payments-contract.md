# Payments Contract

## 目標

收斂新版付款流程，只保留一套正式模型與狀態機。

## 已確認事實

- 舊 ORM 有 `PaymentRecord`
- 舊 route 另存在 `/payment/new` 等流程，使用疑似未完成的 `Payment` 模型
- `payment_records` 目前資料量為 0

## 第一版正式模型

新版先以 `PaymentRecord` 為唯一正式付款記錄實體，是否需要另一張 tenant-submitted payment 表，後續再由 `reasonix` 決策。

正式欄位：

- `id`
- `contract_id`
- `monthly_bill_id`
- `amount`
- `bank_name`
- `account_number`
- `account_holder`
- `transaction_date`
- `payer_name`
- `transaction_id`
- `status_text`
- `raw_ocr_text`
- `raw_llm_response`
- `image_path`
- `ocr_engine`
- `record_status`
- `verified_by_id`
- `verified_at`
- `notes`
- `created_at`

## record_status 第一版

- `pending`
- `verified`
- `rejected`
- `linked`

語義：

- `pending`
  - 已收到記錄，尚未人工確認或對帳
- `verified`
  - 識別內容已人工確認
- `rejected`
  - 無效或錯誤的付款記錄
- `linked`
  - 已成功連結到目標帳單或合約

## 契約規則

- `amount` 不可為負值
- `transaction_id` 若存在，應盡量唯一
- `monthly_bill_id` 與 `contract_id` 可先允許空值，支援先收件後對帳

## 新版決策

- 付款資料蒐集、OCR、人工審核、對帳連結必須是同一條流程
- 不允許再並存一套未定義完成的 `Payment` route/model

## 驗收點

- 同一筆付款記錄的來源、辨識結果、人工審核、帳單連結都能追溯
