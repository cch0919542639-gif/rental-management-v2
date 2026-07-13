# Batch 2 Legacy Monthly Bills Total Reconciliation Report

> **Date**: 2026-07-13
> **Agent**: open
> **Branch**: agent/open-legacy-total-reconciliation-02
> **Data Sources**: `D:\rental\rental.db` (legacy), `D:\CodexRuntime\rental\rebuild\runtime-real.db` (new system)
> **Rule**: Read-only. No UPDATE/DELETE/INSERT on any DB, app/, scripts/, or tests.

---

## Executive Summary

11 legacy monthly_bills with total discrepancies were audited. The **legacy `total` column often embeds accumulated unpaid balances from prior months**, not just the current period charges. The new system separates this into `previous_balance` (unpaid from prior months) + current charges.

| Category | Count | Description |
|----------|-------|-------------|
| **A** — Safe to add previous_balance | 3 | Already written (170, 819, 831); verified correct |
| **B** — Needs owner confirmation | 5 | Difference exists but cannot be fully explained by chain data alone (171, 573, 578, 832, 943) |
| **C** — Not previous_balance; needs correction | 3 | Negative total, negative diff, or fee component error (172, 567, 833) |

**Blockers**: 3 Category C bills require data correction before any previous_balance can be applied.

---

## Method

**Formula**: `current_charges = rent + electricity_amount + public_electricity + water_amount + other_charges`

**Expected relationship**: `legacy_total = current_charges + previous_balance`

**Verification**: For each bill, computed `diff = legacy_total - current_charges`. Cross-checked against unpaid amounts from prior bills in the same contract chain and against the new system's `previous_balance` field.

---

## Full Comparison Table (11 Bills)

| # | Bill ID | Contract | YM | Legacy Total | Rent | Elec | Pub Elec | Water | Other | **Formula** | **Diff** | New Prev Bal | **Category** | Anomaly |
|---|---------|----------|------|-------------|------|------|----------|-------|-------|------------|---------|-------------|-------------|---------|
| 1 | 170 | 15 | 202605 | 22,654 | 4,500 | 349 | 0 | 190 | 0 | 5,039 | **+17,615** | 17,615 ✅ | **A** | paid=4500 (non-boolean) |
| 2 | 171 | 16 | 202605 | 4,520 | 4,200 | 52 | 0 | 190 | 0 | 4,442 | **+78** | 0 | **B** | Small unexplained gap |
| 3 | 172 | 17 | 202605 | 5,089 | 4,800 | 154 | 0 | 190 | 0 | 5,144 | **−55** | 0 | **C** | Negative diff; total < charges |
| 4 | 567 | 21 | 202606 | −27,186 | 4,750 | 1,710 | 0 | 0 | 0 | 6,460 | **−33,646** | 0 | **C** | Negative total; system error |
| 5 | 573 | 27 | 202606 | 11,860 | 5,500 | 697 | 0 | 0 | 0 | 6,197 | **+5,663** | 0 | **B** | Diff = 105% of rent |
| 6 | 578 | 32 | 202606 | 5,244 | 5,000 | 29 | 0 | 0 | 2 | 5,031 | **+213** | 0 | **B** | Small unexplained gap |
| 7 | 819 | 3 | 202606 | 29,710 | 4,465 | 0 | 0 | 0 | 198 | 4,663 | **+25,047** | 25,047 ✅ | **A** | Control group; verified |
| 8 | 831 | 15 | 202606 | 22,654 | 4,500 | 0 | 0 | 0 | 0 | 4,500 | **+18,154** | 18,154 ✅ | **A** | Control group; verified |
| 9 | 832 | 16 | 202606 | 4,220 | 4,200 | 0 | 0 | 0 | 0 | 4,200 | **+20** | 0 | **B** | Tiny gap (0.5%) |
| 10 | 833 | 17 | 202606 | 4,789 | 4,800 | 0 | 0 | 0 | 0 | 4,800 | **−11** | 0 | **C** | Negative diff; total < rent |
| 11 | 943 | 125 | 202605 | 6,807 | 6,500 | 289 | 40 | 18 | 0 | 6,847 | **−40** | 0 | **B** | created_at=NULL; diff=−pub_elec |

> **Formula** = rent + electricity_amount + public_electricity + water_amount + other_charges
> **Diff** = legacy_total − Formula (positive = total includes extra; negative = total understates charges)

---

## Detailed Per-Bill Analysis

### Bill 170 — Contract 15, 202605 — Category A (Control)

