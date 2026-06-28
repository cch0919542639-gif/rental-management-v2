# Test Scenarios

Date: 2026-06-28
Author: mimo

---

| Scenario ID | Scenario Name | Preconditions | Steps | Expected Result | Related Module | Priority |
| --- | --- | --- | --- | --- | --- | --- |
| TS-01 | 正常登入 | User 表存在 admin 帳號 | 1. 開啟 /login 2. 輸入 username/password 3. 點擊登入 | 成功登入，重導向至 /dashboard，session 建立 | auth | P0 |
| TS-02 | 登入失敗 — 錯誤密碼 | User 表存在 admin 帳號 | 1. 開啟 /login 2. 輸入錯誤密碼 3. 點擊登入 | 留在 /login，顯示錯誤訊息，session 未建立 | auth | P0 |
| TS-03 | 登出 | 已登入狀態 | 1. 點擊登出連結 2. 確認 | session 清除，重導向至 /login | auth | P1 |
| TS-04 | 空房顯示 — Dashboard | Room.status='vacant' 的房間存在 | 1. 開啟 /dashboard 2. 查看「空房」統計 | 顯示正確的空房數量，來源為 Room.status='vacant' | dashboard, rooms | P0 |
| TS-05 | 空房顯示 — Room List | Room.status='vacant' 的房間存在 | 1. 開啟 /rooms 2. 查看房間列表 | Room.status='vacant' 的房間顯示為「空房」 | rooms | P0 |
| TS-06 | 空房顯示 — Monthly Report | Room.status='vacant' 且無 active Contract | 1. 開啟 /reports/monthly 2. 查看空房數 | 使用 Room.status='vacant' 計算，不使用 tenant.name 關鍵字 | reports | P0 |
| TS-07 | 待修房顯示 | Room 存在且有待修標記 | 1. 確認 Room.status 為 vacant（待修獨立處理） 2. 確認 maintenance 模組有紀錄 | 待修狀態由 maintenance 模組管理，Room.status 仍為 vacant | rooms, maintenance | P0 |
| TS-08 | 待修房不影響 tenant 表 | 無虛擬 tenant（空房/待修/待補）存在 | 1. 查詢 tenants 表 2. 確認無 name 含「待修」的紀錄 | tenants 表僅含真實房客，無虛擬名稱 | tenants | P0 |
| TS-09 | 新簽約當月帳單 | Room 存在且 status='vacant'，無 active Contract | 1. 建立新 Contract（start_date 為當月） 2. 確認 Room.status → occupied 3. 生成當月帳單 4. 查看 bill list | Room.status 變為 occupied；當月帳單正確生成，year_month 為 YYYYMM（DB）/ YYYY-MM（UI） | contracts, billing | P0 |
| TS-10 | 新簽約 — 同房間唯一 active 合約 | Room 已有 active Contract | 1. 嘗試為同一 Room 建立新 Contract 2. 確認 | 系統拒絕建立，顯示「此房間已有 active 合約」 | contracts | P1 |
| TS-11 | 已到期合約 — 狀態顯示 | Contract.end_date < today 且 status='active' | 1. 開啟 /contracts 2. 查看合約列表 | 該合約顯示為「已到期」或 status 已被修正為 expired | contracts | P0 |
| TS-12 | 已到期合約 — 自動修正 | Contract.end_date < today 且 status='active' | 1. 執行 batch job 或 service 檢查過期合約 2. 確認 status | Contract.status 自動修正為 expired | contracts | P1 |
| TS-13 | 提前終止合約 | Contract.status='active'，start_date < today < end_date | 1. 點擊合約的「終止」按鈕 2. 確認 | Contract.status → 'terminated'；Room.status → 'vacant' | contracts | P0 |
| TS-14 | 提前終止 — 當月帳單已存在 | Contract 已有當月 MonthlyBill | 1. 終止合約 2. 查看當月帳單 | 合約已終止，當月帳單保留（不自動刪除） | contracts, billing | P1 |
| TS-15 | 未繳帳單 — Dashboard 顯示 | MonthlyBill.paid=false 的帳單存在 | 1. 開啟 /dashboard 2. 查看「未繳」統計 | 正確顯示未繳總額，來源為 MonthlyBill WHERE paid=0 | dashboard, billing | P0 |
| TS-16 | 未繳帳單 — Monthly Report | MonthlyBill.paid=false 的帳單存在 | 1. 開啟 /reports/monthly 2. 查看「未繳總額」 | 正確顯示未繳總額 | reports, billing | P0 |
| TS-17 | 溢繳 / 對帳 — PaymentRecord linked | PaymentRecord.record_status='linked' 且 amount > MonthlyBill.total | 1. 建立 PaymentRecord（amount > bill total） 2. 執行 reconciliation 3. 查看 | PaymentRecord record_status → 'linked'；MonthlyBill.paid = true；溢繳金額需有紀錄或標記 | payments | P0 |
| TS-18 | 溢繳 / 對帳 — 多筆付款合併 | 同一 MonthlyBill 有多筆 PaymentRecord | 1. 建立多筆 PaymentRecord 指向同一 MonthlyBill 2. 執行 reconciliation | 各筆 record_status 正確更新；MonthlyBill.paid = true 當總付款 >= bill total | payments | P1 |
| TS-19 | 溢繳 / 對帳 — 金額不足 | PaymentRecord.amount < MonthlyBill.total | 1. 建立 PaymentRecord（amount < bill total） 2. 執行 reconciliation | MonthlyBill.paid 保持 false；PaymentRecord record_status 保持 pending 或 verified（未 linked） | payments | P1 |
| TS-20 | 共用電表 — 多房間同一 meter | ElectricityMeter 被多個 Room 共用 | 1. 建立 ElectricityBill 指向共用 meter 2. 查看相關房間 | 各房間顯示相同的電表資訊；計費按比例分攤（ct_meter_proportional 或 dual_meter_tou） | electricity | P0 |
| TS-21 | 共用電表 — 快速抄表 | ElectricityMeter 被多個 Room 共用 | 1. 使用 /electricity/property/<pid>/quick-reading 2. 選擇電表 3. 輸入讀數 | 電表選擇從 ElectricityMeter 動態列出（不硬編碼 meter_id=1）；讀數正確寫入 | electricity | P0 |
| TS-22 | 共用水表 — 多房間分攤 | WaterBill 存在（billing_start, billing_end, total_amount） | 1. 建立 WaterBill（total_amount=3000, billing_start/billing_end 覆蓋帳期） 2. 查看相關房間 | 水費按 shared_by_stay_days 分攤至各 MonthlyBill.water_amount；WaterBill 為物件層級帳單 | water | P1 |
| TS-23 | year_month 格式轉換 — DB → UI | MonthlyBill.year_month = '202606' (DB) | 1. 開啟 bill list 2. 查看月份欄位 | UI 顯示 '2026-06'（透過 core/year_month.py to_ui()） | billing, core | P0 |
| TS-24 | year_month 格式轉換 — UI → DB | 使用者在表單輸入 '2026-06' | 1. 開啟 bill form 2. 輸入月份 '2026-06' 3. 儲存 | DB 寫入 '202606'（透過 core/year_month.py to_db()） | billing, core | P0 |
| TS-25 | year_month 格式轉換 — ElectricityBill | ElectricityBill.year_month = '202606' (DB) | 1. 開啟 electricity bill detail 2. 查看月份 | UI 顯示 '2026-06' | electricity, core | P0 |
| TS-26 | year_month 格式轉換 — Invalid Input | 使用者輸入 '2026/06' 或 '06-2026' | 1. 在 bill form 輸入非 YYYY-MM 格式 2. 提交 | 表單驗證失敗，顯示格式錯誤訊息 | billing, core | P1 |
| TS-27 | PaymentRecord 驗證 — 審核通過 | PaymentRecord.record_status='pending' | 1. 開啟 /payments 2. 點擊「審核通過」 | record_status → 'verified'；verified_by_id 和 verified_at 設定 | payments | P0 |
| TS-28 | PaymentRecord 驗證 — 拒絕 | PaymentRecord.record_status='pending' | 1. 開啟 /payments 2. 點擊「拒絕」 | record_status → 'rejected' | payments | P1 |
| TS-29 | PaymentRecord 連結狀態 — linked | PaymentRecord.record_status='verified' 且已對帳 | 1. 執行 reconciliation 2. 確認 contract_id 和 monthly_bill_id | record_status → 'linked'；contract_id 和 monthly_bill_id 已設定 | payments | P0 |
| TS-30 | PaymentRecord 連結狀態 — 未關聯 | PaymentRecord.record_status='pending' | 1. 開啟 /payments 2. 查看 Record List | 顯示「未關聯」（contract_id=NULL, monthly_bill_id=NULL） | payments | P1 |
| TS-31 | 月帳單總額與契約一致 | Contract.rent=15000, MonthlyBill 存在 | 1. 建立 MonthlyBill 2. 確認 total 計算 | MonthlyBill.total = rent + electricity_amount + public_electricity + water_amount + other_charges，與 billing-contract.md 公式一致 | billing | P0 |
| TS-32 | 電費顯示與來源一致 | ElectricityBill.amount=2500, MonthlyBill.electricity_amount=2500 | 1. 開啟 monthly bill detail 2. 查看電費 | MonthlyBill.electricity_amount = ElectricityBill.amount | billing, electricity | P0 |
| TS-33 | 水費顯示與來源一致 | WaterBill.total_amount=800, MonthlyBill.water_amount=800 | 1. 開啟 monthly bill detail 2. 查看水費 | MonthlyBill.water_amount = WaterBill.total_amount 經分攤後寫入 | billing, water | P0 |
| TS-34 | 月報總額與來源一致 | MonthlyBill 存在多筆資料 | 1. 開啟 /reports/monthly 2. 查看「應收總額」 | 報表總額 = SUM(MonthlyBill.total WHERE year_month)，與 DB 查詢結果一致 | reports | P0 |
| TS-35 | 房東報表總額與來源 | Landlord 存在，MonthlyBill 存在 | 1. 開啟 /reports/landlord-report 2. 選擇房東 3. 查看總額 | 報表總額 = SUM(MonthlyBill.total WHERE landlord_id)，與 DB 查詢結果一致 | reports | P1 |
| TS-36 | 房東報表 — 孤立報表驗證 | landlord_report.py Blueprint 未掛載 | 1. 確認舊版 /reports/landlord-report 無法存取 2. 確認新版已掛載 | 舊版：404；新版：正常顯示 | reports | P1 |
| TS-37 | Room.status 唯一來源 | Room 存在 | 1. 開啟 /rooms 2. 確認狀態顯示 | Room.status 僅顯示 vacant/occupied，無其他值 | rooms | P0 |
| TS-38 | Contract.status 唯一來源 | Contract 存在 | 1. 開啟 /contracts 2. 確認狀態顯示 | Contract.status 僅顯示 active/expired/terminated | contracts | P0 |
| TS-39 | PaymentRecord 狀態唯一來源 | PaymentRecord 存在 | 1. 開啟 /payments 2. 確認狀態顯示 | record_status 僅顯示 pending/verified/rejected/linked | payments | P0 |
| TS-40 | Dashboard 月份切換 | 多月份帳單存在 | 1. 開啟 /dashboard 2. 切換月份 3. 查看統計 | 統計數據隨月份切換正確更新 | dashboard | P1 |
| TS-41 | 水費帳單 billing_end 晚於 billing_start | WaterBill 資料建立中 | 1. 嘗試建立 WaterBill（billing_end <= billing_start） 2. 確認 | 表單驗證失敗，顯示「billing_end 必須晚於 billing_start」 | water | P1 |
| TS-42 | 水費帳單 total_amount 不可小於 0 | WaterBill 資料建立中 | 1. 嘗試建立 WaterBill（total_amount=-100） 2. 確認 | 表單驗證失敗，顯示金額不可為負 | water | P1 |
| TS-43 | Contract 費率回退到房東預設 | Contract.electricity_rate=NULL, Landlord.electricity_rate=5.0 | 1. 建立 MonthlyBill 2. 查看電費計算 | 電費計算使用 Landlord.electricity_rate=5.0 作為回退值 | billing, contracts | P1 |

---

## Coverage Notes

- 11 個頁面全部覆蓋：Dashboard, Landlords, Properties/Rooms, Tenants, Contracts, Monthly Bills, Electricity, Water, Payments, Monthly Report, Landlord Report
- 所有 P0 測試情境均涵蓋 reasonix 正式結論（year_month, PaymentRecord, Room.status, 虛擬 tenant）
- 所有欄位名稱已對齊正式資料契約（core-entities.md, billing-contract.md, water-contract.md, payments-contract.md, status-machines.md）
- Dead code 路由（/payment/new 等 5 個）不納入測試
- Landlord Report 標記為孤立報表，需在新版中重新設計並驗證

## Missing Preconditions Or Data

- PaymentRecord 表為空，測試前需手動建立測試資料
- 虛擬 tenant 清理前的舊資料測試無法執行（需 migration 完成後）
- 共用電表/水表的測試資料需額外準備
- Contract 自動過期修正的 batch job 實作尚未確認（由 box agent 處理）
