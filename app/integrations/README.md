# integrations

LINE、OCR、Sheets 或其他外部整合。

## Phase 3 Boundary Rule

目前只允許：

- interface / protocol
- route skeleton / placeholder
- README / docs / usage boundary
- OCR minimal adapter within frozen contract

目前不允許：

- 硬編碼 secrets
- 在 route 內直接串第三方服務
- 直接改動 domain model 或新增 OCR 專用欄位

## Current Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package entry |
| `ocr_client.py` | OCR protocol + minimal provider factory |
| `sheets_client.py` | Sheets export interface only |
| `line_webhook.py` | Phase 3 placeholder route |

## OCR Rules

- OCR analysis may write `raw_ocr_text`, `raw_llm_response`, `ocr_engine`
- OCR analysis must not auto-change `PaymentRecord.record_status`
- OCR analysis must not auto-trust extracted values into core payment fields
- Missing config must degrade gracefully instead of crashing
