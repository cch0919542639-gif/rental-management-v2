# Integrations Contract

## 範圍

- LINE Bot
- OCR / receipt analyze
- Google Sheets import

## 原則

- 外部整合與核心業務邏輯分離
- 外部輸入先進 integration boundary，再轉成正式 command / DTO
- secrets 只能來自環境設定或安全設定層

## LINE Bot

角色：

- 接收訊息與圖片
- 建立付款待處理記錄或通知流程

規則：

- Webhook 不直接寫核心業務邏輯
- 長耗時工作需背景任務或 queue
- 與付款流程的接點要落到 `payments` 模組 command/service

## OCR

角色：

- 收圖片
- 辨識匯款資訊或電費資料

規則：

- OCR 原始輸出保留，但不得直接視為正式資料
- 正式資料需經過 parse + validate + human review 或 rule check

## Sheets Import

角色：

- 匯入房東、房客、房間、帳單等資料

規則：

- 匯入流程需有 import log
- 匯入欄位 mapping 必須文件化
- 匯入不可直接繞過正式 service / validation

## 安全規則

- 禁止明文 API key 寫在 repo
- webhook secret、channel token、OCR key 都放 config / secret store

## 已知舊案問題

- `config.py` 有明文 API key
- LINE / OCR / app route 混在單一 `app.py`
