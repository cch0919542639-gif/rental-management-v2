# Architecture Decision

Date: 2026-06-27
Author: reasonix
Status: Approved

## Executive Summary

- 新版採用 **Parallel Rebuild**：在 `rebuild/app/` 建立全新應用層，保留舊 DB schema 與既有商業資料，透過相容層橋接，逐步替換 `D:\rental\app.py` 單體。
- `PaymentRecord` 為唯一正式付款記錄實體，淘汰未完成的 `Payment` 路徑（該路徑引用的 `Payment` class 不存在，已是死碼）。
- `MonthlyBill.year_month` 正式規格：DB 固定 `YYYYMM`，UI/API 使用 `YYYY-MM`，轉換集中在 repository/service 層的單一 helper，禁止 route/template 各自 `replace('-', '')`。
- `user` / `users` 雙表：以既有 ORM 使用的 `user` 為正式來源，`users` 若存在則合併後刪除。
- 空房 / 待修 / 待補：由 `Room.status`（`vacant`/`occupied`）與 `Contract.status` 描述 occupancy；待修由獨立的 `maintenance` 模組或欄位管理，不再使用虛擬 tenant 名稱。

## Confirmed Facts

- 舊系統為單檔 `D:\rental\app.py`，ORM model、route、form、utility 全混在同一檔案，約 1800+ 行。
- `PaymentRecord` 已定義完整 schema 與 `record_status` 狀態機（`pending`/`verified`/`rejected`/`linked`），`payment_records` 表存在但資料量為 0。
- `/payment/new`、`/payment/history`、`/admin/payments` 等 route 引用 `Payment` class，經查驗確認該 class 從未在原始碼中定義，此路徑為死碼。
- `MonthlyBill.year_month` 舊 DB 實際儲存值為 `YYYYMM`（如 `202606`），ORM 註解誤標為 `String(7)` 與 `2026-04` 格式，舊程式在 9 處以上各自做 `replace('-', '')` 或 `strftime('%Y%m')` 轉換。
- 舊 `report_monthly()` 以 `tenant.name` 是否包含 `"待補"`、`"待修"`、`"空房"`、`"倉庫"`、`"鐵皮"` 等關鍵字判定空房顯示。
- DB 內存在 `user` 與 `users` 兩張表（由 `core-entities.md` 記載），ORM `User` class 無 `__tablename__`，SQLAlchemy 預設為 `user`。
- `landlord_report.py`、`water_bill.py`、`check_property_page.py` 等多個外部腳本以 `from app import ...` 反向引用主程式，形成隱性循環依賴。
- `electricity_bp.py` route 內混入計算公式與硬編碼 `meter_id=1`。

## Inferences

- `Payment` 路徑從未上線使用（class 不存在 + 引用它的 route 會在執行時拋出 `NameError`），移除零風險。
- `year_month` 轉換不一致已是產生 bug 的已知來源，集中化是最低成本的修復。
- 虛擬 tenant 名稱機制使 tenant 表語義被汙染，且 `report_monthly` 的關鍵字比對邏輯與 `Room.status` 脫鉤，在 status 改變時不會自動反映。
- 舊系統的模組邊界不存在：所有 route 共享同一個 app 實例，任何 import 都形成雙向耦合。

## Problem Statement

- 舊系統 `app.py` 為 God Object：同時承載 ORM 定義、路由邏輯、表單驗證、外部 API、LINE webhook、OCR 處理。
- 不存在 service 層：計費公式散落在 route、utility class、template 中。
- 不存在 repository 層：所有查詢直接在 route 中用 SQLAlchemy query 寫死。
- 兩套付款流程（`PaymentRecord` vs `Payment`）造成混淆，其中一套為死碼。
- 多個外部腳本以 `from app import` 反向引用，任何重構都會牽動這些腳本。

## Current Risks

### P0

- `year_month` 轉換散落各處，新增功能時極易再引入格式不一致 bug。
- 虛擬 tenant 名稱與 `Room.status` 雙軌並行，occupancy 判定可能互相矛盾。

### P1

- 外部腳本（`landlord_report.py`、`water_bill.py`、`check_*.py`）直接耦合 `app.py` 內部 ORM，任何 schema 變更都會破壞這些腳本。
- 電費 route 內硬編碼 `meter_id=1`，多電表場域會直接錯誤。

### P2

- `user`/`users` 雙表若資料不一致，合併時可能遺失帳號或角色。
- `payment_records` 表空置，無歷史資料需遷移，但也無驗證基準。

## Options

### Option A: Refactor In Place

直接在 `D:\rental\app.py` 上重構，逐步抽出 module/service/repository。

Pros:
- 不需建立新專案結構，改動範圍最小。
- 可漸進進行，每次 commit 都能 deploy。

Cons:
- 舊 app.py 為 God Object，任何抽離都可能打斷既有 route/import。
- 外部腳本的 `from app import` 耦合使重構半徑極大。
- 沒有乾淨的測試基準，抽離後無法獨立驗證。

Risks:
- 重構期間舊系統可能因抽離失誤而無法正常服務。
- 沒有並行驗證機制，回歸只能靠手動測試。

### Option B: Parallel Rebuild

在 `rebuild/app/` 建立全新模組化結構，保留舊 DB，新舊並存，逐步切換。

Pros:
- 舊系統完整保留，隨時可回退。
- 新系統從零建立清晰的模組邊界，無歷史債。
- 每階段可獨立測試、獨立驗收。
- 外部腳本可在切換前逐步改寫為新模組 import。

