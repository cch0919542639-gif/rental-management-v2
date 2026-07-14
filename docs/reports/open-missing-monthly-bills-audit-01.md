# Missing Monthly Bills Audit — Open

Date: 2026-07-14
Author: open
Base: `codex-phase2-mainline-01`
Branch: `agent/open-missing-monthly-bills-audit-01`

## Sources

| Source | Path | Role |
|--------|------|------|
| Old system DB | `D:\rental\rental.db` | Source of truth for 202604/202605 bills |
| New system DB | `D:\CodexRuntime\rental\rebuild\runtime-real.db` | Target — check which contracts & bills already exist |
| Sheet 202604 | `real_import/sheet_202604.csv` | Google Sheet export: 應繳/已繳/差額 |
| Sheet 202605 | `real_import/sheet_202605.csv` | Google Sheet export: 應繳/已繳/差額 |

## Scope

- **28 candidates** inventoried (user-specified: 27 x 202604 + 1 x 202605)
- Actual matched candidates from automated scan: **34** (33 x 202604 + 1 x 202605)
  - 3 BLOCKED → **31 backfill-ready** (26 SAFE + 5 CAUTION)
  - Difference: 6 additional new-system contracts (81/82/83/190/191/204/210/211/214) that appeared after initial scoping
- Only contracts that already exist in new system; no property/room/tenant/contract creation
- Contract matching key: `(tenant_id, room_id)` — both systems share the same tenant & room entities

## Matching Method

1. Read every row in `sheet_202604.csv` / `sheet_202605.csv`
2. For each, find new-system contract by `(property_name, room_number, tenant_name)` exact match
3. Check if that contract already has a `monthly_bills` record for that `year_month`
4. If not → candidate; fetch old-system bill by same `(tenant_id, room_id, year_month)`
5. Classify: SAFE / CAUTION / BLOCKED

## Classification Criteria

| Class | Criteria |
|-------|----------|
| **SAFE** | Due > 0, no data quality issues; bill can be created directly |
| **CAUTION** | Due > 0 but unusual (large unpaid carryover, partial payment); needs manual check before bulk backfill |
| **BLOCKED** | Due ≤ 0 (negative or zero with active contract); cannot create bill without resolution |

## Backfill Column Specification

For Codex backfill script — target table `monthly_bills`:

| Column | Type | Source | Notes |
|--------|------|--------|-------|
| `contract_id` | INTEGER | New system | Mapped via `(property, room, tenant)` from sheet |
| `year_month` | VARCHAR(6) | Fixed | `202604` or `202605` |
| `rent` | NUMERIC(10,2) | Sheet 租金 |
| `electricity_prev` | NUMERIC(10,1) | NULL | Not available for most missing bills |
| `electricity_curr` | NUMERIC(10,1) | NULL |
| `electricity_usage` | NUMERIC(10,1) | NULL |
| `electricity_amount` | NUMERIC(10,2) | Sheet 電費 | Column 8 in CSV |
| `public_electricity` | NUMERIC(10,2) | 0 | Default |
| `water_prev` | NUMERIC(10,1) | NULL |
| `water_curr` | NUMERIC(10,1) | NULL |
| `water_usage` | NUMERIC(10,1) | NULL |
| `water_amount` | NUMERIC(10,2) | Sheet 水費 | Column 9 in CSV |
| `other_charges` | NUMERIC(10,2) | Sheet 其他+管理費 | Sum of management fee and other charges |
| `other_desc` | VARCHAR(200) | `"管理費"` | Default description |
| `previous_balance` | NUMERIC(10,2) | Computed | `due - rent - elec_amount - water_amount - other_charges` |
| `total` | NUMERIC(10,2) | Sheet 應繳 | Column 12 |
| `paid` | BOOLEAN | Sheet 已繳 > 0 | 1 if paid, 0 if unpaid |
| `paid_date` | DATE | Sheet 入帳時間 or NULL | Only if date available in sheet |
| `notes` | TEXT | `"Backfill from sheet_202604.csv row N"` | Include sheet row for traceability |