| Field | Legacy | New System |
|-------|--------|------------|
| rent | 4,500 | 4,500 |
| electricity_amount | 349 | 349 |
| public_electricity | 0 | 0 |
| water_amount | 190 | 190 |
| other_charges | 0 | 0 |
| **total** | **22,654** | **22,654** |
| paid | **4,500** (non-boolean) | 4,500 |
| created_at | 2026-05-26 07:47:33 | 2026-05-26 07:47:33 |
| notes | 2605: 申請補助 | 2605: 申請補助 |
| previous_balance | N/A | **17,615** |

**Formula**: 4,500 + 349 + 0 + 190 + 0 = **5,039**
**Diff**: 22,654 − 5,039 = **+17,615** = previous_balance ✅

**Chain verification**: Contract 15 has only 3 bills (445→170→831). Bill 445 (202603) total=4,500, paid=None. The 17,615 gap implies accumulated unpaid from months prior to 202603 (not in the query window). The new system correctly stores previous_balance=17,615.

**Anomaly**: `paid=4,500` is numeric, not boolean. This equals the rent amount — likely a legacy data entry where paid amount was recorded instead of boolean.

**Verdict**: Safe. previous_balance already written correctly.

---

### Bill 171 — Contract 16, 202605 — Category B

| Field | Legacy | New System |
|-------|--------|------------|
| rent | 4,200 | 4,200 |
| electricity_amount | 52 | 52 |
| water_amount | 190 | 190 |
| other_charges | 0 | 0 |
| **total** | **4,520** | **4,520** |
| paid | 0 | 0 |
| created_at | 2026-05-26 07:47:33 | 2026-05-26 07:47:33 |
| previous_balance | N/A | 0 |

**Formula**: 4,200 + 52 + 0 + 190 + 0 = **4,442**
**Diff**: 4,520 − 4,442 = **+78**

**Chain verification**: Contract 16 has 3 bills (446→171→832). Bill 446 (202603) total=4,200, paid=None → unpaid=4,200. Expected previous_balance should be at least 4,200, but new system shows 0. The +78 gap is much smaller than the unpaid chain (4,200), so it cannot be explained by unpaid amounts.

**Anomaly**: No obvious anomaly. The +78 is a small residual — possibly a rounding adjustment or manual edit in the legacy system. Insufficient data to determine source.

**Verdict**: Needs owner confirmation. The 78 gap is too small to be a previous_balance and doesn't match the unpaid chain.

---

### Bill 172 — Contract 17, 202605 — Category C

| Field | Legacy | New System |
|-------|--------|------------|
| rent | 4,800 | 4,800 |
| electricity_amount | 154 | 154 |
| water_amount | 190 | 190 |
| other_charges | 0 | 0 |
| **total** | **5,089** | **5,089** |
| paid | 0 | 0 |
| created_at | 2026-05-26 07:47:33 | 2026-05-26 07:47:33 |
| previous_balance | N/A | 0 |

**Formula**: 4,800 + 154 + 0 + 190 + 0 = **5,144**
**Diff**: 5,089 − 5,144 = **−55**

**Chain verification**: Contract 17 has 3 bills (447→172→833). Bill 447 (202603) total=4,800, paid=None. The negative diff means the legacy total is **less** than the sum of current charges — the fee components themselves are inconsistent with the total.

**Anomaly**: **Negative diff**. The total (5,089) is lower than the sum of rent + electricity + water (5,144). This indicates the total was manually adjusted downward by 55, or one of the fee components was entered incorrectly.

**Verdict**: Not a previous_balance issue. The fee components or total needs correction.

---

### Bill 567 — Contract 21, 202606 — Category C

| Field | Legacy | New System |
|-------|--------|------------|
| rent | 4,750 | 4,750 |
| electricity_amount | 1,710 | 1,710 |
| water_amount | 0 | 0 |
| other_charges | 0 | 0 |
| **total** | **−27,186** | **−27,186** |
| paid | 0 | 0 |
| created_at | 2026-05-28 09:13:50 | 2026-05-28 09:13:50 |
| previous_balance | N/A | 0 |

**Formula**: 4,750 + 1,710 + 0 + 0 + 0 = **6,460**
**Diff**: −27,186 − 6,460 = **−33,646**

**Chain verification**: Contract 21 has 7 bills. Multiple bills have paid=None (538, 544, 550). The unpaid sum before bill 567 is 18,936. But the diff is −33,646 — far beyond any unpaid chain.

