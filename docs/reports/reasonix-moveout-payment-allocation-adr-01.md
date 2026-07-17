# Architecture Decision: ADR-R05 — 退租結清付款分攤

**Date:** 2026-07-17
**Author:** reasonix
**Status:** Proposed
**References:**
- `docs/reports/reasonix-reporting-expansion-contract-01.md` (ADR-R05 定義來源)
- `data_contracts/payments-contract.md`
- `data_contracts/billing-contract.md`
- MoveOutSettlement minimum contract (`reasonix-reporting-expansion-contract-01.md` § Direct Items)
- `app/models/billing.py` (PaymentRecord / MonthlyBill)

## Executive Summary

- 退租結清場景下，一筆銀行轉帳可能同時覆蓋最後一期月帳單未繳部分與結清單額外費用。現有 `PaymentRecord` 僅支援一對一連結 `monthly_bill_id`，無法表達此種分攤。
- 比較三種方案後，推薦 **Option C：獨立 PaymentAllocation 分攤表**，因其在不變更現有 PaymentRecord 契約的前提下提供明確稽核軌跡、支援任意目標組合，且與現有架構的分層原則一致。
- 此決策只定義資料模型與分攤規則；不涉及結清單最終化條件、押金退款證據、或退款付款處理（屬 ADR-R04、ADR-R06 範圍）。

## Confirmed Facts

- `PaymentRecord` 目前透過 `monthly_bill_id` FK 一對一連結 `MonthlyBill`；另有可選 `contract_id` FK。
- `PaymentRecord.record_status` 狀態機：`pending → verified → linked`、`pending → rejected`。`linked` 表示已連結帳單。
- `PaymentReconciliationService.is_bill_paid()` 以 `SUM(PaymentRecord.amount) WHERE record_status='linked' AND monthly_bill_id=... >= MonthlyBill.total` 判定繳清。
- R6 `MoveOutSettlement` 最小契約已定義 `paid_amount`、`outstanding_amount`、`final_monthly_bill_id`。
- `MoveOutSettlement` 的 `gross_charges = final_rent + electricity_amount + water_amount + management_fee + previous_debt + cleaning_fee + repair_fee + other_charge`。
- `settlement_due = gross_charges - deposit_applied`；`outstanding_amount = max(settlement_due - paid_amount, 0)`。
- 現有 `PaymentRecord.transaction_id` 有唯一性約束（create 時檢查重複）。
- 退租日期已有人工確認紀錄（`docs/operations/move-out-date-confirmations-20260715.md`，5 筆）。

## Inferences

- 若不做分攤，退租場景需要兩筆 `PaymentRecord`（一筆對月帳單、一筆對結清單），但實際銀行轉帳只有一筆交易編號，重複建立會違反 `transaction_id` 唯一約束或迫使運營人員拆分金額。
- 若將 `MoveOutSettlement.paid_amount` 以獨立 PaymentRecord 記錄而不連結月帳單，會導致最後一期月帳單在 `MonthlyBill.paid` 欄和 R1/R2/R5 報表中永遠顯示未繳。
- 現有 `monthly_bill_id` FK 在結清場景中語義模糊：付款到底是付月帳單還是付結清單，還是兩者皆有。

## Problem Statement

- 同一筆銀行交易可能同時清償最後一期月帳單餘額和結清單應收款，現有 `PaymentRecord` 模型無法表達一對多的分攤關係。
- 若強制拆分為多筆 `PaymentRecord`，會導致交易編號重複、金額拆分無稽核記錄、退款對帳困難。
- R6 結清單的 `paid_amount` 與 `outstanding_amount` 在無分攤機制下無法自動化計算，只能人工填入。

## Current Risks

### P0

- 若未定義分攤規則就實作 R6 結清，`paid_amount` 將只能由人工填入，與 `PaymentRecord` 脫鉤，報表無法對帳。
- 最後一期月帳單的 `paid` 狀態可能與結清付款不一致，導致 R1/R2/R5 報表資料失真。

### P1

- 若選擇修改 `PaymentRecord.amount` 語義（拆成多個子金額），會破壞現有 OCR→審核→對帳流程中金額欄位的唯一性。
- 若用 `other_charges` 或 `notes` 承載分攤資訊，稽核無法追溯。

### P2

- 若結清付款與月帳單連結在不同時間點被不同操作員處理，可能出現同一筆付款被重複連結到不同目標。

## Options

### Option A: 不可拆分付款 — 付款僅能連結月帳單或結清單其中之一

`PaymentRecord` 維持現狀：`monthly_bill_id` 與日後可能的 `settlement_id` 互斥。退租時需建立兩筆獨立 `PaymentRecord`（共用相同 `transaction_id` 需放寬唯一約束，或拆分交易編號命名規則）。

