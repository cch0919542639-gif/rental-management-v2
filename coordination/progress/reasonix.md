# reasonix

Status: DONE — ADR-R05 退租結清付款分攤決策
Last Updated: 2026-07-17

## Current Task
- ✅ ADR-R05「退租結清付款分攤」決策文件已提交，Owner 已批准 Option C。

## Scope
- 比較「不可拆分付款」、「單筆付款拆分到最後一期帳單與結清單」、「獨立 allocation table 分攤」三種方案。
- 說明對 PaymentRecord、稽核、退款、重複交易編號與未收款報表的影響。
- Owner 批准 Option C（獨立 PaymentAllocation 表）並確認驗收標準。
- 明確列出禁止事項。

## Completed So Far
- ✅ 分析現有 PaymentRecord 模型、狀態機、對帳服務
- ✅ 分析 R6 MoveOutSettlement 最小契約中的 paid_amount / outstanding_amount 語義
- ✅ 評比三種方案
- ✅ Owner 審閱並選擇 Option C
- ✅ docs/reports/reasonix-moveout-payment-allocation-adr-01.md（Status: Approved）

## Verdict
- Owner 批准 Option C（獨立 PaymentAllocation 表）。在不破壞現有 PaymentRecord 的前提下，提供明確稽核軌跡並支援靈活分攤。

## Risks / Blockers
- R6 MoveOutSettlement 的 paid_amount 自動化仍相依於 ADR-R04（押金退款證據）和 ADR-R06（結清前合約狀態規則）。
- PaymentAllocation 表實作需等 R6 模型就位後進行。
