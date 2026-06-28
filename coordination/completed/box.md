# box Completed Log

Completed Time: 2026-06-28 00:00

## Completed Items

- Script Index：整理舊專案 `D:\rental\` 內 `check_/fix_/debug_/verify_/create_/update_/test_` 與 `*.bak*` 腳本，分類 Keep/Archive/Rewrite，並建議新位置。
- Module README Templates：建立可重複使用的模組 README 樣板（responsibility/inputs/outputs/dependencies/risks/tests），並標記 billing/electricity/water、payments、reports、integrations 等需額外章節的模組類型。
- Small Fix Notes：僅記錄上游切割清楚的小修補與 migration/repair 候選（包含 `user/users` 合併、`MonthlyBill.year_month` 與 `ElectricityBill.year_month` 正規化、虛擬 tenant 清理、`Contract.status` 過期修正、`Room.status` 非標準 mapping、mimo 回歸 evidence SQL 修正候選）。

## Output Files

- `D:/CodexRuntime/rental/rebuild/docs/reports/box-script-index.md`
- `D:/CodexRuntime/rental/rebuild/docs/reports/box-module-readme-templates.md`
- `D:/CodexRuntime/rental/rebuild/evidence/box-small-fix-notes.md`

## Validation / Verification

- 檢查上述檔案已符合模板格式與欄位要求（表格欄位存在、必填章節/欄位已填入）。
- 內容上遵守規範：不重新定義資料契約、不修改 reasonix 已凍結規則、僅做腳本索引/README 樣板/repair-migration 候選整理。

Remaining: 無

