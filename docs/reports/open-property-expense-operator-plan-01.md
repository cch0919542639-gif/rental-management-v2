# PropertyExpense 操作計畫 01 — 人工支出與歷史資料規則

Author: open
Branch: `agent/open-property-expense-operator-plan-01`
Date: 2026-07-17
Baseline: `codex-phase2-mainline-01`
Contract: `reasonix-reporting-expansion-contract-01.md` (PropertyExpense 最小契約已確立)

---

## 1. 適用範圍

本計畫規範 **PropertyExpense 操作流程**，不涉及資料模型、遷移、API、UI、測試或資料庫結構變更。所有規則以 `reasonix-reporting-expansion-contract-01.md` 已確立的 PropertyExpense 欄位、狀態機、不變量為基礎，僅補充操作面規則。

---

## 2. 新增人工支出的最低必要資料與憑證規則

### 2.1 必要欄位

| 欄位 | 規則 |
| --- | --- |
| `property_id` | 必填。支出歸屬的物件。 |
| `transaction_date` | 必填。支出發生日期，不得為未來日期（容許當日）。系統由此推導 `year_month`。 |
| `category` | 必填。受控值：`management_fee`, `utility`, `cleaning`, `repair`, `tax`, `insurance`, `supplies`, `other`。 |
| `amount` | 必填。正數金額，精確儲存。 |
| `payee` | 建議填寫。收款方名稱或統編。 |
| `reference_no` | 建議填寫。外部憑證號碼（發票、收據、轉帳序號）。 |
| `notes` | 建議填寫。支出用途說明。 |
| `record_status` | 系統自動設為 `draft`。 |
| `created_by_id` | 系統自動填入操作者。 |

### 2.2 憑證規則（Voucher Rules）

| 類別 | 最低憑證要求 | 備註 |
| --- | --- | --- |
| `management_fee` | 管理合約或房東書面通知 | 若依比例計算，須附計算說明。 |
| `utility` | 帳單掃描／拍照／截圖 | 電費、水費、瓦斯等公共事業帳單。 |
| `cleaning` | 收據或請款單 | 清潔完成證明。 |
| `repair` | 估價單 + 完工收據 | 單筆 > 3000 須附估價單。 |
| `tax` | 稅單或繳款證明 | 房屋稅、地價稅等。 |
| `insurance` | 保單或繳費收據 | 火險、公共意外險等。 |
| `supplies` | 採購單據或發票 | 單筆 > 1000 須附明細。 |
| `other` | 說明 + 佐證文件 | 須在 notes 詳述支出原因。 |

- 憑證以附件形式上傳（檔案或圖片），非必填但建議上傳；`draft` → `posted` 前系統不強制檢查附件。
- 無任何憑證的支出僅允許 `draft` 狀態，不得 `posted`。
- **手動輸入（人工支出）**：所有類別均可由使用者手動建立，不受類別限制。

---

## 3. 舊系統僅 11 筆 utility 資料的安全匯入前置條件

### 3.1 背景

舊系統遺留 11 筆資料，全數屬於 `utility` 類別。這些是唯一承認的歷史支出來源。其他類別（`management_fee`, `cleaning`, `repair`, `tax`, `insurance`, `supplies`, `other`）在舊系統中無對應資料，**禁止自動回填或推估**。

### 3.2 安全匯入前置條件

| # | 條件 | 說明 |
| --- | --- | --- |
| 1 | PropertyExpense schema 已存在 | 包含完整欄位與 FK 約束。 |
| 2 | 11 筆紀錄的手工驗證完成 | 逐筆確認 `property_id`、`transaction_date`、`amount`、`notes` 可對應到舊系統原始資料。 |
| 3 | 對應物件（`properties`）皆存在 | 每筆紀錄的 `property_id` 須能關聯至已匯入的物件。 |
| 4 | 確認無重複 | 比對舊系統原始來源，確保 11 筆無重複匯入。 |
| 5 | 匯入腳本僅限 `utility` 類別 | 腳本寫死 category = `utility`，不接受動態類別參數。 |
| 6 | record_status 設為 `posted` | 歷史資料視為已確認支出，直接 `posted`，不經 `draft`。 |
| 7 | 匯入前先備份目標資料表 | `property_expenses` 表如有任何資料須先 dump 備份。 |
| 8 | 匯入後人工對帳 | 比對匯入筆數、金額總和與舊系統原始紀錄一致。 |

### 3.3 禁止自動回填規則

- **非 `utility` 類別禁止自動回填**：舊系統無 `management_fee`、`cleaning` 等支出紀錄，任何自動推估或腳本回填 `posted` 資料的行為均禁止。
- `other` 類別同樣禁止自動回填：不接受將無法歸類的歷史模糊資料以 `other` 名義匯入。
- 舊系統若有未對應到 `utility` 的疑似支出紀錄（如租約備註中的代墊款），手動評估後以人工支出流程（第 2 節）逐筆輸入。

---

## 4. 草稿、入帳、作廢與禁止刪除的操作流程

### 4.1 狀態機（引用契約定義）

```
draft -> posted -> voided
draft -> cancelled
```

### 4.2 操作流程

#### 4.2.1 Draft（草稿）

- **允許操作**：編輯所有欄位、刪除草稿本身（走 cancellation，非物理刪除）、上傳／移除附件。
- **不列入**：任何支出總計、報表、對帳計算。
- **生命週期**：無時效限制，但建議 7 日內處理。

#### 4.2.2 Posted（入帳）

- **觸發條件**：
  1. record_status 非 `draft`。
  2. 必要欄位全部填寫（`property_id`, `transaction_date`, `category`, `amount`）。
  3. 有憑證（參考 2.2 節，至少一項對應類別的佐證）。
