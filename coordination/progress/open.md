# open

Status: DONE
Last Updated: 2026-07-14

## Current Task
- Expense & Move-Out Settlement source audit (R3/R6)

## Deliverables
- `docs/reports/open-expense-moveout-source-audit-01.md`

## Summary
- Scanned old system DB (18 tables), Google Sheet CSVs (202604/202605/202606), new system DB (empty)
- R3 PropertyExpense: DIRECT=8, CAUTION=4, BLOCKED=5 — only `utility` (electricity_bills) has source data
- R6 MoveOutSettlement: DIRECT=9, CAUTION=5, BLOCKED=7 — 6 terminated contracts but all settlement fields empty
- 7 questions raised for Owner (deposit, cleaning, repair, move-out dates, prorated rent)
- Hard blockers: no cleaning/repair/deposit/refund data anywhere in old system

## Next Step
- Owner answers Q1–Q7 before R6 can be imported
- R3 utility expenses (11 electricity_bills) can be imported after R3 model deployment