**Anomaly**: **Negative total (−27,186)**. This is a system error — no bill should have a negative total. The magnitude (−33,646) is inconsistent with any possible previous_balance or unpaid accumulation. This bill appears to have been corrupted during a batch operation or migration.

**Verdict**: System error. The total must be corrected before any previous_balance can be determined.

---

### Bill 573 — Contract 27, 202606 — Category B

| Field | Legacy | New System |
|-------|--------|------------|
| rent | 5,500 | 5,500 |
| electricity_amount | 697 | 697 |
| water_amount | 0 | 0 |
| other_charges | 0 | 0 |
| **total** | **11,860** | **11,860** |
| paid | 0 | 0 |
| created_at | 2026-05-28 09:13:50 | 2026-05-28 09:13:50 |
| previous_balance | N/A | 0 |

**Formula**: 5,500 + 697 + 0 + 0 + 0 = **6,197**
**Diff**: 11,860 − 6,197 = **+5,663**

**Chain verification**: Contract 27 has 7 bills (695→688→587→458→681→619→573). All prior bills show paid=0. Unpaid sum before bill 573 = 34,153. The diff (+5,663) is much smaller than the total unpaid (34,153). The 5,663 ≈ rent (5,500) + 163 — possibly the May bill's total minus water charge, but the pattern is unclear.

**Anomaly**: No direct anomaly in the data, but the diff cannot be cleanly matched to any specific prior unpaid amount or combination.

**Verdict**: Needs owner confirmation. The +5,663 could be a previous_balance but needs verification against the legacy operator's intent.

---

### Bill 578 — Contract 32, 202606 — Category B

| Field | Legacy | New System |
|-------|--------|------------|
| rent | 5,000 | 5,000 |
| electricity_amount | 29 | 29 |
| other_charges | 2 | 2 |
| **total** | **5,244** | **5,244** |
| paid | 0 | 0 |
| created_at | 2026-05-28 09:13:50 | 2026-05-28 09:13:50 |
| previous_balance | N/A | 0 |

**Formula**: 5,000 + 29 + 0 + 0 + 2 = **5,031**
**Diff**: 5,244 − 5,031 = **+213**

**Chain verification**: Contract 32 has 7 bills. All prior bills show paid=0. Unpaid sum before bill 578 = 30,629. The diff (+213) is tiny compared to total unpaid. 213 doesn't match any single prior bill's total.

**Anomaly**: The +213 gap is too small to be a meaningful previous_balance. Could be a rounding residual or manual adjustment.

**Verdict**: Needs owner confirmation. The 213 gap is ambiguous.

---

### Bill 819 — Contract 3, 202606 — Category A (Control)

| Field | Legacy | New System |
|-------|--------|------------|
| rent | 4,465 | 4,465 |
| electricity_amount | 0 | 0 |
| other_charges | 198 | 198 |
| **total** | **29,710** | **29,710** |
| paid | 0 | 0 |
| created_at | 2026-06-05 16:13:10 | 2026-06-05 16:13:10 |
| previous_balance | N/A | **25,047** |

**Formula**: 4,465 + 0 + 0 + 0 + 198 = **4,663**
**Diff**: 29,710 − 4,663 = **+25,047** = previous_balance ✅

**Chain verification**: Contract 3 has 3 bills (451→158→819). Bill 451 (202603) total=4,465, paid=None. Bill 158 (202605) total=9,631, paid=0 → unpaid=9,631. Visible unpaid sum = 4,465 + 9,631 = 14,096. The remaining 10,951 must come from pre-202603 bills (not in query window). The system correctly stores previous_balance=25,047.

**Verdict**: Safe. previous_balance already written correctly.

---

### Bill 831 — Contract 15, 202606 — Category A (Control)

| Field | Legacy | New System |
|-------|--------|------------|
| rent | 4,500 | 4,500 |
| **total** | **22,654** | **22,654** |
| paid | 0 | 0 |
| created_at | 2026-06-05 16:13:10 | 2026-06-05 16:13:10 |
| previous_balance | N/A | **18,154** |

**Formula**: 4,500 + 0 + 0 + 0 + 0 = **4,500**
**Diff**: 22,654 − 4,500 = **+18,154** = previous_balance ✅

**Chain verification**: Contract 15 chain: bill 445 (202603, total=4,500, paid=None) → bill 170 (202605, total=22,654, paid=4,500) → bill 831 (202606, total=22,654). Bill 170's unpaid = 22,654 − 4,500 = 18,154. This exactly matches bill 831's previous_balance=18,154 ✅.

**Verdict**: Safe. previous_balance already written correctly. Chain integrity verified.

