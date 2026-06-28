# Route Template Matrix

Date: 2026-06-28
Author: open

## Main app.py Routes (Direct app.route, ~35 routes)

| Route / Blueprint | Methods | Handler | Template | Query / Data Source | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `/login` | GET,POST | login | auth/login.html | User.query | P1 | 表單認證 |
| `/logout` | GET | logout | redirect | — | P1 | 清除 session |
| `/` | GET | dashboard | dashboard.html | Contract, MonthlyBill 匯總查詢 | P0 | year_month 在 app.py 與 app.aliyun.py 格式不同 |
| `/landlords` | GET | landlord_list | landlord/list.html | Landlord.query.all() | P2 | 無特殊邏輯 |
| `/landlords/create` | GET,POST | landlord_create | landlord/form.html | Landlord(), db.session.add | P2 | 含表單驗證 |
| `/landlords/<int:id>/edit` | GET,POST | landlord_edit | landlord/form.html | Landlord.query.get_or_404(id) | P2 | |
| `/landlords/<int:id>/delete` | POST | landlord_delete | redirect | Landlord.query.get_or_404(id) | P2 | |
| `/landlords/<int:lid>/properties/create` | GET,POST | property_create | room/property_form.html | Landlord + Property | P2 | 房東下新增房產 |
| `/rooms` | GET | room_list | room/list.html | Room.query + Property/Landlord join | P2 | |
| `/properties/<int:pid>/rooms/create` | GET,POST | room_create | room/form.html | Property + Room | P2 | |
| `/rooms/<int:id>/edit` | GET,POST | room_edit | room/form.html | Room.query.get_or_404(id) | P2 | |
| `/tenants` | GET | tenant_list | tenant/list.html | Tenant.query.all() | P2 | |
| `/tenants/create` | GET,POST | tenant_create | tenant/form.html | Tenant(), db.session.add | P2 | |
| `/tenants/<int:id>/edit` | GET,POST | tenant_edit | tenant/form.html | Tenant.query.get_or_404(id) | P2 | |
| `/tenants/<int:id>/delete` | POST | tenant_delete | redirect | Tenant.query.get_or_404(id) | P2 | |
| `/contracts` | GET | contract_list | contract/list.html | Contract.query + joins | P2 | |
| `/contracts/create` | GET,POST | contract_create | contract/form.html | Contract(), 含表單驗證 | P2 | |
| `/contracts/<int:id>/edit` | GET,POST | contract_edit | contract/form.html | Contract.query.get_or_404(id) | P2 | |
| `/contracts/<int:id>/terminate` | POST | contract_terminate | redirect | Contract.query.get_or_404(id) | P1 | 修改 Contract.status |
| `/contracts/<int:cid>/bills` | GET | bill_list | bill/list.html | Contract + MonthlyBill | P1 | 合約帳單列表 |
| `/contracts/<int:cid>/bills/create` | GET,POST | bill_create | bill/form.html | MonthlyBill + UtilityCalculator.generate_bill() | P0 | 混入計費邏輯，year_month 格式不一致 |
| `/bill/batch_entry` | GET,POST | batch_bill_entry | bill/batch_entry.html | 多合約批次操作 | P0 | year_month 格式不一致 |
| `/bills/<int:id>/toggle_paid` | POST | bill_toggle_paid | redirect | MonthlyBill.query.get_or_404(id) | P1 | 直接 flip paid boolean，無對帳流程 |
| `/bills/generate` | POST | bills_generate | redirect | 所有 active contract 批次產生月帳單 | P0 | year_month 格式不一致 |
| `/reports/monthly` | GET | report_monthly | report/monthly.html | MonthlyBill + Contract + Room + Property + Landlord 多表 join | P0 | 虛擬 tenant 關鍵字判定空房；app.py 與 app.aliyun.py 實作不同 |
| `/reports/summary` | GET | report_summary | report/summary.html | 同上 + 匯總計算 | P0 | year_month 格式不一致 |
| `/api/analyze-receipt` | POST | api_analyze_receipt | JSON | receipt_ocr module + requests (LLM API) | P1 | 外部 API 呼叫，OCR 流程 |
| `/api/payment-records` | GET,POST | api_payment_records | JSON | PaymentRecord.query | P1 | CRM對帳用 |
| `/api/payment-records/<int:id>/verify` | POST | api_verify_payment | JSON | PaymentRecord + verified_by | P1 | |
| `/api/payment-records/<int:id>/analyze` | POST | api_analyze_payment | JSON | PaymentRecord + receipt_ocr | P1 | |
| `/payments` | GET | payment_list | payment/list.html | PaymentRecord.query | P1 | |
| `/callback` | POST | callback | text | LINE Bot Webhook | P1 | 外部整合 |
| `/sheets/import` | GET,POST | sheets_import | sheets/import.html | scripts.smart_import | P1 | Google Sheets 匯入 |
| `/api/electricity/create-from-ocr` | POST | api_electricity_create | JSON | ElectricityBill + ElectricityReading | P0 | 硬編碼 meter_id=1，year_month 格式不一致 |
| `/payment/new` | GET,POST | payment_new | payment/new.html | Payment class (未定義) | P0 | **死碼** — NameError |
| `/payment/history` | GET | payment_history | payment/history.html | Payment class (未定義) | P0 | **死碼** — NameError |
| `/admin/payments` | GET | admin_payments | payment/admin_list.html | Payment class (未定義) | P0 | **死碼** — NameError |
| `/admin/payment/<int:pid>/confirm` | POST | admin_confirm_payment | redirect | Payment class (未定義) | P0 | **死碼** — NameError |
| `/admin/payment/<int:pid>/cancel` | POST | admin_cancel_payment | redirect | Payment class (未定義) | P0 | **死碼** — NameError |

