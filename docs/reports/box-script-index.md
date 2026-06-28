# Script Index

Date: 2026-06-28
Author: box

| Script/File | Current Location | Purpose | Category | Keep / Archive / Rewrite | Suggested New Home | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| check_bill_period.py | D:\rental\check_bill_period.py | 檢查電費/帳單週期資料狀況（示例：查 electricity_bills 某 id 的 period_start/end 與用量/金額） | check_* | Keep（作為資料診斷參考） | scripts/repair/ | 依現行新版路徑可再包裝成 repair/verify。現為一次性 db 檢查指令腳本。 |
| check_db.py | D:\rental\check_db.py | 尋找實際 app 使用的 db 檔（掃描 db 檔、查特定 property=立志街 June=2026-06 是否存在） | check_* | Keep | scripts/repair/ | 不屬於資料契約變更，主要是執行前的環境/證據對齊工具。 |
| check_elec_schema.py | D:\rental\check_elec_schema.py | 印出電力相關表的欄位結構（PRAGMA table_info） | check_* | Keep | scripts/repair/ | 用於 migration/repair 前的 schema 對齊檢查。 |
| check_elec_tables.py | D:\rental\check_elec_tables.py | 列出電力帳單/電表/讀數現況（property 13 示範） | check_* | Keep | scripts/repair/ | 現為針對 property_id=13 的觀測腳本；新版可抽成可配置 verify。 |
| check_elec.py | D:\rental\check_elec.py | 彙整電力資料狀態：最新 year_month、occupied rooms 數、各 property 最近 electricity 月份 | check_* | Keep | scripts/repair/ | 針對總覽診斷，建議保留為 verify/observability 工具。 |
| check_existing_elec.py | D:\rental\check_existing_elec.py | （未逐檔讀取內容；命名推定）檢查既有電力資料是否存在 | check_* | Keep/Rewrite（視內容） | scripts/repair/ | 需依實際內容確認是否仍有效的資料核對邏輯。 |
| check_june.py | D:\rental\check_june.py | 檢查 2026-06 各項帳單資料（命名推定） | check_* | Keep/Rewrite（視內容） | scripts/repair/ | 需依內容確認與 `year_month` 正規化關聯程度。 |
| check_lizhi.py | D:\rental\check_lizhi.py | 檢查立志街（property 13）資料現況（命名推定） | check_* | Keep/Rewrite（視內容） | scripts/repair/ | 需依內容確認可否通用化成 repair/verify。 |
| check_property_page.py | D:\rental\check_property_page.py | 檢查物件頁顯示/資料正確性（命名推定） | check_* | Archive（若僅 UI/模板驗證）或 Keep（若仍可驗證） | scripts/repair/ | 若純 UI/模板渲染測試，建議以 test/或 archive 處理。 |
| check_rate.py | D:\rental\check_rate.py | 檢查電價/費率設定正確性（命名推定） | check_* | Keep | scripts/repair/ | 需依實際內容確認與 electricity rate type 的契約一致性。 |
| check_rooms_again.py | D:\rental\check_rooms_again.py | 房間資料/狀態再檢查（命名推定） | check_* | Keep | scripts/repair/ | 若涉及 Room.status 非標準值診斷，可對應到 repair 候選。 |
| create_may_bills.py | D:\rental\create_may_bills.py | 依既有邏輯建立特定月份帳單（命名推定：May bills） | create_* | Rewrite | scripts/migration/ | 若仍用於 production data repair/migration，需改造為可參數的 migration（避免硬編碼月份）。 |
| create_meters.py | D:\rental\create_meters.py | 建立電表（命名推定） | create_* | Archive/Rewrite（視內容） | scripts/migration/ | 如果是一次性資料建立，可 rewrite 成 migration。 |
| create_meters_fixed.py | D:\rental\create_meters_fixed.py | 清理並重新建立 property=13 下 electricity_meters（強制正確欄位/格式） | create_* | Rewrite（或 Keep 作為明確 repair 範本） | scripts/migration/ | 對應「共用/獨立電表與電表資料一致性」類 repair/migration。現為針對 property_id=13 的一次性清理。 |
| ct_meter_proportional.py | D:\rental\ct_meter_proportional.py | （命名推定）按比例處理共用電表/分攤 | create_* / update_* | Archive/Rewrite（視內容） | scripts/repair/ | 僅列為候選；若涉及量化分攤，需核對新版計費契約後才可進入正式 repair。 |
| debug_bills.py | D:\rental\debug_bills.py | 針對電費帳單某 id/pattern 的 debug/觀測 | debug_* | Keep | scripts/repair/ | 建議降級為 debug/verify 類觀測腳本。 |
| debug_json.py | D:\rental\debug_json.py | （命名推定）JSON 輸入/輸出 debug | debug_* | Archive | scripts/repair/ | 純 debug，多半不進入正式索引。 |
| debug_meters.py | D:\rental\debug_meters.py | 檢查 property 13 下 electricity_meters 是否存在（逐 room_id 測試） | debug_* | Keep（作為 repair 前檢） | scripts/repair/ | 可用於 verify：電表是否正確建立/清理後可用。 |
| debug_bills（已包含檔名） | D:\rental\debug_bills.py | （同上） | debug_* | Keep | scripts/repair/ |  |
| deploy.py | D:\rental\deploy.py | 部署入口（非資料修復） | update_* | Archive | scripts/repair/ | 只保留索引參考，不建議納入 migration/repair。 |
| deploy_landlord_report.sh | D:\rental\deploy_landlord_report.sh | 部署 landlord report（非資料修復） | update_* | Archive | scripts/repair/ |  |
| deploy_aliyun.sh | D:\rental\deploy_aliyun.sh | 部署 aliyun（非資料修復） | update_* | Archive | scripts/repair/ |  |
| dual_meter_tou.py | D:\rental\dual_meter_tou.py | （命名推定）雙電表/TOU 相關處理 | debug_/create_? | Archive/Rewrite（視內容） | scripts/repair/ | 僅列候選；需核對新版 electricity 契約。 |
| electricity_bp.py | D:\rental\electricity_bp.py | electricity blueprint（程式來源，不是腳本） | update_* | Archive（不納入 repair 索引為主） | app/modules/electricity（不在本任務範圍） | 本任務只做腳本索引/README/repair 候選，不做架構決策；保留為查考。 |
| final_check.py | D:\rental\final_check.py | 末期檢查：列出 property=13 的 2026-06 月帳單資料 | verify_* | Keep（作為 verify） | scripts/repair/ | 可對應收尾驗證清單。 |
| final_verify.py | D:\rental\final_verify.py | （命名推定）末期 verify（可能是 final_check 的補強） | verify_* | Keep/Rewrite（視內容） | scripts/repair/ | 需逐檔讀取內容確認。 |
| fix_202606_bills.py | D:\rental\fix_202606_bills.py | 針對 year_month=202606 的 electricity_prev/curr/usage/amount 與 total 修正 | fix_* | Rewrite（納入 repair/migration） | scripts/repair/ | 強烈對應 mimo 回歸 evidence 的「錯誤 SQL 修正候選」類型：year_month 正規化、電費欄位一致。 |
| fix_elec.py | D:\rental\fix_elec.py | 修正 electricity_bills 格式：fee/usage=5 推回 prev_reading 與 total | fix_* | Rewrite（納入 repair/migration） | scripts/repair/ | 對應「ElectricityBill.year_month 正規化」與電費資料一致性 repair。 |
| fix_rent.py | D:\rental\fix_rent.py | 修正租金值：把 rent 誤與 deposit（押金）對調，並修正 2026-06 monthly_bills.total | fix_* | Archive（非本次指定小修） | scripts/repair/ | 不在你指定的優先小修清單中；目前僅作索引記錄。 |
| fix_templates.py | D:\rental\fix_templates.py | （命名推定）修正模板細節 | fix_* | Archive | scripts/repair/ | 若純模板展示，不進入 DB migration/repair。 |
| fix_units.py | D:\rental\fix_units.py | 移除 electricity templates 內 Jinja2 表達式後的「度/元」字樣 | fix_* | Archive（非 migration/repair） | templates/（不納入本任務） | 屬 UI/模板修正，不是 migration/repair；本任務僅索引。 |
| fix_units（已包含檔名） | D:\rental\fix_units.py | （同上） | fix_* | Archive |  |  |
| fix_templates（已包含檔名） | D:\rental\fix_templates.py |  | fix_* | Archive |  |  |
| update_contracts.py | D:\rental\update_contracts.py | 更新 contracts.rent 為表格資料（property=13, room A-F） | update_* | Archive/Rewrite（視是否 migration） | scripts/migration/ | 若契約租金屬於資料修復（不是程式），可轉 migration/repair。此任務未要求實作。 |
| update_lizhi.py | D:\rental\update_lizhi.py | （命名推定）更新立志街資料（非確定） | update_* | Archive/Rewrite（視內容） | scripts/migration/ | 需逐檔讀取確認是否屬年月份修正/狀態修正。 |
| update_rent.py | D:\rental\update_rent.py | （命名推定）更新租金/費用 | update_* | Archive/Rewrite（視內容） | scripts/migration/ | 需核對。 |
| verify_data.py | D:\rental\verify_data.py | 列出 property=13 的 2026-06 月帳單/合約/租客資訊 | verify_* | Keep（作為 verify） | scripts/repair/ | 可作 repair 後驗證（但本檔已針對 property_id=13 與月=2026-06）。 |
| verify_elec_data.py | D:\rental\verify_elec_data.py | 查 electricity 資料（property=13）並印出 bill 與 reading | verify_* | Keep | scripts/repair/ | 對應 repair 前後驗證。 |
| verify_templates.py | D:\rental\verify_templates.py | 檢查模板（例如 ${ {}} jinja 殘片） | verify_* | Keep/Archive（視需求） | scripts/repair/ | 純驗證模板清潔程度，不屬 DB repair。 |
| rental.db.bak.20260616 | D:\rental\rental.db.bak.20260616 | DB 備份檔 | *.bak* | Archive | (evidence/) | 不是腳本；但依索引要求歸類到 *.bak*。 |
| app.py.bak_rounding_20260616 | D:\rental\app.py.bak_rounding_20260616 | 舊版 app.py 備份（rounding 相關） | *.bak* | Archive | (archive/) |  | 
| app.py.bak | D:\rental\app.py.bak | 舊版 app.py 備份 | *.bak* | Archive | (archive/) |  |
| app.py.bak.20260523 | D:\rental\app.py.bak.20260523 | 舊版 app.py 備份 | *.bak* | Archive | (archive/) |  |
| app.py.bak2 | D:\rental\app.py.bak2 | 舊版 app.py 備份 | *.bak* | Archive | (archive/) |  |
| app.py.bak3 | D:\rental\app.py.bak3 | 舊版 app.py 備份 | *.bak* | Archive | (archive/) |  |
| rental_530_backup.db | D:\rental\rental_530_backup.db | DB 備份檔 | *.bak* | Archive | (evidence/) |  |
| rental_202606_create_missing.db | D:\rental\rental_202606_create_missing.db | DB 備份檔 | *.bak* | Archive | (evidence/) |  |
| rental_202606_final_fix.db | D:\rental\rental_202606_final_fix.db | DB 備份檔 | *.bak* | Archive | (evidence/) |  |
| rental_202606_full_backup.db | D:\rental\rental_202606_full_backup.db | DB 備份檔 | *.bak* | Archive | (evidence/) |  |
| rental_202606_mass_update.db | D:\rental\rental_202606_mass_update.db | DB 備份檔 | *.bak* | Archive | (evidence/) |  |
| rental_changyu_fix.db | D:\rental\rental_changyu_fix.db | DB 備份檔 | *.bak* | Archive | (evidence/) |  |
| rental_cleanup_backup.db | D:\rental\rental_cleanup_backup.db | DB 備份檔 | *.bak* | Archive | (evidence/) |  |
| rental_contract_fix.db | D:\rental\rental_contract_fix.db | DB 備份檔 | *.bak* | Archive | (evidence/) |  |
| test_flask_report.py | D:\rental\test_flask_report.py | 測試報表渲染（Flask report） | test_* | Keep/Archive（視是否可重放） | tests/integration/ | 僅索引。新版若無法直接跑需 archive。 |
| test_import.py | D:\rental\test_import.py | （命名推定）匯入測試 | test_* | Archive/Keep（視內容） | tests/ |  |
| test_line.py | D:\rental\test_line.py | LINE 相關測試 | test_* | Archive | tests/ |  |
| test_property_page.py | D:\rental\test_property_page.py | 房產頁測試 | test_* | Archive/Keep（視內容） | tests/ |  |
| test_report.py | D:\rental\test_report.py | 測試報表 | test_* | Keep | tests/ |  |
| test_secret.py | D:\rental\test_secret.py | 測試 secret/env | test_* | Archive | tests/ |  |

## Rewrite Candidates

- `create_meters_fixed.py`：轉成 scripts/migration/ 或 scripts/repair/ 的可參數 migration/repair（避免硬編碼 property_id=13）。
- `fix_elec.py`：轉成 scripts/repair/ 的 electricity repair（強制 `ElectricityBill.year_month` 寫入 YYYYMM）。
- `fix_202606_bills.py`：轉成 scripts/repair/ 的 year_month 與 electricity 欄位修復 repair（補上查核與回滾/驗證）。

## Archive Candidates

- `fix_rent.py`：不在本次指定的必修小修清單中（僅保留索引）。
- `fix_units.py`：模板文字修正屬 UI 修正，不屬 DB migration/repair。
- `fix_templates.py`：模板修正屬 UI 修正，不屬 DB migration/repair。
- `deploy.py` / `deploy_*.sh`：部署腳本不屬本次 migration/repair。