---

### Bill 832 — Contract 16, 202606 — Category B

| Field | Legacy | New System |
|-------|--------|------------|
| rent | 4,200 | 4,200 |
| **total** | **4,220** | **4,220** |
| paid | 0 | 0 |
| created_at | 2026-06-05 16:13:10 | 2026-06-05 16:13:10 |
| previous_balance | N/A | 0 |

**Formula**: 4,200 + 0 + 0 + 0 + 0 = **4,200**
**Diff**: 4,220 − 4,200 = **+20**

**Chain verification**: Contract 16 chain: bill 446 (202603, total=4,200, paid=None) → bill 171 (202605, total=4,520, paid=0) → bill 832 (202606). Bill 171's unpaid = 4,520. Expected previous_balance for bill 832 should be at least 4,520, but new system shows 0. The +20 gap is much smaller than the unpaid chain.

**Anomaly**: The +20 is too small to be a previous_balance and doesn't match the unpaid chain (4,520).

**Verdict**: Needs owner confirmation. The 20 gap is ambiguous — possibly a rounding residual.

---

### Bill 833 — Contract 17, 202606 — Category C

| Field | Legacy | New System |
|-------|--------|------------|
| rent | 4,800 | 4,800 |
| **total** | **4,789** | **4,789** |
| paid | 0 | 0 |
| created_at | 2026-06-05 16:13:10 | 2026-06-05 16:13:10 |
| previous_balance | N/A | 0 |

**Formula**: 4,800 + 0 + 0 + 0 + 0 = **4,800**
**Diff**: 4,789 − 4,800 = **−11**

**Chain verification**: Contract 17 chain: bill 447 (202603, total=4,800, paid=None) → bill 172 (202605, total=5,089, paid=0) → bill 833 (202606). Bill 172's unpaid = 5,089. Expected previous_balance should be at least 5,089, but new system shows 0. The −11 diff means the total is less than the rent alone.

**Anomaly**: **Negative diff**. The total (4,789) is less than the rent (4,800). This indicates the total was manually adjusted downward by 11, or the rent was entered incorrectly.

**Verdict**: Not a previous_balance issue. The total needs correction (should be at least 4,800).

---

### Bill 943 — Contract 125, 202605 — Category B

| Field | Legacy | New System |
|-------|--------|------------|
| rent | 6,500 | 6,500 |
| electricity_amount | 289 | 289 |
| public_electricity | 40 | 40 |
| water_amount | 18 | 18 |
| other_charges | None | None |
| **total** | **6,807** | **6,807** |
| paid | 0 | 0 |
| created_at | **NULL** | **1970-01-01 00:00:00** |
| previous_balance | N/A | 0 |

**Formula**: 6,500 + 289 + 40 + 18 + 0 = **6,847**
**Diff**: 6,807 − 6,847 = **−40**

**Chain verification**: Contract 125 has 6 bills (939→940→941→942→943→944). All paid=0. Unpaid sum before bill 943 = 26,370. The −40 diff does not match any unpaid amount.

**Anomaly**:
- `created_at=NULL` in legacy → mapped to `1970-01-01 00:00:00` in new system (epoch default)
- `other_charges=NULL` (not 0) — other_charges is nullable in legacy
- Diff = −40 = negative of `public_electricity` (40) — the total may have excluded the public electricity charge

**Verdict**: Needs owner confirmation. The −40 likely represents a manual adjustment where public_electricity was not included in the total. Needs verification.

---

## Accounting Chain Verification (Control Group)

### Contract 15 Chain (Bills 170 → 831)

| Bill | YM | Formula | Total | Previous Balance | Paid | Unpaid |
|------|------|---------|-------|-----------------|------|--------|
| 445 | 202603 | 4,500 | 4,500 | 0 | None | 4,500 |
| **170** | **202605** | **5,039** | **22,654** | **17,615** ✅ | **4,500** | **18,154** |
| **831** | **202606** | **4,500** | **22,654** | **18,154** ✅ | **0** | **22,654** |

- Bill 170's previous_balance (17,615) + formula (5,039) = total (22,654) ✅
- Bill 170's unpaid = 22,654 − 4,500 = 18,154
- Bill 831's previous_balance (18,154) = bill 170's unpaid ✅
- No double-counting detected ✅

### Contract 3 Chain (Bill 819)