**Pros:**
- 無需任何 schema 變更。
- `PaymentRecord` 語義不變。

**Cons:**
- 退租結清一律需要拆分付款記錄，增加運營負擔。
- 拆分後的兩筆記錄之間的關聯僅靠人工備註或命名慣例，無正式約束。
- 報表難以區分「月帳單還款」與「結清攤付」。

**Risks:**
- `transaction_id` 唯一約束必須放寬，但放寬後可能引入真正的重複交易。

### Option B: 單筆付款可拆分到最後一期帳單與結清單

在 `PaymentRecord` 上增加 `settlement_id` FK 和 `allocated_to_bill` / `allocated_to_settlement` 金額欄位，使一筆 PaymentRecord 同時指向一個月帳單和一個結清單。

**Pros:**
- 無需新表，schema 變更最小（加 2-3 個欄位）。
- 單筆付款直接表達分攤意圖。

**Cons:**
- `PaymentRecord` 語義從「一筆付款對應一個目標」變成「一筆付款可對應兩個目標」，但未來若需要分攤到更多目標（如多期欠款），仍須再次擴展。
- 月帳單對帳邏輯（`linked_amount_for_bill`）需要改寫，分兩欄加總。
- 退款場景下，結清單退款與月帳單退款的歸屬模糊。

**Risks:**
- 此設計將付款分攤邏輯嵌入 PaymentRecord 本身，未來若有更複雜的分攤需求（如一筆付款覆蓋多期帳單 + 結清單），schema 需再次 migrate。

### Option C: 以獨立 PaymentAllocation 表分攤（推薦）

新增 `PaymentAllocation` 表，每筆付款可產生多條 allocation row，每條指向一個目標（`MonthlyBill` 或 `MoveOutSettlement`），並記錄分配金額。

```
PaymentAllocation
├── id
├── payment_record_id  FK → payment_records.id
├── target_type        ENUM('monthly_bill', 'move_out_settlement')
├── target_id          多態 FK（依 target_type 決定指向哪張表）
├── allocated_amount   此筆分攤金額
├── created_at
```

`PaymentRecord` 新增 `record_status = 'allocated'`（替代或擴展 `linked`，表示付款已分攤完畢）。

**Pros:**
- `PaymentRecord` 本身契約不變：`amount` 仍為原始付款金額，`monthly_bill_id` 可保留為向後相容的快捷欄位。
- 分攤與付款解耦：一筆付款可以有任意數量、任意類型的目標分攤。
- 稽核軌跡清晰：每筆 allocation 有獨立 row，可追溯、可作廢、可重新分攤。
- 總額不變式可在 DB 層或 service 層強制執行：SUM(allocation.allocated_amount) <= PaymentRecord.amount。
- 未來若引入「部分退款」或「多期欠款攤還」，無需再次擴展 PaymentRecord。

**Cons:**
- 新增一張表與對應 repository/service。
- 現有 `PaymentReconciliationService` 和報表查詢需調整，從直接查 `PaymentRecord.monthly_bill_id` 改為透過 allocation 查。
- `MoveOutSettlement` 的 `paid_amount` 衍生邏輯需多一層 join。

**Risks:**
- 多態 FK（`target_type` + `target_id`）在 SQLite 無原生 ENUM 或 FK constraint，需在 service 層做強驗證。
- 現有 `linked` 狀態與新的 `allocated` 狀態之間的遷移相容期需要明確定義過渡規則。

## Decision

- **Selected Option: C — 獨立 PaymentAllocation 表分攤**
- **Why:**
  1. 最小侵入：`PaymentRecord` 模型不變，現有 API / OCR / 審核流程不受影響。
  2. 稽核優先：每筆分攤有獨立行，可追溯每筆付款流向哪個帳單或結清單，符合 `data_contracts/payments-contract.md` 中「同一筆付款記錄的來源、辨識結果、人工審核、帳單連結都能追溯」的要求。
  3. 未來擴展性：支援任意數量的分攤目標，不需要再次遷移。
  4. 符合現有架構的分層原則（model / repository / service），不將分攤邏輯內嵌於單一實體。
  5. Option A 在退租場景強制拆分記錄，增加運營錯誤風險。Option B 將分攤邏輯嵌入 PaymentRecord，在更複雜的場景（多期欠款 + 結清）下仍須再次擴展。

## Scope Included

- 建立 `PaymentAllocation` 模型與遷移腳本（`target_type` 為字串、`target_id` 為整數、`allocated_amount` 為正數）。
- `PaymentRecord` 新增 `record_status = 'allocated'`：當 `SUM(allocation.allocated_amount) == PaymentRecord.amount` 時，狀態可從 `linked`/`verified` 轉為 `allocated`。
- `PaymentAllocation` 不變式：
  - `allocated_amount > 0`
  - 同一 `payment_record_id` 下，`SUM(allocated_amount) <= PaymentRecord.amount`
  - `(target_type, target_id)` 指向存在的 `MonthlyBill` 或 `MoveOutSettlement`
