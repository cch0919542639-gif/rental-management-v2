# GitHub 上傳前檢查清單

Last Updated: 2026-06-28

## Goal

這份清單用來確認 `D:\CodexRuntime\rental\rebuild` 已經適合上傳到 GitHub，且不會把本機資料、暫存物或敏感資訊一併送上去。

## Must Confirm

- 已閱讀 `README.md`
- 已閱讀 `CONTRIBUTING.md`
- 已閱讀 `COLLABORATION_RULES.md`
- 已閱讀 `docs/operations/github-branch-and-pr-flow.md`
- 已閱讀 `docs/operations/github-second-round-collaboration.md`

## Files That Must Exist

- `.gitignore`
- `.gitattributes`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `CONTRIBUTING.md`
- `COLLABORATION_RULES.md`
- `docs/operations/phase1-master-status.md`
- `coordination/progress/codex.md`

## Must Not Upload

- `.env`
- `.env.*`
- `runtime.db`
- `*.db`
- `*.sqlite`
- `*.sqlite3`
- `__pycache__/`
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/`
- `.venv/`
- `venv/`
- 本機 IDE 設定資料夾

## Recommended Preflight

執行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\github_preflight_check.ps1
```

若腳本輸出 warning，先確認是否需要刪除、移動或加入 `.gitignore`。

## Upload Scope

應上傳：

- `app/`
- `coordination/`
- `data_contracts/`
- `docs/`
- `evidence/`
- `scripts/`
- `tests/`
- `README.md`
- `TODO.md`
- `CONTRIBUTING.md`
- `COLLABORATION_RULES.md`

## Final Sanity Check

- branch 名稱符合規則
- `coordination/progress/<agent>.md` 已更新
- 若是收尾上傳，`coordination/completed/<agent>.md` 已更新
- 沒有未記錄的資料契約變更
