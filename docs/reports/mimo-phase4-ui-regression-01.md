# Phase 4 UI Regression Report — Rental Rebuild (zh-TW)

**Date**: 2026-07-01
**Branch**: `agent/box-phase4-runbook-tests-01`
**Repo**: `D:\CodexRuntime\rental\rebuild`
**Scope**: UI/Page regression only — no service/repository/model changes
**Auditor**: MiMoCode Agent

---

## Executive Summary

The rental rebuild project is a **Flask WPF application** with Jinja2 templates. The zh-TW localization is **mostly complete** for:
- All form labels (WTForms `StringField`/`SelectField`/`SubmitField` labels are in Chinese)
- All flash messages (46 messages, all in Chinese)
- All error pages (404, 500, app_error — all in Chinese)
- Dashboard, billing list, payments list, maintenance index — all in Chinese

**However, there are 12+ hardcoded English strings** in the XAML/HTML templates that create an inconsistent bilingual experience. These are the regression findings.

---

## 1. Base Template Navigation (base.html)

The header navigation links are **all in English**:

| Line | Element | Current (English) | Should Be (zh-TW) |
|------|---------|-------------------|---------------------|
| 29 | Nav link | `Dashboard` | 儀表板 |
| 30 | Nav link | `Billing` | 帳單管理 |
| 31 | Nav link | `Payments` | 付款記錄 |
| 32 | Nav link | `Electricity` | 電費管理 |
| 33 | Nav link | `Water` | 水費管理 |
| 34 | Nav link | `Reports` | 報表 |
| 35 | Nav link | `Maintenance` | 維修管理 |
| 36 | Nav link | `Landlords` | 房東管理 |
| 37 | Nav link | `Properties` | 物件管理 |
| 38 | Nav link | `Rooms` | 房間管理 |
| 39 | Nav link | `Tenants` | 房客管理 |
| 40 | Nav link | `Contracts` | 合約管理 |
| 41 | Nav link | `Logout` | 登出 |

**Severity**: HIGH — Navigation is the first thing users see.

---

## 2. Page Title Headers (English `<h1>` tags)

Several page titles remain in English:

| File | Line | Current | Should Be |
|------|------|---------|-----------|
| `dashboard/index.html` | 5 | `Dashboard` | 儀表板 |
| `maintenance/index.html` | 5 | `Maintenance` | 維修管理 |
| `properties/list.html` | 5 | `Properties` | 物件管理 |
| `tenants/list.html` | 5 | `Tenants` | 房客管理 |
| `contracts/list.html` | 5 | `Contracts` | 合約管理 |
| `rooms/list.html` | 5 | `Rooms` | 房間管理 |
| `electricity/index.html` | 3 (title) | `Electricity` | 電費管理 |
| `water/list.html` | 3 (title) | `Water` | 水費管理 |
| `reports/index.html` | 3 (title) | `Reports` | 報表 |
| `reports/maintenance.html` | 3 (title) | `Maintenance Summary` | 維修彙總 |
| `billing/contract_list.html` | 3 (title) | `Contract Bills` | 合約帳單 |

**Severity**: MEDIUM — Page titles appear in browser tabs and `<h1>`.

---

## 3. Billing Generate Form — English Label

| File | Line | Current | Should Be |
|------|------|---------|-----------|
| `billing/generate_form.html` | 7 | `<strong>Contract:</strong>` | `<strong>合約：</strong>` |

**Severity**: LOW — Single label, but visible on the form.

---

## 4. Maintenance Index — English Mixed Content

| File | Line | Current | Should Be |
|------|------|---------|-----------|
| `maintenance/index.html` | 10 | `Open 維修單` | 開放維修單 |
| `maintenance/index.html` | 88 | `Room ID` (table header) | 房間 ID |
| `maintenance/index.html` | 88 | `物件`, `房號`, `狀態`, `備註` | (OK — already Chinese) |

**Severity**: LOW — Mixed English/Chinese in the same table.

---

## 5. Reports — English Table Headers

| File | Line | Current | Should Be |
|------|------|---------|-----------|
| `reports/maintenance.html` | 15 | `Open` (card label) | 開放 |
| `reports/maintenance.html` | 24 | `Open` (table header) | 開放 |
| `reports/index.html` | 17 | `total / paid / unpaid` (inline English) | 總額 / 已繳 / 未繳 |

**Severity**: LOW — Mixed English terms in Chinese context.

---

## 6. Payments — English OCR Labels

| File | Line | Current | Should Be |
|------|------|---------|-----------|
| `payments/list.html` | 46 | `OCR 資訊` (summary) | (OK — Chinese) |
| `payments/list.html` | 48 | `OCR Engine：` | OCR 引擎： |
| `payments/list.html` | 49 | `Image Path：` | 影像路徑： |
| `payments/list.html` | 50 | `OCR Raw：` | OCR 原文： |
| `payments/list.html` | 51 | `LLM Raw：` | LLM 回應： |

**Severity**: LOW — Technical labels, but should be consistent.

---