- **不可逆**：`posted` 後禁止編輯 amount、category、transaction_date、property_id。
- **允許編輯**：`notes`、`payee`、`reference_no`（補充說明性質）。
- **立刻生效**：計入該 `year_month` 的物件支出總計與後續報表。
- **通知**：操作者確認後系統更新狀態，無需主管簽核（MVP 階段）。

#### 4.2.3 Voided（作廢）

- **觸發條件**：
  1. 原紀錄已 `posted`。
  2. 必須填寫 `void_reason`（至少 10 字）。
- **效果**：
  1. `voided_at` 記入系統時間。
  2. 原始 `amount`、`category`、`property_id`、`transaction_date` 全部保留，僅狀態變更。
  3. 不再計入正常支出總計。
- **禁止取消作廢**：一旦 `voided`，不可恢復為 `posted`。修正方式為新增一筆正確紀錄。

#### 4.2.4 Cancelled（取消草稿）

- **觸發條件**：原紀錄為 `draft`，操作者選擇取消。
- **效果**：紀錄保留但標記為取消，不計入任何總計。
- **無需理由**：可選填。

#### 4.2.5 禁止刪除

| 狀態 | 物理刪除 | 說明 |
| --- | --- | --- |
| `draft` | **禁止** | 只能走 cancellation。草稿雖然無財務影響，但仍保留操作軌跡。 |
| `posted` | **禁止** | 已入帳的財務事實禁止銷毀。修正只能走作廢 + 新紀錄。 |
| `voided` | **禁止** | 作廢紀錄保留原始金額與軌跡以供查核。 |
| `cancelled` | **禁止** | 取消紀錄保留以供查核。 |

---

## 5. 每月物件支出對帳流程

### 5.1 對帳週期

每月 5 日前完成前一月的支出對帳（例如 8 月支出於 9/5 前對帳完畢）。

### 5.2 對帳步驟

| 步驟 | 動作 | 負責 | 產出 |
| --- | --- | --- | --- |
| 1 | 篩選目標 `year_month` + `property_id` 的所有 `posted` 支出 | 系統 | 支出明細清單 |
| 2 | 比對外部憑證（發票、收據、銀行扣款） | 操作者 | 勾稽表 |
| 3 | 確認金額合計與外部來源一致 | 操作者 | 差異報告（如有） |
| 4 | 標記對帳完成 | 操作者 | 該月該物件支出視為已核對 |
| 5 | 如有未核對差異，進入錯誤回報（第 5.4 節） | 操作者 | 異常單 |

### 5.3 對帳不強制

- `posted` 紀錄無需等待對帳即可計入報表。
- 對帳為管理流程，不阻斷系統功能。

### 5.4 錯誤回報

| 錯誤類型 | 處理方式 |
| --- | --- |
| 金額錯誤 | 原單作廢（`voided` + `void_reason`），新增一筆正確 `posted` 紀錄。 |
| 類別錯誤 | 同上：作廢原單，新增正確類別的紀錄。 |
| 歸屬物件錯誤 | 作廢原單，新增正確 `property_id` 的紀錄。 |
| 重複輸入 | 作廢重複的那一筆，保留正確的一筆。 |
| 憑證不符 | 若無法補正憑證，作廢該筆紀錄，金額損失認定為管理問題另行處理。 |

所有錯誤修正留下完整 audit trail：原始紀錄狀態 `posted` -> `voided`，修正紀錄為新 `posted` 列。

### 5.5 Rollback 步驟

rollback 指將 PropertyExpense 模組回退至前一穩定部署版本。由於此模組尚未正式上線，rollback 計畫為預防性。

| 步驟 | 動作 | 指令／備註 |
| --- | --- | --- |
| 1 | 確認 rollback 原因 | 資料毀損、錯誤匯入、關鍵 Bug |
| 2 | 關閉 PropertyExpense 寫入路由 | 禁止新的 `draft` / `posted` 操作 |
| 3 | 回復前次部署版本的 `property_expenses` 資料表 | `pg_restore` 或 SQL dump 回存 |
| 4 | 回復前次版本的 app 程式碼 | `git revert` 或 deploy 前一版本 |
| 5 | 人工總計驗證 | 比對回退後的總金額與預期一致 |
| 6 | 開啟路由，恢復服務 | --- |

**不包含 rollback 的情況**：
- 單筆錯誤 -> 走作廢 + 新紀錄（第 5.4 節），不 rollback 整個模組。
- 使用者操作失誤 -> 同上。

---

## 6. 禁止事項（引用契約並補充）

1. 物理刪除任何狀態的 PropertyExpense 紀錄。（契約已有）
2. 在無對應憑證的情況下將 `draft` 變更為 `posted`。
3. 自動回填非 `utility` 類別的歷史支出。
4. 將 PropertyExpense 資料塞入 `MonthlyBill.other_charges`。（契約已有）
5. 將支出類別擴充至受控清單以外的值。（契約已有）
6. 允許未來日期作為 `transaction_date`。

---

## 7. 附錄：與既有契約的關係

本計畫完全相容於 `reasonix-reporting-expansion-contract-01.md`，不修改任何契約定義的欄位、狀態轉移或不變量。兩者分工如下：

| 面向 | 契約（Contract） | 本計畫（Operator Plan） |
| --- | --- | --- |
| 欄位定義 | 資料類型、FK、nullable | 操作必填、憑證要求 |
| 狀態機 | 狀態與允許轉移 | 操作流程、時限、通知 |
| 不變量 | 金額 > 0、不可原地編輯 | 錯誤修正步驟、對帳流程 |
| 刪除規則 | ON DELETE RESTRICT / SET NULL | 禁止 UI 刪除、只走作廢／取消 |
| 歷史資料 | 遷移相容性 | 11 筆 utility 匯入條件、類別限制 |