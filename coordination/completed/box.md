# box Completed Log — Round 02 (Missing Monthly Bills Backfill)

Completed Time: 2026-07-14  
Branch: `agent/box-safe-monthly-backfill-01`  
Author: box (tests / scripts / runbook agent)

---

## Summary

Created dry-run-first backfill script for missing historical MonthlyBill rows (202604/202605). Script implements 9 stop conditions, maps Sheet rows to DB contracts via property→room→contract chain, and caps processing to 25 approved safe candidates (24 × 202604 + 1 × 202605).

**pytest: 60 passed, 15 skipped, 0 failures** (was 50; +10 new tests)

---

## Deliverables

| File | Action | Description |
|------|--------|-------------|
| `scripts/repair/backfill_missing_monthly_bills.py` | Created | Dry-run-first backfill script with 9 stop conditions |
| `tests/integration/test_backfill_missing_monthly_bills.py` | Created | 10 tests: dry-run, execute, rerun, skip-list, virtual, rent diff, total diff, 202605 pb, no property, rent=0 |
| `scripts/repair/README.md` | Updated | Added backfill script entry + usage examples |

## Dry-Run Results (runtime-real.db)

| Year-Month | SAFE | SKIP | STOP | Created |
|------------|------|------|------|---------|
| 202604 | 24 | 129 | 0 | 0 (dry-run) |
| 202605 | 1 | 152 | 0 | 0 (dry-run) |

### 202604 SAFE Candidates (24)

伸格股份有限公司, 楊仁銘, 郭毓涵, 王國成, 林家綺, 蘇正泰, 柯伒砡, 王芃筑, 陳泓瑞, 趙千慧, 李福欽, 許博文, 曾志任, 趙建成, 陳筱梅, 唐玉燕兒, 劉彥廷, 陳敬容, 林胤妘, 孫哲綸, 吳昱叡, 廖有畯, JACKMILLS, 沙慶余

### 202605 SAFE Candidate (1)

吳慧娟 (contract 214, 苓中路33巷 5A)

## Constraints Honored

- ✅ No schema, model, service, route, or template modifications
- ✅ Dry-run by default; `--execute` required to persist
- ✅ `paid=False`, `paid_date=None` on all created bills
- ✅ `total` recalculated via `MonthlyBill.calculate_total()`
- ✅ 202604: `previous_balance=0`, notes includes "前期差額無證據，設為0"
- ✅ 202605: `previous_balance` from Sheet 未收款 column
- ✅ Stop conditions: rent diff >100, total diff >10, virtual tenant, stop-list, duplicate, no contract, rent=0
- ✅ No PaymentRecord creation
- ✅ All stop-list tenants skipped: 張硯傑, 張啟中, 邱聖霖, 高富國, 侯家敏, 李政諺, 何佾洋, 鄭博仁, 田美麗