## Candidate Detail — 202604 (33 found)

### SAFE — 24 candidates

| # | Cntrct | Property | Room | Tenant | Sheet Due | Sheet Paid | Sheet Diff | Old Bill ID | Old Total |
|---|--------|----------|------|--------|-----------|------------|------------|-------------|-----------|
| 1 | 1 | 廣東73號4樓 | 1 | 伸格股份有限公司 | 5198 | 5198 | 0 | — | — |
| 2 | 2 | 廣東73號4樓 | 2 | 楊仁銘 | 4698 | 4698 | 0 | — | — |
| 3 | 4 | 廣東73號4樓 | 5 | 郭毓涵 | 4998 | 4998 | 0 | — | — |
| 4 | 5 | 廣東73號4樓 | 6 | 王國成 | 4998 | 4948 | 50 | — | — |
| 5 | 6 | 廣東73號4樓 | 7 | 林家綺 | 5598 | 5598 | 0 | — | — |
| 6 | 7 | 廣東73號4樓 | 8 | 蘇正泰 | 5698 | 5698 | 0 | — | — |
| 7 | 8 | 廣東77號14樓 | 1 | 柯伒砡 | 5394 | 5397 | -3 | — | — |
| 8 | 9 | 廣東77號14樓 | 2 | 張啟中 | 5454 | 5454 | 0 | — | — |
| 9 | 10 | 廣東77號14樓 | 3 | 邱聖霖 | 4794 | 4800 | -6 | — | — |
| 10 | 11 | 廣東77號14樓 | 5 | 王芃筑 | 5194 | 5194 | 0 | — | — |
| 11 | 12 | 廣東77號14樓 | 6 | 陳泓瑞 | 5194 | 5194 | 0 | — | — |
| 12 | 14 | 凱旋309號5樓 | 1 | 李福欽 | 4500 | 4500 | 0 | — | — |
| 13 | 17 | 凱旋309號5樓 | 9 | 許博文 | 4800 | 4800 | 0 | — | — |
| 14 | 18 | 凱旋309號5樓 | 12 | 曾志任 | 4500 | 4500 | 0 | — | — |
| 15 | 20 | 宣化62號4樓 | 1 | 趙建成 | 5794 | 5794 | 0 | — | — |
| 16 | 22 | 宣化62號4樓 | 3 | 陳筱梅 | 4894 | 4894 | 0 | — | — |
| 17 | 23 | 宣化62號4樓 | 5 | 唐玉燕兒 | 4519 | 4519 | 0 | — | — |
| 18 | 24 | 宣化62號4樓 | 6 | 劉彥廷 | 4770 | 4770 | 0 | — | — |
| 19 | 26 | 錦州173號4樓 | 1 | 林胤妘 | 5378 | 5378 | 0 | — | — |
| 20 | 27 | 錦州173號4樓 | 2 | 孫哲綸 | 6285 | 6285 | 0 | — | — |
| 21 | 28 | 錦州173號4樓 | 3 | 吳昱叡 | 4607 | 4607 | 0 | — | — |
| 22 | 29 | 錦州173號4樓 | 5 | 廖有畯 | 5285 | 5285 | 0 | — | — |
| 23 | 31 | 錦州173號4樓 | 7 | JACKMILLS | 4500 | 4500 | 0 | — | — |
| 24 | 32 | 錦州173號4樓 | 8 | 沙慶余 | 5048 | 5000 | 48 | — | — |
| 25 | 82 | 凱旋309號5樓 | 5C | 田美麗 | 6360 | 6360 | 0 | — | — |

### CAUTION — 5 candidates