## Blueprint: electricity_bp (prefix `/electricity`)

| Route / Blueprint | Methods | Handler | Template | Query / Data Source | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `/electricity/` | GET | index | electricity/index.html | Property + ElectricityBill 匯總 | P2 | |
| `/electricity/property/<int:property_id>/bills` | GET | property_bills | electricity/property_bills.html | Property + ElectricityBill | P1 | |
| `/electricity/property/<int:property_id>/new-bill` | GET,POST | new_bill | electricity/new_bill.html | ElectricityBill + ElectricityReading + ct_meter_proportional/dual_meter_tou | P0 | 混入計算公式；硬編碼 meter_id=1 ；year_month 格式不一致 |
| `/electricity/bill/<int:bill_id>/readings` | GET,POST | edit_readings | electricity/edit_readings.html | ElectricityBill + ElectricityReading | P1 | |
| `/electricity/property/<int:property_id>/quick-reading` | GET,POST | quick_reading | electricity/quick_reading.html | 快速抄表 + ElectricityReading | P1 | 硬編碼 meter_id=1 |
| `/electricity/property/<int:property_id>/reading-log` | GET | reading_log | electricity/reading_log.html | ElectricityReading | P2 | |

## Blueprint: water_bill (註冊方式：register_routes 直接掛在 app 上)

| Route / Blueprint | Methods | Handler | Template | Query / Data Source | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `/water/bills` | GET | water_bills_list | water/bills_list.html | WaterBill + Property | P1 | 僅註冊於 app.py，app.aliyun.py 未註冊 |
| `/water/bills/new` | GET,POST | water_bills_new | water/bill_form.html | WaterBill + calc_water_by_days | P1 | 混入計算公式 |
| `/water/preview` | POST | water_preview | water/bill_result.html | 水費試算結果 | P1 | |
| `/water/bills/<int:id>/delete` | POST | water_bills_delete | redirect | WaterBill | P2 | |

## Blueprint: landlord_report (未註冊於任何 app variant)

| Route / Blueprint | Methods | Handler | Template | Query / Data Source | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `/reports/landlord-report` | GET | landlord_report | report/landlord_report.html | Landlord + Property + Room + Contract + Tenant + MonthlyBill + PaymentRecord | P2 | **未註冊** — Blueprint 定義但從未被 app.register_blueprint 掛載 |

## Error Handlers

| Route / Blueprint | Methods | Handler | Template | Risk Level | Notes |
| --- | --- | --- | --- | --- | --- |
| 404 (errorhandler) | — | not_found | error/404.html | P2 | |
| 500 (errorhandler) | — | server_error | error/500.html | P2 | |

## Missing Templates

- 無 (所有 render_template 路徑均有對應檔案在 templates/ 中)

## Templates With No Known Route

| Template | Likely Cause |
| --- | --- |
| `report/landlord_report.html` | 僅被未註冊的 landlord_report.py Blueprint 使用 |
| `bill/list.html.bak_rounding` | 備份殘留 |
| `report/monthly.html.bak_rounding` | 備份殘留 |
| `report/landlord_report.html.bak_rounding` | 備份殘留 |

## High Risk Route Findings

1. **5 個 Payment 死碼 route** (P0): `/payment/new`, `/payment/history`, `/admin/payments`, `/admin/payment/<int:pid>/confirm`, `/admin/payment/<int:pid>/cancel` 使用不存在的 `Payment` class，執行會 NameError。reasonix 已決議不移植到新版。
2. **app.aliyun.py 中 admin payment routes 在 `if __name__ == '__main__'` 之後** (P0): 這 5 個 route 在 app.aliyun.py 中也定義在 main guard 後，gunicorn/flask run 模式下永遠不會註冊。
3. **year_month 格式散落** (P0): route 層各自轉換 YYYY-MM ↔ YYYYMM，新舊 app 變體 (app.py vs app.aliyun.py) 行為不一致。
4. **電費 route 硬編碼 meter_id=1** (P0): electricity_bp.py 與 api_electricity_create 共 6 處使用 `meter_id=1`，多電表場域會直接錯誤。
5. **report_monthly() 雙實作** (P0): app.py 使用 tenant.name 關鍵字 + DummyBill；app.aliyun.py 用 JOIN 查詢，行為不同。
