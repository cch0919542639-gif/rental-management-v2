# 水電 OCR 作業入口收工紀錄

## 狀態

已在正式租屋系統部署管理員用的「水電費作業」入口。可選物件與水電類型、上傳 PDF 或照片、使用 Google Vision 取得 OCR 原文，並接續既有電費單、水費單與抄表流程。

## 安全與帳務邊界

- 上傳只供 OCR 使用；Cloud Storage 暫存區禁止公開，30 天自動刪除。
- OCR 僅產生人工校正草稿，不自動建立 `MonthlyBill`、不自動向房客入帳。
- 正式 VM 使用獨立的 `rental-vision-ocr` 服務帳號；未建立下載式金鑰。

## 變更範圍

- `app/integrations/ocr_client.py`：Google Vision 圖片與 PDF OCR adapter。
- `app/modules/utility_intake/`、`app/templates/utility_intake/`：上傳與人工校正入口。
- `app/core/config/settings.py`、`app/modules/__init__.py`、`app/templates/base.html`：設定、註冊與導覽。
- `tests/integration/test_utility_intake.py`：入口不入帳的回歸測試。

## 驗證

- `py -3 -m pytest -q tests\\integration\\test_utility_intake.py tests\\integration\\test_electricity_property_workflows.py tests\\integration\\test_water_property_preview.py`：4 passed。
- `py -3 -m pytest -q tests\\integration`：184 passed、15 skipped。migration bridge 測試已改為比對 bridge 實際偵測到的 Alembic head，不再硬編碼版本號。
- 正式 VM：`rental-v2.service` active，`/readyz` 回傳 200；新入口未登入時導向登入頁。

## 後續

以實際水電單完成第一次人工 OCR 驗收，核對 PDF 辨識結果、物件選擇與各房電表度數後，再由使用者確認是否建立水電草稿或入帳。

## 更新者

Codex，2026-09-19。此次只提交水電 OCR 作業入口相關檔案；未推送遠端。
