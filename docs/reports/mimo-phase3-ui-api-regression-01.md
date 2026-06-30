# Phase 3 UI/API Regression Report — mimo-phase3-ui-api-regression-01

- **Branch**: `agent/mimo-phase3-ui-api-regression-01`
- **Base**: `codex-phase2-mainline-01`
- **Date**: 2026-06-30
- **Tests**: 62 passed, 15 skipped (baseline maintained)

---

## Checked Pages

| Page | Route | Result |
|------|-------|--------|
| Payment list | `/payments/` | ✅ Verified — status labels, OCR block, action links |
| Payment create | `/payments/create` | ✅ Verified — form fields, Chinese labels |
| Payment verify | `/payments/<id>/verify` | ✅ Fixed — labels, status display, amount format |
| Payment reject | `/payments/<id>/reject` | ✅ Fixed — labels, status display, amount format |
| Payment link | `/payments/<id>/link` | ✅ Fixed — labels, status display, amount format |
| Error 404 | `/nonexistent` | ✅ Fixed — title now Chinese |
| Error 500 | N/A (handler) | ✅ Fixed — title now Chinese |
| App error | DomainValidationError | ✅ Fixed — title now Chinese |

## Checked APIs

| Endpoint | Method | Result |
|----------|--------|--------|
| `/api/payment-records/` | GET | ✅ Correct — items, count, limit, offset, filters |
| `/api/payment-records/<id>` | GET | ✅ Correct — all contract fields serialized |
| `/api/payment-records/` | POST | ✅ Correct — 201, pending status, amount as string |
| `/api/payment-records/<id>` | PATCH | ✅ Correct — partial update, unknown field 422 |
| `/api/payment-records/<id>/verify` | POST | ✅ Correct — verified status, verified_by_id |
| `/api/payment-records/<id>/reject` | POST | ✅ Correct — rejected status, verified_by_id |
| `/api/payment-records/<id>/link` | POST | ✅ Correct — linked status, bill.paid=True |
| `/api/payment-records/<id>/analyze` | POST | ✅ Correct — manual_review_required=True |

## LINE Webhook

| Scenario | Status Code | Result |
|----------|-------------|--------|
| Config missing (`LINE_CHANNEL_SECRET`) | 501 | ✅ `error: "not_configured"` |
| Invalid signature | 401 | ✅ `error: "invalid_signature"` |
| Valid signed payload | 200 | ✅ `status: "accepted"`, event_count, reply_capable |
| Missing events array | 400 | ✅ `error: "invalid_payload"` |
| Invalid JSON | 400 | ✅ `error: "invalid_payload"` |

## Error / Feedback Consistency

| Check | Result |
|-------|--------|
| 422 API response format | ✅ `{error, message, details}` with field-level errors |
| 404 API response format | ✅ `{error: "not_found", message: "找不到指定資源"}` — fixed |
| 409 conflict response | ✅ `{error: "conflict", message: "..."}` |
| UI status labels in Chinese | ✅ 待審核/已驗證/已連結/已駁回 (list, verify, link pages) |
| Amount format consistency | ✅ API: `"12345.00"` string, UI: `12345.00` formatted — fixed |
| Error page titles in Chinese | ✅ 找不到頁面/伺服器錯誤/操作失敗 — fixed |
| OCR info display | ✅ detail block with word-wrap — fixed |

---

## Code Changes Made

### Templates (UI consistency fixes)

| File | Change | Type |
|------|--------|------|
| `app/templates/payments/review_form.html` | English labels → Chinese (付款記錄 ID/金額/付款人/狀態); status label mapping; amount formatted to 2dp | Polish |
| `app/templates/payments/link_form.html` | English labels → Chinese (付款記錄 ID/金額/狀態); status label mapping; amount formatted to 2dp | Polish |
| `app/templates/payments/list.html` | Title `Payments` → `付款記錄`; Amount format to 2dp; OCR block word-wrap | Polish |
| `app/templates/errors/404.html` | Title `404 Not Found` → `找不到頁面` | Polish |
| `app/templates/errors/500.html` | Title `500 Server Error` → `伺服器錯誤` | Polish |
| `app/templates/errors/app_error.html` | Title `App Error` → `操作失敗` | Polish |

### Error handlers (API response consistency)

| File | Change | Type |
|------|--------|------|
| `app/core/errors/handlers.py` | 404 JSON message: `Resource not found` → `找不到指定資源` | Polish |
| `app/core/errors/handlers.py` | 500 JSON message: `Internal server error` → `伺服器內部錯誤` | Polish |

## Incidents / Blockers

**None.** All findings were low-risk UI polish issues resolved within scope.

## Verification

```
pytest tests/ -v --tb=short
# Result: 62 passed, 15 skipped (baseline maintained)
```

All template changes verified via existing integration tests:
- `test_payment_list_shows_ocr_section_when_present` — OCR block still renders
- `test_payment_reject_flow` — reject flow with Chinese labels works
- `test_payment_list_with_records` — list page renders correctly
- `test_payment_records_api_verify_reject_and_link_flow` — full API lifecycle
- `test_payment_records_api_returns_404_for_missing_record` — 404 JSON format
- `test_payment_records_api_returns_422_field_details` — 422 JSON format
- `test_line_webhook_*` — LINE webhook scenarios unchanged
