# Phase 3 Kickoff Checklist

Date: 2026-06-29
Owner: Codex
Prerequisite: `phase2-final-summary-2026-06-29.md`

## Goal

這份清單用來在進入 Phase 3 前確認：

- 先做哪個主題
- 哪些工作可以平行分派
- 哪些工作仍需 ADR
- 哪些工作不應提早做

## Candidate Phase 3 Themes

### Option A — Water Preview

Scope:

- `POST /water/preview`
- preview template / validation / presentation

Why start here:

- 低風險
- 使用者可見
- 不需要外部 API

Good for:

- 先拿一個小而完整的 Phase 3 功能

### Option B — PaymentRecords API Boundary

Scope:

- internal API-style route for payment records
- read / create boundary only
- no external provider calls

Why start here:

- 延續已存在的 `PaymentRecord`
- 為後續 OCR / webhook 做準備

Good for:

- 下一階段要往 integration 實作走

### Option C — Migration Write Path

Scope:

- `contract_expiry_repair.py --execute` path hardening
- more write-safe repair / normalization scripts
- optional dry-run + execute conventions

Why start here:

- 為正式資料導入做前置

Good for:

- 接下來要碰真實資料遷移

## Recommended Order

1. `water preview`
2. `payment-records API boundary`
3. `migration write path`
4. OCR / Sheets / LINE real integrations

## Parallelizable Work

### Can Be Parallelized

- `open`
  - Phase 3 gap check / route inventory for selected theme
- `mimo`
  - UI regression / placeholder copy / empty-state review
- `box/hermes`
  - tests / runbook / script usage docs

### Should Stay With Codex

- model changes
- service formula changes
- write-capable migration scripts
- integration boundary to real implementation transition

## ADR Gates

Phase 3 still should not bypass these:

- OCR provider selection
- LINE webhook auth strategy
- OCR result → `PaymentRecord` auto-create policy
- virtual tenant → `MaintenanceRequest` write conversion

## Ready Checklist

Before starting a Phase 3 theme:

- [ ] Selected one theme only
- [ ] Updated `coordination/progress/codex.md`
- [ ] Confirmed tests baseline still green
- [ ] Wrote new dispatch text if other agents will help
- [ ] Confirmed whether the theme is boundary-only or write-capable

## Suggested Agent Split By Theme

### If Theme = Water Preview

- Codex: route / service / template implementation
- mimo: preview UI regression
- box/hermes: preview tests + runbook
- open: route gap follow-up

### If Theme = PaymentRecords API Boundary

- Codex: API route + serializer + boundary logic
- open: API gap check
- mimo: no primary role unless API gets debug UI
- box/hermes: API test coverage + docs

### If Theme = Migration Write Path

- Codex: write-safe script implementation
- reasonix: ADR / guard review if write scope expands
- box/hermes: runbook + dry-run / execute docs
- open: audit output inventory only

## Not To Start Yet

- Real OCR client implementation
- Real LINE webhook processing
- Google Sheets OAuth flow
- Email / SMS notifications
- Background job scheduler