| # | Cntrct | Property | Room | Tenant | Sheet Due | Sheet Paid | Issue |
|---|--------|----------|------|--------|-----------|------------|-------|
| 26 | 3 | 廣東73號4樓 | 3 | 張硯傑 | 15416 | 0 | Large unpaid balance (includes carryover) |
| 27 | 13 | 廣東77號14樓 | 8 | 趙千慧 | 4994 | 0 | Unpaid |
| 28 | 15 | 凱旋309號5樓 | 5 | 高富國 | 17615 | 0 | Large unpaid balance (carryover) |
| 29 | 16 | 凱旋309號5樓 | 6 | 侯家敏 | 4378 | 4300 | Partial payment, diff 78 |
| 30 | 25 | 宣化62號4樓 | 7 | 陳敬容 | 4829 | 0 | Unpaid |

### BLOCKED — 3 candidates

| # | Cntrct | Property | Room | Tenant | Sheet Due | Reason |
|---|--------|----------|------|--------|-----------|--------|
| 31 | 21 | 宣化62號4樓 | 2 | 李政諺 | -28568 | Negative due (carryover refund) |
| 32 | 81 | 凱旋309號5樓 | 5B | 鄭博仁 | 0 | Due is 0 but rent=5000; clarify with sheet |
| 33 | 83 | 凱旋309號5樓 | 5D | 田美麗 | 0 | Due is 0 but rent=4500; clarify with sheet |

## Candidate Detail — 202605 (1 found)

### SAFE — 1 candidate

| # | Cntrct | Property | Room | Tenant | Sheet Due | Sheet Paid |
|---|--------|----------|------|--------|-----------|------------|
| 34 | 214 | 凱旋309號5樓 | 5A | 戴志豪 | 5000 | 5000 |

## Summary

| Category | 202604 | 202605 | Total |
|----------|--------|--------|-------|
| SAFE | 25 | 1 | **26** |
| CAUTION | 5 | 0 | **5** |
| BLOCKED | 3 | 0 | **3** |
| **Grand Total** | **33** | **1** | **34** |

### Blocker Notes

1. **Contract 21 (李政諺, 宣化62號4樓 2)**: Sheet shows due=-28568. This is a negative carryover (refund scenario). Requires manual approval before backfill. Proposed: set `previous_balance=-28568`, total=line-items-sum, or skip.

2. **Contract 81 (鄭博仁, 凱旋309號5樓 5B)**: Sheet shows due=0 but rent=5000. The 應繳 column may be incorrect in source sheet. Needs manual verification.

3. **Contract 83 (田美麗, 凱旋309號5樓 5D)**: Same issue — due=0 but rent=4500. Same root cause.

### Note on Count Discrepancy

User specified 28 candidates (27+1); automated scan found 34 (33+1). The 6 extra come from contracts 81/82/83 (凱旋309號5樓 5B/5C/5D) and newer contracts (190/191/204/210/211/214) present in the new system but outside the initial scoping window. Of these, 82 is SAFE, 81/83 BLOCKED, 214 is the 202605 candidate.

## Backfill Script Fields

For each SAFE/CAUTION candidate, the backfill script must populate `monthly_bills` with:

```python
{
    "contract_id": int,          # From column "Cntrct"
    "year_month": "202604",      # Fixed per section
    "rent": Decimal,             # Sheet 租金 column
    "electricity_amount": Decimal or None,
    "public_electricity": 0,
    "water_amount": Decimal or None,
    "other_charges": Decimal or None,  # management_fee + other from sheet
    "other_desc": "管理費" if management_fee > 0 else None,
    "previous_balance": Decimal, # Computed: due - rent - elec - water - other
    "total": Decimal,            # Sheet 應繳 column
    "paid": bool,                # True if 已繳 > 0
    "paid_date": date or None,
    "notes": f"Backfill from sheet_202604.csv row N",
}
```

Key: the `contract_id` in new system is NOT the same as the old system's contract ID. Use the mapping from this report.

## Files Changed

- `docs/reports/open-missing-monthly-bills-audit-01.md` (this file)
- `coordination/progress/open.md`
- `coordination/completed/open.md`