Cons:
- 初期工作量較大，需建立完整骨架。
- 新舊並存期間需維護兩套結構。
- 需要 migration/compat 層確保 DB schema 相容。

Risks:
- 若新舊 DB schema 分歧未管理好，可能產生資料不一致。
- 切換期需停機窗口。

### Option C: Hybrid

部分模組 rebuild（如 payments、billing），部分模組原地重構（如 landlords、properties）。

Pros:
- 可優先處理高風險模組（payments、billing）。
- 比全 parallel rebuild 更快看到成果。

Cons:
- 新舊邊界交錯，import 關係更複雜。
- 無法建立統一的 app factory / config / error handling。
- 中期會出現三種程式風格共存（舊 route、refactored route、new module）。

Risks:
- 架構不一致導致難以維護。
- 跨模組 bug 更難定位。

## Decision

- **Selected Option: B — Parallel Rebuild**

- **Why:**
  1. 舊系統 `app.py` 的耦合程度（ORM + route + form + integration + utility 全混）使任何原地重構都不可控，測試覆蓋率為零。
  2. `rewrite-roadmap.md` 已明確採用「先重建應用結構」策略，Phase 0-5 分期設計預設就是 parallel rebuild。
  3. `target-structure.md` 的目錄（`app/core/`, `app/modules/`, `app/services/`, `app/repositories/`）已在 `rebuild/` 下建立，骨架已就位。
  4. 外部腳本的 `from app import` 反向耦合若原地重構必然全數破壞，parallel rebuild 可讓舊腳本繼續指向舊 app.py，新模組逐步取代。
  5. `Payment` 死碼可直接在新版不實作，若原地重構則需先釐清誰依賴它（結果是無人依賴，但驗證成本高）。

## Scope Included

- 全新 `app/` 結構：`core/`（app factory、config、db、security、logging、errors）、`models/`（ORM）、`modules/`（11 個業務模組）、`services/`（計費、對帳、驗證）、`repositories/`（集中查詢）。
- `PaymentRecord` 為唯一付款實體，含完整 `record_status` 狀態機與 OCR→審核→對帳流程。
- `year_month` 統一 helper：`core/year_month.py`，提供 `to_db(YYYY-MM) -> YYYYMM`、`to_ui(YYYYMM) -> YYYY-MM`、`validate()`。
- `Room.status` 僅 `vacant`/`occupied`；`Contract.status` 為 `active`/`expired`/`terminated`；待修由獨立 `maintenance` 模組處理。
- `user` 單表，`role` 為 `admin`/`landlord`/`viewer`。

## Scope Excluded

- 不實作 `Payment` model 及相關 route（`/payment/new`、`/payment/history`、`/admin/payments`、`/admin/payment/<pid>/confirm`、`/admin/payment/<pid>/cancel`）。
- 不保留虛擬 tenant 名稱機制。
- 不遷移舊版外部腳本（`landlord_report.py`、`water_bill.py`、`check_*.py` 等），改由新版 `reports` 模組與 service 取代。
- 不保留舊版 electricity route 的硬編碼 `meter_id=1`。
- 第一版不實作 `billing_rule` enum 完整展開（先保留契約欄位，邏輯後補）。

## Required Migration Work

1. **`user` / `users` 雙表合併**：比對兩表筆數與欄位，確認 ORM `User.__tablename__` 指向 `user`，另一張若無額外資料則 drop，若有則 INSERT INTO ... SELECT 合併。
2. **`MonthlyBill.year_month` 正規化**：若 DB 內存在非 `YYYYMM` 格式的殘留值（如 `2026-04`），需 repair script 統一為 `YYYYMM`。
3. **虛擬 tenant 清理**：盤點 `tenants` 表中 `name` 為 `空房`、`待修`、`待補`、`倉庫`、`鐵皮` 的 row，關聯的 contract 需改以 `Room.status` 與 `Contract.status` 重新評估後歸檔或標記。
4. **`Payment` 路徑移除**：從舊 `app.py` 刪除 `/payment/new`、`/payment/history`、`/admin/payments`、`admin_confirm_payment`、`admin_cancel_payment` 五個 route 定義（保留對應 template 作為參考但不掛載）。
5. **`ElectricityBill.year_month` 格式統一**：舊 schema 定義為 `String(7)`，需 alter 為 `String(6)` 或維持長度但強制寫入 `YYYYMM`。

## Rollback Strategy

- 新版 `app/` 與舊版 `D:\rental\app.py` 完全隔離，rollback 即停止新版服務、回復舊版啟動。
- DB migration 每支腳本必須有對應的 down 腳本（或備份後執行）。
- 在 Phase 5 切換前，新舊系統共用同一 DB，任何 schema 變更必須同時相容新舊兩套 ORM。

## Exact Next Steps

1. `open` agent 接手：建立 `core/year_month.py` helper、`core/db/` session factory、`core/config/` 設定層。
2. `open` agent 建立 `app/models/` 下所有 ORM model（基於 `data_contracts/` 凍結欄位）。
3. `mimo` agent 依合約撰寫 `PaymentRecord` 的 service + route + template。
4. `box` agent 處理 migration scripts：user 雙表合併、year_month 正規化、虛擬 tenant 清理。
5. 所有 agent 完成後，`reasonix` 進行 Phase 0 驗收（關卡 A：資料契約凍結確認）。
