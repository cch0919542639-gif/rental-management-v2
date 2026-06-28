# payments module

## 責任

- 付款記錄收件
- OCR 解析結果落地
- 人工審核
- 帳單對帳與連結

## 依賴文件

- `../../../data_contracts/payments-contract.md`
- `../../../data_contracts/status-machines.md`

## 第一批要做

- 統一正式付款模型
- payment workflow service
- verify / reject / link lifecycle

## 注意

- 不可同時維持兩套付款流程