- 報表 R1/R2/R5 的「已繳」計算，改為透過 `PaymentAllocation` 查 `target_type='monthly_bill'` 的分攤總和。
- `MoveOutSettlement.paid_amount` 由 service 從 `PaymentAllocation WHERE target_type='move_out_settlement'` 衍生。
- 結清工作流：可將一筆 `PaymentRecord` 拆分到最後一期月帳單和結清單（各一筆 allocation），並在分配完畢後將 PaymentRecord 標記為 `allocated`。
- 現有 `monthly_bill_id` FK 在 `PaymentRecord` 上保留為向後相容的快捷欄位；當存在對應 allocation 時，該欄位值應與 allocation 一致。

## Scope Excluded

- 不實作「部分退款」的分攤反向操作（退款屬 ADR-R04 範圍，需 Owner 另外決策後定義）。
- 不修改 `MonthlyBill.paid` 的計算公式邏輯（仍以 `linked_amount_for_bill` ≥ total 判定），但 `linked_amount_for_bill` 的來源改為查 allocation。
- 不在此 ADR 定義 `MoveOutSettlement` 的最終化條件（屬 ADR-R06）。
- 不實作 allocation 的審核流程或雙人簽核。
- 不支援跨合約的分攤（結清單始終關聯單一合約）。

## Forbidden Implementations

1. **禁止**在 `PaymentRecord` 上用字串拼接或 JSON 欄位承載分攤資訊（如 `"bill:8000,settlement:2000"`）。
2. **禁止**以負數 `PaymentRecord` 記錄退款或押金退還。
3. **禁止**用 `PaymentRecord.notes`、`status_text` 或其他自由文字欄位替代正式 allocation 記錄。
4. **禁止**讓 `PaymentAllocation.allocated_amount` 超過 `PaymentRecord.amount` 或為負值。
5. **禁止**在 allocation 存在後仍僅依 `PaymentRecord.monthly_bill_id` FK 計算報表已繳金額，必須改以 allocation 為準。
6. **禁止**將結清付款分攤資料存入 `MonthlyBill.other_charges`、`MonthlyBill.notes` 或 `Contract.notes`。
7. **禁止**跨合約建立 allocation（同一筆 PaymentRecord 的所有 allocation 必須指向同一 `contract_id` 下的月帳單/結清單）。

## Acceptance Criteria

Owner 可直接用以下標準驗收此決策是否可接受：

1. **一筆付款可分攤到最後一期月帳單與結清單**：在 UI / API 上能為同一筆 `PaymentRecord` 建立兩筆 allocation（一筆 `target_type=monthly_bill`、一筆 `target_type=move_out_settlement`），金額合計不超過付款金額。
2. **報表金額一致性**：R1 物件收租明細的「已繳」欄從 allocation 計算，與月帳單對帳結果一致。R5 年度統計亦使用相同來源。
3. **稽核可追溯**：每筆 allocation 有獨立建立時間，能回答「這筆銀行匯款中，多少錢去了哪張帳單、多少錢去了結清單」。
4. **重複交易編號防護**：同一 `transaction_id` 仍只允許一筆 `PaymentRecord`，分攤不影響此約束。
5. **不破壞現有流程**：現有 `create → verify → link` 流程在純月帳單場景下行為不變；`link` 時自動建立一筆 `target_type=monthly_bill` 的 allocation 作為預設行為。
6. **結清單 paid_amount 自動化**：當結清單存在對應 allocation 後，`paid_amount` 不應再由人工輸入，而是由 service 計算。

## Required Migration Work

1. 建立 `payment_allocations` 表。
2. 為現有 `record_status='linked'` 的 PaymentRecord 補建對應 allocation row（`target_type='monthly_bill'`、`allocated_amount = PaymentRecord.amount`），確保報表查詢切換時不出現遺漏。
3. `MoveOutSettlement` 模型新增後，其 `paid_amount` 欄位改為 derived/computed，不允許直接寫入。
4. 報表查詢逐步從直接讀 `PaymentRecord.monthly_bill_id` 切換為讀 allocation。

## Rollback Strategy

- `PaymentAllocation` 表與 `PaymentRecord` 完全獨立，rollback 可直接 drop 該表並回復報表查詢至原有邏輯。
- 在 allocation 過渡期，`PaymentRecord.monthly_bill_id` FK 保留不刪，報表可並行讀取兩邊並比對差異，確認無誤後再切換。
