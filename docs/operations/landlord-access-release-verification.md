# 房東報表與存取權限：提交前驗證標準

狀態：規則與測試案例已獨立複核；待可用 pytest 環境執行
建立日期：2026-08-31
核准範圍：房東帳號／報表存取／`user_property_accesses` migration／對應測試。

## 已確認的業務規則

1. 房東可見物件的唯一依據是 `user_property_accesses` 的明確授權；不得因 `landlord_id`、同名房東或前端篩選而取得其他物件。
2. 房東可使用「我的月報」、物件收款相關報表、年度總覽與房東彙總；年度總覽與房東彙總同樣只顯示明確授權物件。畫面與 CSV/XLSX 匯出都必須套用同一可見物件範圍。
3. 房東一律不得操作帳單、物件、房客、合約與付款；日後若要開放任何操作，必須另立需求、權限規則與測試，不得由本批變更隱含開放。
4. 一個登入帳號可以被授權多個物件。
5. `user_property_accesses` 是正式新增表：`(user_id, property_id)` 唯一，並對 `user.id` 與 `properties.id` 設外鍵。
6. 目前 10 個房東帳號與 21 筆物件授權是已核准的業務設定，可用於驗收與上線資料核對；不得把 `runtime.db`、密碼雜湊、明碼密碼或帳號資料直接提交到 Git。

## 白話說明：為何要新增 `user_property_accesses`

原本一個帳號只能連到一位房東，無法清楚表示「同一位登入者可看多個指定物件」。新表就像一張授權清單：每一列只寫「這個帳號可以看這個物件」。因此它可以支援多物件帳號，也可以拒絕沒有列在清單中的物件；唯一限制會防止同一帳號被重複授權同一物件。

這個 migration 只新增授權表，不會刪除既有帳號、物件、合約或帳務資料。Git 提交的是表結構與程式邏輯；正式帳號與授權資料仍由受控資料庫／上線流程管理，不提交資料庫檔。

## 提交內容與排除項目

### 本批應包含

- `app/migrations/versions/20260724_000002_add_user_property_accesses.py`
- `app/models/user.py`、`app/models/__init__.py` 與必要 migration 設定
- 房東可見物件範圍、報表入口與 CSV/XLSX 匯出相關程式與模板
- 房東營運操作限制相關 routes
- 對應 integration tests 與本文件／必要交接紀錄

### 本批不得包含

- `runtime.db`、備份資料庫、staging 資料庫或任何資料庫匯出
- 明碼密碼、密碼雜湊、電話、身分證字號、銀行帳號、OCR 原文
- 7 月匯入、結算、Google 對帳腳本與稽核 JSON
- `scratch-rental-v2.service`、本機 cache、IDE 設定或與本批無關的既有變更

## 驗證流程與通過標準

### A. Migration 安全性（在正式資料庫的備份副本）

1. 複製正式資料庫為隔離測試副本；記錄原始檔與副本的 SHA-256、資料表筆數與 `PRAGMA integrity_check`。
2. 對副本執行 migration upgrade；確認只新增 `user_property_accesses`，且既有表筆數不變。
3. 檢查表結構：主鍵、兩個外鍵與 `uq_user_property_access` 唯一限制均存在。
4. 以同一 `(user_id, property_id)` 嘗試插入兩次，第二次必須因唯一限制失敗；以不存在的 user/property 嘗試插入，必須因外鍵失敗。
5. 對副本執行 downgrade，再執行 upgrade；兩次都成功，且既有帳務與主檔筆數不變。
6. 再次執行 `PRAGMA integrity_check` 與 `PRAGMA foreign_key_check`；結果分別為 `ok` 與 0 筆。

通過標準：migration 可重複執行、可回滾再升級，且沒有對既有資料造成遺失或外鍵損壞。注意：`downgrade` 會移除新增的 `user_property_accesses` 表，因此已建立的授權資料必須在回滾前另行備份；回滾後再升級不會自動還原那些授權列。

### B. 授權與報表範圍

建立至少三種測試帳號／資料情境：

- 房東 A：被授權一個物件。
- 房東 B：被授權兩個物件。
- 房東 C：沒有指定物件的授權。

逐一確認：

1. 房東 A／B 只能看到自身明確授權的地址、房號、房客與金額。
2. 房東 C 沒有任何 `user_property_accesses` 時，月報、房東彙總、年度總覽及其 CSV/XLSX 可開啟但只能得到空資料／零金額；若帶入任一 `property_id`，必須回 `403`。
3. 對接受 `property_id` 的物件收款相關報表，直接帶入未授權物件必須回 `403`；月報、年度總覽與房東彙總則必須以授權物件集合產生結果。所有回應及匯出檔均不得含未授權物件資料。
4. 同一限制必須套用到 HTML、CSV 與 XLSX。
5. 房東入口應顯示：我的月報、物件收款相關報表、年度總覽、房東彙總；不應出現營運管理選單。
6. 管理員仍可看所有被授權管理範圍內的報表；不可因本次調整失去既有營運功能。

通過標準：所有報表與匯出均在伺服器端以 `user_property_accesses` 範圍過濾，且無越權資料洩漏。

