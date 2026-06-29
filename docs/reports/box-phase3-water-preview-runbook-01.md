# Phase 3 Box — Water Preview Runbook (Round 01)

Date: 2026-06-29  
Branch: `codex-phase2-mainline-01`  
Baseline pytest: **50 passed, 15 skipped, 0 failures**  
Water preview tests: **4/4 passed** (2 original + 2 new)

---

## 1. What Is Water Preview?

Water preview allows an operator to **see the calculated water allocation result** before actually posting it to a monthly bill. Two preview modes exist:

| Mode | Description |
|------|-------------|
| `shared_by_stay_days` | Allocates water bill total proportionally by stay days across all active contracts in the same property |
| `independent_meter` | Applies a fixed amount directly to a single monthly bill |

**Preview does NOT write data.** It runs the same allocation logic that `POST /water/<id>/post` uses, but returns the result for inspection only.

---

## 2. Route & Page

| Item | Detail |
|------|--------|
| URL | `GET/POST /water/<water_bill_id>/preview` |
| Auth | ✅ Login required |
| Form fields | `monthly_bill_id` (required), `mode` (required), `amount` (required for independent_meter) |
| Template | `water/preview.html` |
| Service | `WaterService.preview_post_to_monthly_bill()` → dispatches to `preview_shared_to_monthly_bill()` or `preview_independent_to_monthly_bill()` |

---

## 3. Manual Verification Steps

### 3.1 Prerequisites

```powershell
cd D:\CodexRuntime\rental\rebuild
py -3 -m flask --app app.wsgi run --debug
```

Login at `http://127.0.0.1:5000/auth/login` with `admin` / `admin123`.

### 3.2 Shared Mode Preview

1. Navigate to `/water/` and create a water bill for "North House" (June 2026, total_amount=300, usage=10)
2. Click **預覽分攤** on the newly created bill
3. Fill in:
   - **月帳單 ID**: pick the June 2026 bill (should be ID 1)
   - **分攤模式**: `shared_by_stay_days`
   - **獨立水表金額**: leave blank
4. Click **預覽分攤**
5. **Expected result:**
   - Page shows **預覽結果** section
   - Shows mode: `shared_by_stay_days`
   - Shows **預覽水費金額** (e.g. 300.00, since only 1 contract exists)
   - Shows **合約居住天數** (e.g. 30 days, the full billing period)
   - Shows **物件總居住天數**
   - Shows **總用量**

### 3.3 Independent Mode Preview

1. Create another water bill (July 2026, total_amount=350)
2. Click **預覽分攤**
3. Fill in:
   - **月帳單 ID**: pick a monthly bill
   - **分攤模式**: `independent_meter`
   - **獨立水表金額**: `350`
4. Click **預覽分攤**
5. **Expected result:**
   - Page shows **預覽結果** section
   - Shows mode: `independent_meter`
   - Shows **預覽水費金額**: 350.00

### 3.4 GET Form (No Preview Yet)

1. Navigate directly to `/water/<id>/preview` in browser (GET)
2. **Expected result:**
   - Form is displayed with all fields
   - **No** "預覽結果" section
   - Submit button reads "預覽分攤"

### 3.5 Edge: Empty monthly_bill_id

1. POST to `/water/<id>/preview` with empty `monthly_bill_id`
2. **Expected result:**
   - Form re-renders (still 200)
   - No "預覽結果" section
   - Form validation error (default WTForms behavior)

---

## 4. Test Coverage

### 4.1 Existing Tests (original)

| Test | Coverage | Status |
|------|----------|--------|
| `test_water_preview_shared_mode_renders_result` | Create water bill, POST preview with shared mode, check result fields | ✅ 1/1 pass |
| `test_water_preview_independent_mode_renders_result` | Create water bill, POST preview with independent_meter, check result | ✅ 1/1 pass |

### 4.2 Tests Added in This Round

| Test | Coverage | Status |
|------|----------|--------|
| `test_water_preview_get_renders_form` | GET preview page → form renders, no preview result | ✅ 1/1 pass |
| `test_water_preview_post_no_monthly_bill` | POST with missing required field → form re-renders | ✅ 1/1 pass |
| (improved) Hardcoded `/water/1/preview` replaced with dynamic `water_bill_id` | Makes tests resilient to seeding order | ✅ |

### 4.3 Coverage Assessment

| Scenario | Covered? |
|----------|----------|
| Shared mode preview with result | ✅ Yes |
| Independent mode preview with result | ✅ Yes |
| GET renders form without preview | ✅ Yes (new) |
| POST with missing required field | ✅ Yes (new) |
| Shared mode preview — multi-contract allocation | ❌ No (requires 2+ contracts) |
| Independent mode preview — zero amount | ❌ No |
| Preview values match actual post values | ❌ No (requires service-level comparison) |

The uncovered scenarios involve either multi-contract setup (not a test issue — allocation logic) or cross-step verification (preview vs. post — service-level). These are acceptable gaps for a Phase 3 entry point.

---

## 5. Runbook Integration

### 5.1 dev-runbook.md — Update the Quick Verification list

After the existing Quick Verification items, add:

```
- `/water/<id>/preview` — Preview water allocation before posting
```

### 5.2 tests/README.md — Already includes test_water_preview.py

The test file (`test_water_preview.py`) is already tracked in the full test matrix.

---

## 6. Skip Classification — Unchanged

All 15 skips remain correctly deferred. No skips were activated or added.

---

## 7. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-06-29 | Round 01: Added 2 water preview edge-case tests. Improved test robustness (dynamic IDs). Produced manual verification runbook. | box |
