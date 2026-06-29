# Phase 2 Integrations Gap Check — Round 7

Author: open
Date: 2026-06-29
Baseline: `codex-phase2-mainline-01` (HEAD)
Tests: `44 passed, 15 skipped`

---

## 1. Executive Summary

自 recheck-06 以來，Codex 已完成絕大多數 integrations 前置工作。本次 gap check 僅鎖定 `app/integrations/`、相關 route、docs、runbook 範圍，不做全缺口盤點。

**結論：integrations skeleton 已落地，邊界明確，尚無 blocking gap。** 剩餘未實作項目均符合 Phase 2 boundary rule（interface only / placeholder / 延期到 Phase 3）。

---

## 2. `app/integrations/` 落地狀態

| 檔案 | 狀態 | 內容 |
|------|------|------|
| `__init__.py` | ✅ | 匯出 `OCRClientProtocol`、`SheetsClientProtocol` |
| `README.md` | ✅ | Phase 2 boundary rule 定義清楚 |
| `ocr_client.py` | ✅ | `OCRClientProtocol` interface（僅 method signature） |
| `sheets_client.py` | ✅ | `SheetsClientProtocol` interface（僅 method signature） |
| `line_webhook.py` | ✅ | Blueprint + POST `/integrations/line/callback` → 回傳 501 |

**Blueprint registration** ✅ — `app/modules/__init__.py` 已註冊 `line_webhook_bp`。

---

## 3. 相關 route 狀態

| Route | 預期用途 | 狀態 | 說明 |
|-------|---------|------|------|
| `POST /integrations/line/callback` | LINE webhook | ✅ | 501 placeholder |
| `POST /api/analyze-receipt` | OCR 收據分析 | ❌ | 需 OCR engine，Phase 2 rule 不允許 |
| `GET,POST /api/payment-records` | API variant | ❌ | 非 blocking，可延至 Phase 3 |
| `POST /api/electricity/create-from-ocr` | OCR 電費單 | ❌ | 需 OCR engine，Phase 2 rule 不允許 |
| `POST /water/preview` | 水費預覽 | ❌ | UX convenience，無外部依賴 |
| `GET,POST /sheets/import` | Google Sheets | ❌ | 需外部授權，Phase 2 rule 不允許 |

---

## 4. 錯誤頁面狀態

| 模板 | 狀態 | Error handler |
|------|------|---------------|
| `templates/errors/404.html` | ✅ | `handlers.py` → `handle_not_found` ✅ |
| `templates/errors/500.html` | ✅ | `handlers.py` → `handle_server_error` ✅ |
| `templates/errors/app_error.html` | ✅ | `handlers.py` → `handle_app_error` ✅ |
| Integration test | ✅ | `test_error_pages_and_migration_index.py` |

**結論：error pages 已完整落地。** 不再屬於缺口。

---

## 5. Migration / Repair 入口狀態

| 項目 | 狀態 |
|------|------|
| `scripts/migration/migration_index.py` | ✅ — read-only entry point |
| `scripts/migration/maintenance_legacy_scan.py` | ✅ |
| `scripts/migration/README.md` | ✅ |
| `scripts/repair/*.py` (4 audit scripts) | ✅ |
| `scripts/repair/README.md` | ✅ |
| Migration docs in runbook | ✅ `docs/operations/dev-runbook.md` 有提及 |
| Integration test | ✅ `test_repair_scripts_and_integrations_boundary.py` + `test_error_pages_and_migration_index.py` |

**結論：migration/repair entry point 已落地。**

---

## 6. 尚未落地的項目

| 項目 | 建議階段 | 理由 |
|------|---------|------|
| `POST /water/preview` | **Phase 2 或 Phase 3** | 無外部依賴，純 route + template，工時 < 30 min |
| `GET,POST /api/payment-records` | **Phase 3** | Service/repo 已存在，僅缺 route |
| `POST /api/analyze-receipt` | **Phase 3** | 需 OCR engine 整合決策 |
| `POST /api/electricity/create-from-ocr` | **Phase 3** | 同上 |
| `GET,POST /sheets/import` | **Phase 3** | 需 Google API 授權設定 |
| `POST /integrations/line/callback` 實作填補 | **Phase 3** | 需 LINE API channel 設定 |

以上項目均符合 Phase 2 boundary rule：**不阻擋 Phase 2 結案，可安全延至 Phase 3。**

---

## 7. Runbook / Docs 相關

| 文件 | 狀態 | 備註 |
|------|------|------|
| `docs/operations/dev-runbook.md` | 🟡 有提及 integrations boundary | 184 行提到「integrations 目前只讀介面與佔位流程」，可考慮補強獨立章節 |
| `app/integrations/README.md` | ✅ | Phase 2 rule 清楚 |

---

## 8. 結論

Integrations skeleton 已在 `codex-phase2-mainline-01` 完整落地：

- ✅ Interface/protocol：`OCRClientProtocol`、`SheetsClientProtocol`
- ✅ Placeholder route：`POST /integrations/line/callback` → 501
- ✅ Error pages：404 / 500 / app_error 三層齊備
- ✅ Migration entry point：`scripts/migration/migration_index.py`
- ✅ Repair scripts：4 支 audit script + README
- ✅ 測試覆蓋：44 passed, 15 skipped
- ✅ Phase 2 boundary rule 已在文件載明

剩餘 6 項（water preview + API variant + 3 OCR/sheets + LINE 實作）均符合 Phase 2 defer 規則，不阻擋結案。

**無需新增 incident。** 邊界清楚，無模型/契約矛盾。

---

*End of report — no models touched, no data contracts modified, no core code rewritten.*