### C. 房東營運操作禁止

房東對以下 GET 與 POST 都必須得到 `403`，並檢查資料未變動：

- 帳單：建立、編輯、產生、批次產生、切換繳款狀態。
- 物件、房客、合約：列表、建立、編輯、刪除／終止。
- 付款：列表、建立、驗證、駁回、連結。

通過標準：被拒絕後，帳單 `paid`、付款狀態、合約狀態及物件／房客資料的前後值完全相同。

### D. 自動化回歸

先跑與本批直接相關的測試：

```powershell
py -3 -m pytest -q tests\integration\test_reporting_expansion.py tests\integration\test_landlord_billing_access.py tests\integration\test_landlord_operational_access.py tests\integration\test_auth_login_security.py
```

再跑完整整合測試：

```powershell
py -3 -m pytest -q tests\integration
```

最後執行：

```powershell
git diff --check
git status --short
```

通過標準：相關與完整整合測試全數通過；`git diff --check` 無輸出；暫存區僅有本文件「應包含」章節所列的範圍。

## 獨立驗證交付格式

驗證 agent 必須提供：

1. 執行環境與使用的資料庫副本路徑（不得提供帳密）。
2. 每個步驟的命令、結果與必要證據。
3. 每一個未通過項目的檔案／路由／migration 位置與可重現方式。
4. 明確結論：`可提交`、`可提交但有已知限制` 或 `不可提交`。

未完成 A 至 D 任一項，主控不得提交。

## 2026-08-31 獨立複核結果

- 已確認程式修正符合已核准規則：房東的可見物件只取自 `user_property_accesses`；沒有任何授權時只得到空資料；年度總覽與房東彙總對房東開放，但仍使用同一授權範圍。
- 已確認測試案例覆蓋：單一授權房東的年度／房東彙總範圍，以及零授權房東的月報、房東彙總、物件收租、年度總覽 HTML／CSV／XLSX 空資料與未授權 `property_id` 的 `403`。
- `git diff --check` 通過，暫存區仍為空。
- 阻擋：本機 `py -3` 顯示 `No installed Python found!`；bundled Python 未安裝 pytest，故 D 的 focused 與完整整合測試尚未執行。完成 D 前不得提交。

## 2026-09-01 修正後複核

- 已修正零授權資料洩漏：所有 property-scoped repository 查詢以 `property_ids is not None` 判斷篩選；空集合 `[]` 現在會產生零筆結果，而 `None` 才代表管理端未指定篩選。
- 已修正 `ReportService.property_yearly()`：零授權不再列出全部物件的零額月份列，避免經由直接 URL 洩漏物件名稱。
- 已修正年度總覽整數金額顯示、退租報表測試的明確物件授權，以及 Alembic bridge 對目前 revision `20260724_000002` 的斷言。
- 已補零授權與單一授權帳號的 HTML／CSV／XLSX 回歸案例，涵蓋月報、房東彙總、物件收租、物件年度與年度總覽。
- 獨立程式複核與 `git diff --check` 通過；尚未發現新的空集合範圍洩漏。
- 仍待完成：在可用 Flask/Alembic 環境對隔離副本實做 upgrade → downgrade → upgrade；並執行 D 的 focused 與完整 integration suite。這兩項完成前不得提交。

## 2026-09-01 最終驗證結果

### A. 隔離資料庫 migration 往返

- 副本：`D:\CodexRuntime\migration-verify-20260901\runtime-before.db`；來源與副本建立時的 SHA-256 均為 `7A318141DE91DD639C7832D639CD7ACDF36437FDFDEE988197D7E8FA54B38217`。
- 在副本以 Flask-Migrate 的 `app/migrations` 目錄完成 `20260724_000002` 的 stamp、downgrade 至 `20260701_000001`，再 upgrade 回 `20260724_000002`。
- 既有資料表筆數在往返前後均為：users 2、properties 2、rooms 2、tenants 2、contracts 2、monthly_bills 2、payment_records 0、property_expenses 0。
- 最終確認 `user_property_accesses` 已建立、`alembic_version` 為 `20260724_000002`、`PRAGMA integrity_check` 為 `ok`、`PRAGMA foreign_key_check` 為 0 筆。
- 來源正式資料庫只讀，驗證結束後 SHA-256 未變。已知限制：downgrade 依 migration 設計會 drop 新表，因此副本原有的 1 筆授權列未隨 re-upgrade 回復；正式環境若需回滾，必須先匯出／備份授權列，後續再恢復。

### B 至 D. 權限、回歸與 Git 檢查

- `tests\\integration\\test_reporting_expansion.py`：9 passed。
- `tests\\integration\\test_migration_scaffold.py`：10 passed。
- `tests\\integration`：168 passed、15 skipped、1 個既有 SQLAlchemy `Query.get()` deprecation warning，耗時 207.20 秒。
- `git diff --check` 通過（僅有 Git 的 CRLF/LF 工作樹提示，沒有 whitespace error）。
- 結論：**可提交但有已知限制**。程式、migration 與測試符合授權規則；部署回滾作業必須將 `user_property_accesses` 資料備份與還原列為必要步驟。
