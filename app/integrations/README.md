# integrations

LINE、OCR、Sheets 或其他外部整合。

## Phase 2 Boundary Rule

目前只允許：

- interface / protocol
- route skeleton / placeholder
- README / docs / usage boundary

目前不允許：

- 真實外部 API 呼叫
- 硬編碼 secrets
- 在 route 內直接串第三方服務

## Current Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package entry |
| `ocr_client.py` | OCR interface only |
| `sheets_client.py` | Sheets export interface only |
| `line_webhook.py` | Phase 3 placeholder route |
