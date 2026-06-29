# 給 reasonix 的派工指令

你現在負責 **Phase 2 migration path + integration boundary review**。  
這次不要直接改主幹程式碼，重點是幫 Codex 把可直接施工的 migration 與 integration 邊界再收斂一次。

## 你的目標

產出一份短而準的守門報告，明確區分：

- 哪些 migration 可以直接做
- 哪些必須先 ADR
- 哪些禁止直接做
- 哪些 integration 前置只到 boundary 即可，不應先落實外部串接

## 先讀

- `D:\CodexRuntime\rental\rebuild\coordination\progress\codex.md`
- `D:\CodexRuntime\rental\rebuild\docs\operations\phase2-parallel-dispatch-index-2026-06-29.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-phase2-contract-notes-01.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-maintenance-review-02.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-maintenance-migration-guard-03.md`
- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-maintenance-followup-04.md`

## 直接交付

請直接建立並填寫：

- `D:\CodexRuntime\rental\rebuild\docs\reports\reasonix-phase2-migration-integration-06.md`

## 你必須回答的內容

至少整理這 6 段：

1. Executive Summary
2. Migration: Direct / ADR / Forbidden
3. Integration Boundary: Direct / ADR / Forbidden
4. 目前主幹可安全新增的 script 類型
5. 目前主幹不可先做的外部串接類型
6. 給 Codex 的實作優先順序建議

## 必查範圍

- `user` / `users`
- `year_month` normalization
- virtual tenant cleanup
- `Room.status` normalization
- `Contract.status` expiry repair
- `scripts/migration/` 與 runbook 對 migration 的入口
- payment / OCR / external integration 目前最多能做到哪一層

## 明確限制

- 不要改 code
- 不要新增 schema
- 不要自行放寬已凍結契約
- 不要把外部 integration 細節當成現在必做項

## 工作紀錄要求

- 開工前更新 `D:\CodexRuntime\rental\rebuild\coordination\progress\reasonix.md`
- 完成後更新 `D:\CodexRuntime\rental\rebuild\coordination\completed\reasonix.md`

## 如果卡住

遇到以下情況立刻回報：

- 某 migration 需要動到未凍結欄位
- integration boundary 無法只靠既有契約決定
- 現有文件彼此矛盾

回報方式：

- 新增 `D:\CodexRuntime\rental\rebuild\coordination\incidents\<timestamp>_reasonix_<topic>.md`
- 把 `progress/reasonix.md` 狀態改成 `NEEDS-DECISION`

