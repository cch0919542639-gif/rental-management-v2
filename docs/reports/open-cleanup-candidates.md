# Cleanup Candidates

Date: 2026-06-28
Author: open

## Files To Archive

| File | Reason | Safe To Archive | Notes |
| --- | --- | --- | --- |
| `D:\rental\app.aliyun.py` | 部署變體，邏輯與 app.py 有小差異（year_month 格式、計算四捨五入、缺 public_electricity 欄位、無水費）。已非現行使用版本。 | yes | 保留作為 migrat ion 驗證參考，不參與重建 |
| `D:\rental\app.asus.py` | ASUSTOR NAS 部署變體，2135 行，內含自己的 electricity Blueprint（非 electricity_bp.py）。無水費。 | yes | 保留作為 NAS 部署參考 |
| `D:\rental\templates\bill\list.html.bak_rounding` | 備份殘留，無 route 使用 | yes | |
| `D:\rental\templates\report\monthly.html.bak_rounding` | 備份殘留，無 route 使用 | yes | |
| `D:\rental\templates\report\landlord_report.html.bak_rounding` | 備份殘留，無 route 使用 | yes | |

## Files To Convert Into Formal Scripts

| File | Current Purpose | New Home | Why |
| --- | --- | --- | --- |
| `D:\rental\config.py` | Config class 含明文金鑰 | `rebuild/app/core/config/` | 改環境變數，移除明文 API key |
| `D:\rental\electricity_bp.py` | 電費 Blueprint（6 routes, 含計算公式） | `rebuild/app/modules/electricity/` | 拆為 routes.py + service + repository |
| `D:\rental\water_bill.py` | 水費 route 群（4 routes, 含計算公式） | `rebuild/app/modules/water/` | 拆為 routes.py + service + repository |
| `D:\rental\landlord_report.py` | 房東報表 Blueprint（未註冊） | `rebuild/app/modules/reports/` | 重新設計後正式掛載 |
| `D:\rental\receipt_ocr.py` | 收據 OCR + LLM 分析模組 | `rebuild/app/integrations/ocr/` | 保留演算法，重構 API |
| `D:\rental\ct_meter_proportional.py` | CT 比流器電費計算 | `rebuild/app/services/electricity_calculator.py` | 合併為統一電費計算 service |
| `D:\rental\dual_meter_tou.py` | 雙電表時間電價計算 | `rebuild/app/services/electricity_calculator.py` | 同上，作為 calculator 的演算法實作 |

## Possible Dead Code

| File / Symbol | Evidence | Risk If Removed | Suggested Verification |
| --- | --- | --- | --- |
| `Payment` class (不存在) | 5 個 route 引用但從未定義於任何原始碼 | 無 — 執行時必 NameError | 已在 app.py 確認無 Payment class 定義；route 在 app.py 與 app.aliyun.py 中皆無法正常執行 |
| `/payment/new`, `/payment/history`, `/admin/payments`, `/admin/payment/<int:pid>/confirm`, `/admin/payment/<int:pid>/cancel` | 引用不存在的 Payment class，且 app.aliyun.py 中定義在 `if __name__ == '__main__'` guard 後 | 零風險 | reasonix 已決議不移植 |
| `landlord_report.py` Blueprint `landlord_report_bp` | Blueprint 定義完整（421 行）但從未被任何 app variant 的 `app.register_blueprint()` 呼叫 | Medium — 功能完整但無人使用 | 確認三個 app variant（app.py, app.aliyun.py, app.asus.py）均無此 register_blueprint 呼叫 |
| `templates/report/landlord_report.html` | 僅被未註冊的 landlord_report.py 使用 | Medium — 無人使用的模板 | 確認 landlord_report.py 未被掛載 |
| `D:\rental\add_cache_control.py` | 遠端伺服器維修腳本，寫死 `/opt/rental/app.py` 路徑 | Low — 本機不相關 | 僅適用於特定部署環境 |
| `D:\rental\read_route.py`, `read_report_route.py` | 遠端伺服器除錯腳本，寫死 `/opt/rental/app.py` 路徑 | Low — 本機不相關 | 僅適用於特定部署環境 |

## Immediate Low Risk Fixes

| File | Problem | Suggested Fix | Risk |
| --- | --- | --- | --- |
| app.py:1753,1762,1776 | 使用 `abort` 但未 import | 新增 `from flask import abort` | P0 — 執行到該 route 時會 NameError（雖然 route 本身就是死碼） |
| app.py:27-29 | LINE SDK import 在頂層 | 移至延遲 import 或在有 LINE config 時才載入 | P2 — 非 LINE 環境啟動會報錯 |

## Escalate To Reasonix

- 無。所有發現與 reasonix 結論一致，無矛盾。但有一項新發現需記錄：

**New Discovery**: `landlord_report.py` 定義了完整的 Blueprint（421 行）和 `/reports/landlord-report` 路由以及 `report/landlord_report.html` 模板，但在 `app.py`、`app.aliyun.py`、`app.asus.py` 三種 app variant 中均未執行 `app.register_blueprint(landlord_report_bp)`。這表示：
- 該報表功能從未在現行系統中實際提供
- 模板 `report/landlord_report.html` 為孤兒模板
- `get_landlord_summary()` 函數也從未被調用

建議新版 `/reports` 模組重新設計此報表，不必保留舊實作。