| Bill | YM | Formula | Total | Previous Balance | Paid | Unpaid |
|------|------|---------|-------|-----------------|------|--------|
| 451 | 202603 | 4,465 | 4,465 | 0 | None | 4,465 |
| 158 | 202605 | 9,631 | 9,631 | 0 | 0 | 9,631 |
| **819** | **202606** | **4,663** | **29,710** | **25,047** ✅ | **0** | **29,710** |

- Bill 819's previous_balance (25,047) + formula (4,663) = total (29,710) ✅
- Visible unpaid before bill 819: 4,465 + 9,631 = 14,096
- Remaining 10,951 from pre-202603 bills (not in query window) — consistent with large previous_balance ✅
- No double-counting detected ✅

---

## Anomaly Summary

| Anomaly Type | Bills Affected | Details |
|-------------|----------------|---------|
| **Negative total** | 567 | total=−27,186; system error |
| **Negative diff** | 172, 833, 943 | Total < sum of fee components |
| **paid non-boolean** | 170 | paid=4,500 (numeric, equals rent) |
| **created_at=NULL** | 943 | All 6 bills in contract 125 |
| **other_charges=NULL** | 943 | Nullable in legacy, not in new system |
| **Large unexplained gap** | 573 | +5,663 ≈ rent but not exact match |

---

## Classification Summary

### Category A: Safe to Apply previous_balance (3 bills)

| Bill | Contract | YM | Previous Balance | Status |
|------|----------|------|-----------------|--------|
| 170 | 15 | 202605 | 17,615 | ✅ Already written |
| 819 | 3 | 202606 | 25,047 | ✅ Already written |
| 831 | 15 | 202606 | 18,154 | ✅ Already written |

All three have been verified: `previous_balance + formula = total` ✅. No action needed.

### Category B: Needs Owner Confirmation (5 bills)

| Bill | Contract | YM | Diff | Recommended previous_balance | Concern |
|------|----------|------|------|------------------------------|---------|
| 171 | 16 | 202605 | +78 | 0 (or 78?) | Gap too small to be meaningful |
| 573 | 27 | 202606 | +5,663 | 5,663? | Cannot verify against chain |
| 578 | 32 | 202606 | +213 | 0 (or 213?) | Gap too small to be meaningful |
| 832 | 16 | 202606 | +20 | 0 (or 20?) | Gap too small to be meaningful |
| 943 | 125 | 202605 | −40 | 0 | Diff may be manual adjustment |

**Recommended action**: Present these 5 bills to the owner with the diff values and ask whether the gap represents an intentional previous_balance or a data entry adjustment.

### Category C: Needs Correction (3 bills)

| Bill | Contract | YM | Issue | Recommended Action |
|------|----------|------|-------|-------------------|
| 172 | 17 | 202605 | total (5,089) < formula (5,144) by 55 | Correct total or verify manual adjustment |
| 567 | 21 | 202606 | total=−27,186 (negative); diff=−33,646 | **CRITICAL**: Correct total; system error |
| 833 | 17 | 202606 | total (4,789) < rent (4,800) by 11 | Correct total or verify manual adjustment |

**Note on bill 567**: This is a blocker. The negative total is a system error that must be resolved before any previous_balance can be determined. The correct total should be formula (6,460) + any legitimate previous_balance from unpaid chain.

---

## Risks

1. **Bill 567 negative total**: If corrected to a positive value, the previous_balance may be very large (up to ~33,646). Owner must verify the correct total.
2. **Bills 172/833 negative diffs**: These suggest the legacy operator manually adjusted totals downward. The new system should preserve the legacy total as-is (not recompute from components) to maintain historical accuracy.
3. **Bill 943 created_at=NULL**: All 6 bills in contract 125 have NULL created_at. The new system defaults to epoch (1970-01-01). This should be flagged for data cleanup.
4. **Bill 170 paid=4500**: Non-boolean paid value. The new system stores it as-is. This doesn't affect total calculation but should be documented.
5. **Chain gaps**: Several contracts have months with no bills (e.g., contract 15 skips April 2026). This is expected if bills weren't generated for those months, but means unpaid amounts from those months aren't tracked.

---

## Recommended Next Steps

1. **Immediate**: Present Category B bills (171, 573, 578, 832, 943) to owner for confirmation
2. **Immediate**: Investigate and correct bill 567 (negative total) — this is a blocker
3. **Low priority**: Verify bills 172 and 833 totals against legacy receipts/records
4. **Cleanup**: Address bill 943 created_at=NULL and other_charges=NULL
5. **Documentation**: Record decisions in ADR for future reference

---

*Report generated by agent/open-legacy-total-reconciliation-02. Read-only — no data was modified.*
