# open

Status: COMPLETED
Last Updated: 2026-06-28

## Current Task

- 所有 4 份報告已產出，待 reasonix 驗收

## Scope

- 盤點 D:\rental\ 所有 route、template、table、external script
- 映射到 rebuild 新模組結構

## Completed So Far

1. 讀完 reasonix 三份報告（architecture-decision, data-contract-audit, dependency-map）
2. 讀完 rewrite-roadmap、target-structure、agent-work-rules
3. 掃描 app.py (1783行) 完整 route 清單
4. 掃描 templates/ (37個檔案)
5. 掃描外部 Python 腳本 (54個檔案)
6. 掃描 app.aliyun.py、electricity_bp.py、water_bill.py、landlord_report.py
7. 產出 open-route-template-matrix.md（35+11+4+1 routes 完整映射）
8. 產出 open-schema-inventory.md（16 表 + field mismatches）
9. 產出 open-cleanup-candidates.md（52 腳本分類）
10. 產出 open-module-mapping.md（50+ 項目映射 + 6 大 tangle + 5 個 first moves）

## Next Step

- 等待 reasonix 驗收 Phase 0 關卡 A

## Risks / Blockers

- 無

## New Discovery Summary

1. **landlord_report.py Blueprint 從未註冊**（已在 cleanup-candidates 詳細記錄）
2. **app.aliyun.py admin payment routes 在 main guard 後**，gunicorn/flask run 模式永不註冊
3. **app.aliyun.py 累進稅率用 ROUND_HALF_UP**，app.py 用 ROUND_UP — 兩版本計算結果可能差 1 元以內
