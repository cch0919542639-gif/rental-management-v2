# TODO - box agent（封閉小任務／腳本索引／README 模板／migration-repair 補件）

- [ ] Step 0: 更新 coordination/progress/box.md 為 IN_PROGRESS
- [ ] Step 1: 盤點 scripts/（migration/repair）與既有 check_/fix_/debug_/verify_/create_/update_/test_/*.bak 腳本（若存在舊專案路徑再補）
- [ ] Step 2: 依模板建立 docs/reports/box-script-index.md：分類 + Keep/Archive/Rewrite + 建議新位置
- [ ] Step 3: 依模板建立/補齊 docs/reports/box-module-readme-templates.md：提供可重複使用模組 README 樣板（含責任/輸入/輸出/依賴/風險/測試等）
- [ ] Step 4: 更新 evidence/box-small-fix-notes.md：只填封閉小修補與 migration/repair 候選
  - [ ] user/users 合併需求
  - [ ] MonthlyBill.year_month 正規化
  - [ ] ElectricityBill.year_month 正規化
  - [ ] 虛擬 tenant 清理
  - [ ] Contract.status 過期修正
  - [ ] Room.status 非標準 mapping
  - [ ] mimo 回歸清單中錯誤 evidence SQL 修正候選（共用電表 room_meters）
- [ ] Step 5: 每完成一個輸出更新 coordination/completed/box.md
- [ ] Step 6: 交付結果彙整到 attempt_completion