## 7. What Is Already Correct (zh-TW)

The following are **already fully localized**:

### Forms (WTForms labels)
- `auth/forms.py`: 帳號, 密碼, 登入
- `billing/forms.py`: 合約, 月份, 租金, 電費, 水費, 其他費用, 已繳, 備註, 儲存帳單, 產生帳單
- `payments/forms.py`: 合約 ID, 帳單, 金額, 交易日期, 付款人, 交易編號, 銀行名稱, 帳號, 戶名, OCR 引擎, 影像路徑, OCR 原文, LLM 回應, 備註, 建立付款記錄, 審核備註, 送出
- `maintenance/forms.py`: 房間, 分類, 優先級, 標題, 描述, 通報人, 指派處理人, 預估成本, 實際成本, 備註, 儲存維修單, 套用篩選
- `electricity/forms.py`: 物件, 房間, 電表號碼, 主電表, 備註, 儲存電表, 建立電費單, 新增抄表, 回寫月帳單
- `water/forms.py`: 物件, 備註, 儲存水費單, 月帳單 ID, 回寫月帳單
- `contracts/forms.py`: 房客, 房間, 儲存
- `properties/forms.py`: 房東, 名稱, 地址, 計費規則, 儲存
- `tenants/forms.py`: 姓名, 電話, 身分證字號, 緊急聯絡人, 緊急聯絡電話, 儲存
- `rooms/forms.py`: 房產, 房號, 狀態, 儲存
- `landlords/forms.py`: 姓名, 電話, 電費戶號, 水費戶號, 儲存

### Flash Messages (46 total, all Chinese)
- Auth: 帳號或密碼錯誤
- Billing: 月帳單已建立, 月帳單已更新, 月帳單付款狀態已更新, 月帳單已產生
- Payments: 付款記錄已建立, 付款記錄已驗證, 付款記錄已駁回, 付款記錄已連結帳單
- Maintenance: 維修單已建立, 維修單已更新, 維修單狀態已更新
- Electricity: 物件電費單已建立, 電表已建立, 電表已更新, 電費單已建立, 抄表資料已建立, 電費單已標記為 calculated, 電費已回寫月帳單
- Water: 水費單已建立, 水費單已更新, 水費已回寫月帳單, 水費單已刪除
- Properties/Rooms/Tenants/Contracts/Landlords: 全部中文

### Error Pages
- `errors/404.html`: 404｜找不到頁面 (Chinese)
- `errors/500.html`: 500｜伺服器錯誤 (Chinese)
- `errors/app_error.html`: 操作失敗, 錯誤代碼 (Chinese)

### Login Page
- `auth/login.html`: 登入, 帳號, 密碼 (Chinese)

---

## 8. /readyz and /healthz Endpoints

Both endpoints are **API-only** (return JSON), not user-facing HTML:

- `/healthz` → `{"ok": true}` — No UI strings
- `/readyz` → `{"ok": true/false, "checks": {...}, "issues": [...]}` — Returns English check names (`"database"`, `"config"`) but this is an internal API, not a user-facing page.

**Verdict**: No UI regression needed — these are API endpoints.

---

## 9. Deployment Baseline (phase4-launch-baseline.md)

The deployment baseline document is **mostly in Chinese** with appropriate English technical terms:

| Line | Content | Status |
|------|---------|--------|
| 7 | Goal description | Chinese |
| 11-16 | Baseline items | Chinese |
| 18-31 | Environment variables | English (correct — variable names) |
| 35-66 | Pre-launch sequence | Chinese with PowerShell code blocks |
| 68-80 | Backup/Restore | Chinese |
| 82-87 | Known risks | Chinese |
| 89-95 | Exit criteria | Chinese |

**Verdict**: Consistent with zh-TW localization intent.

---

## 10. Summary of Findings

| Category | Severity | Count | Status |
|----------|----------|-------|--------|
| Base nav links (English) | HIGH | 13 | Not translated |
| Page `<h1>` titles (English) | MEDIUM | 11 | Not translated |
| Billing form label (English) | LOW | 1 | Not translated |
| Maintenance mixed English | LOW | 2 | Not translated |
| Reports mixed English | LOW | 3 | Not translated |
| Payments OCR labels (English) | LOW | 4 | Not translated |

**Total untranslated user-visible strings: ~34**

---

## 11. Recommendations

1. **Immediate**: Translate `base.html` navigation links — these are the most visible UI elements.
2. **Immediate**: Translate all `<h1>` page titles to Chinese.
3. **Quick fix**: Translate the `Contract:` label in `billing/generate_form.html`.
4. **Quick fix**: Translate `Open` and `Room ID` in maintenance/reports templates.
5. **Quick fix**: Translate OCR labels in `payments/list.html`.

---

## 12. What Was NOT Checked (Out of Scope)

Per user instructions, the following were NOT modified or checked:
- Service layer code
- Repository layer code
- Model layer code
- Database migrations
- Business logic

The report focuses exclusively on UI/page display regression for zh-TW localization consistency.
