# Small Fix Notes

Date: 2026-06-28
Author: box

| Fix ID | File | Problem | Small Safe Fix | Validation | Risk |
| --- | --- | --- | --- | --- | --- |
| BOX-FIX-001 | (旧) D:\rental\ (scripts：user/users 合併相關候選) | 旧專案可能存在 `users` 與 `user` 雙表或資料不一致 | 若 `users` 僅為重複表：合併到正式 `user`（依既有 ORM `User` 指定表名）。若 `users` 有額外欄位，採 INSERT INTO ... SELECT 合併後刪除/歸檔 | 比對兩表筆數、username 唯一性、role 分佈；跑 verify：登入/role 查詢可正常 | P0 |
| BOX-FIX-002 | (旧) D:\rental\fix_elec.py / fix_202606_bills.py | `ElectricityBill.year_month`（舊 DB 或程式可能混用 YYYY-MM 或 YYYYMM；契約要求 DB 固定 YYYYMM） | repair script 統一 `electricity_bills.year_month` 為 YYYYMM：
- 若值含 '-'：移除 '-'
- 若值長度不足/超出：依 month/day 來源做推導（以契約為準）
- 更新後重算/確保關聯查詢可命中 | verify：查詢 `electricity_bills.year_month` 是否全為 `/^\d{6}$/`；同時抽查某 property 的 bill 可被 monthly 報表/對帳查到 | P0 |
| BOX-FIX-003 | (旧) D:\rental\app.py / billing route 與旧 repair 候選（year_month 正規化） | `MonthlyBill.year_month` 統一：DB 固定 `YYYYMM` | repair script 統一 `monthly_bills.year_month` 為 YYYYMM（集中一套 helper 逻辑；repair 只做資料矯正、不做架構） | verify：`monthly_bills.year_month` 全部匹配 `^\d{6}$`；以 `report_monthly` 查詢目標月份能正常渲染 | P0 |
| BOX-FIX-004 | (旧) D:\rental\app.py（報表 occupancy 關鍵字）、舊資料 tenant 可能混入虛擬名稱 | 虛擬 tenant 清理：舊系統可能以 tenant.name 含「空房/待修/待補/倉庫/鐵皮」等關鍵字做 occupancy 判定，需轉換為新版 `Room.status` / `Contract.status` | repair 候選：
- 清理 tenant.name 中虛擬語意的相關資料（歸檔或標記）
- contracts/rooms 重新評估：`Room.status` 僅 `vacant/occupied`；`Contract.status` 僅 `active/expired/terminated`
- 避免把 occupancy 邏輯再綁在 tenant.name 關鍵字 | verify：
- `Room.status` 非允許值為 0
- `Contract.status` 非允許值為 0
- monthly 報表在同月下 occupancy 顯示與 contract/room 狀態一致 | P0 |
| BOX-FIX-005 | (旧) D:\rental\app.py（Contract.status 欄位允許 active/expired/terminated）、舊資料可能存在過期值 | `Contract.status` 過期修正：舊 DB 若存在與 end_date 不一致的狀態 | repair 候選：
- `end_date < today` 且狀態為 `active` → 更新為 `expired`
- 若有明確終止訊號/規則（需依現有資料字段判定）：更新為 `terminated`
- 保留其他狀態不動 | verify：抽查 end_date 在過去合約；驗證報表 expiring/active_contracts 邏輯一致 | P1 |
| BOX-FIX-006 | (旧) D:\rental\app.py（Room.status 設定為 vacant/occupied）與舊資料 | `Room.status` 非標準值 mapping：舊 DB 可能存在 `Room.status` 不在 `vacant/occupied` 的值 | repair 候選：
- 若 status ∈ 允許集合：保留
- 否則：依 contracts/rooms 關聯推導 mapping（或保守歸為 vacant/occupied；若資訊不足則標記需人工確認）
- 嚴格禁止產生新增 status 值 | verify：`rooms.status` 唯一值集合僅為 `{vacant, occupied}` | P0 |
| BOX-FIX-007 | evidence SQL in mimo 回歸清單（需求描述） | mimo 回歸 evidence SQL 錯誤：共用電表目前使用了可能不存在的 `room_meters` 表 | Small safe fix：把 evidence SQL 改成依正式 schema 可執行的查法：
- 以 `electricity_meters`/`electricity_readings`（或新版正式模型）對應關聯條件取得共用表讀數/分攤證據
- 不再引用不存在的 `room_meters`
- 保留原有查詢目標（同月/year_month、property、meter type） | validation：
- evidence SQL 在新版 schema 下可直接跑出結果
- SQL 結果與既有期望欄位一致（欄位名/row count 或關鍵指標） | P0 |

## Deferred Items

- 以上候選均以「修復/遷移需求」為核心；實作細節需依 `scripts/migration/` 與 `scripts/repair/` 的正式腳本規範落地。

