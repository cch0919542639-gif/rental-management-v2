# Task Board

這是 repo 內的檔案式任務板，用來取代不穩定的 localhost kanban。

## Columns

- `backlog/`
- `ready/`
- `in_progress/`
- `review/`
- `done/`
- `blocked/`

## Rule

- 一個 task = 一個 markdown 檔
- 檔名格式：
- `YYYY-MM-DD_<phase>_<owner>_<short-task>.md`

## Required Fields

- Title
- Owner
- Phase
- Goal
- Allowed Files
- Do Not Touch
- Acceptance
- Dependencies
- Status

## Flow

1. Codex 建 task 檔到 `ready/`
2. agent 接手後移到 `in_progress/`
3. 完成後移到 `review/`
4. Codex 驗收後移到 `done/`
5. 若卡住移到 `blocked/`
