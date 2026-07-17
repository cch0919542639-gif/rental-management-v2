# reasonix

Status: IN_PROGRESS — ADR-R05 退租結清付款分攤決策
Last Updated: 2026-07-17

## Current Task
- 撰寫並提交 ADR-R05「退租結清付款分攤」決策文件，交付 Owner 審閱。

## Scope
- 比較「不可拆分付款」、「單筆付款拆分到最後一期帳單與結清單」、「獨立 allocation table 分攤」三種方案。
- 說明對 PaymentRecord、稽核、退款、重複交易編號與未收款報表的影響。
- 給出建議方案（Option C: 獨立 PaymentAllocation 表）與驗收標準。
- 明確列出禁止事項。

## Completed So Far
- ✅ 分析現有 PaymentRecord 模型、狀態機、對帳服務
- ✅ 分析 R6 MoveOutSettlement 最小契約中的 paid_amount / outstanding_amount 語義
- ✅ 評比三種方案並產出建議
- ✅ docs/reports/reasonix-moveout-payment-allocation-adr-01.md

## Verdict
- 推薦 Option C（獨立 PaymentAllocation 表）。在不破壞現有 PaymentRecord 的前提下，提供明確稽核軌跡並支援靈活分攤。

## Risks / Blockers
- ADR 尚待 Owner 審閱批准。批准前 R6 MoveOutSettlement 的 paid_amount 不可自動化。
- 相依於 ADR-R04（押金退款證據）和 ADR-R06（結清前合約狀態規則），此三者共同決定 R6 最終化條件。
