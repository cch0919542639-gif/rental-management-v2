# reasonix

Status: DONE
Last Updated: 2026-07-15

## Current Task
- ✅ R3 PropertyExpense + R6 MoveOutSettlement contract decision package frozen

## Scope
- 凍結 R3 PropertyExpense 與 R6 MoveOutSettlement 的資料契約決策包，不寫程式。

## Completed So Far
- ✅ 從 codex-phase2-mainline-01 建立 agent/reasonix-expense-moveout-contract-01
- ✅ 交付 docs/reports/reasonix-expense-moveout-contract-01.md
- ✅ 含最小欄位（R3: 14 columns, R6: 25 columns）、狀態機、金額公式、FK/ondelete、不可變規則
- ✅ 含 management fee、清潔費、維修費、欠款、押金扣抵/退款、結清付款邊界
- ✅ 含 Owner 必答決策 8 項（ADR-R01 ~ ADR-R08），含安全預設與後果
- ✅ 含 DIRECT / ADR_REQUIRED / FORBIDDEN 分類（12 FORBIDDEN items）
- ✅ 含實作前 Gate（8 checkpoints）與驗收標準（R3: 13 criteria, R6: 18 criteria）

## Verdict
- R3 PropertyExpense schema, migration, CRUD, report 皆為 DIRECT，可立即施工。
- R6 MoveOutSettlement schema, draft/finalized 為 DIRECT；closed 狀態需 ADR-R04/R05。
- 無程式碼變更，無 schema 修改，無 runtime-real.db 異動。

## Risks / Blockers
- ADR-R04（押金退款證據）與 ADR-R05（結清付款分攤）為 R6 closed 狀態的 Owner 阻塞項。
