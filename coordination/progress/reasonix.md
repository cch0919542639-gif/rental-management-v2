# reasonix

Status: IN PROGRESS
Last Updated: 2026-07-14

## Current Task
- 🔄 審查「既有 contract 的歷史月帳單回填」契約與風險守門
- Branch: `agent/reasonix-missing-monthly-bills-guard-01`

## Scope
- 審查 202604 的 27 筆與 202605 的 1 筆缺漏月帳單回填
- 回填僅可使用 Google Sheet 已存在證據
- 產出 DIRECT/CAUTION/FORBIDDEN 分類與 stop conditions

## Completed So Far
- ✅ 讀取 billing model、data contract、sheet CSVs、prior reconciliation incidents
- ✅ 分析 sheet_202604.csv (154 rows) 與 sheet_202605.csv (154 rows) 欄位結構
- ✅ 比對 runtime-real.db 既有 monthly_bills (Batch 1: 191, Batch 2: 200)
- ✅ 產出 guard report: docs/reports/reasonix-missing-monthly-bills-guard-01.md

## Classification Summary
- DIRECT: 8 fields
- CAUTION: 9 fields (含 9 個 stop conditions)
- FORBIDDEN: 5 fields

## Key Blockers Identified
- B1: 202604 previous_balance 缺乏 Sheet 未收款欄位 (HIGH)
- B3: total 公式驗證偏差 >10 需手動調查 (HIGH)
- B2: Sheet 租金 vs contract.rent 差異 >100 需手動確認 (MEDIUM)

## Risks / Blockers
- 見 guard report §10
