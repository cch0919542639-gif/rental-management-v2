# Phase 5 Rollback Checklist

Last Updated: 2026-07-02

## Trigger

出現以下任一狀況時，停止 cutover 並啟動 rollback 評估：

- row parity 無法通過
- bridge 後 `alembic_version` 不一致
- production health check 失敗
- 關鍵頁面無法載入或資料錯亂

## Immediate Actions

1. 停止進一步 migration / import / app 寫入
2. 保留當前日誌、manifest、migration list 輸出
3. 確認最近一次 source / target backup 可用

## Rollback Baseline

- SQLite source 仍為回退基線
- PostgreSQL target 若為 rehearsal，可直接重建
- 若已進正式 cutover，先以 backup/restore 文件為準，不在未驗證狀況下手動修表

## Required Evidence

- `run_migrations.py --list` 輸出
- `bridge_drill_checklist.py` 輸出
- `verify_row_parity.py` 輸出
- `health_check.py --config production` 輸出
- 錯誤時間點與操作人記錄
