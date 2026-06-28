# 給其他 Agent 的 GitHub 上傳指令

以下文字可直接貼給任何接手上傳 GitHub 的 agent。

```text
請將 D:\CodexRuntime\rental\rebuild 整理成可上傳 GitHub 的工作樹，並依以下規則執行：

1. 先讀：
- D:\CodexRuntime\rental\rebuild\README.md
- D:\CodexRuntime\rental\rebuild\CONTRIBUTING.md
- D:\CodexRuntime\rental\rebuild\COLLABORATION_RULES.md
- D:\CodexRuntime\rental\rebuild\docs\operations\github-upload-checklist.md
- D:\CodexRuntime\rental\rebuild\docs\operations\github-branch-and-pr-flow.md
- D:\CodexRuntime\rental\rebuild\docs\operations\github-second-round-collaboration.md

2. 檢查以下內容不可提交：
- .env / .env.*
- runtime.db / *.db / *.sqlite*
- __pycache__/
- .venv/ / venv/
- IDE 本機設定

3. 執行 preflight：
- powershell -ExecutionPolicy Bypass -File D:\CodexRuntime\rental\rebuild\scripts\github_preflight_check.ps1

4. 若 preflight 無阻塞，初始化或接續 git：
- git init
- git status
- git add .
- git status

5. 建立第一個 commit：
- git commit -m "chore: prepare rental rebuild workspace for GitHub collaboration"

6. 若使用 GitHub remote：
- git branch -M main
- git remote add origin <repo-url>
- git push -u origin main

7. 完成後更新：
- D:\CodexRuntime\rental\rebuild\coordination\progress\<agent>.md
- D:\CodexRuntime\rental\rebuild\coordination\completed\<agent>.md

8. 若發現敏感檔案、衝突或不確定是否可上傳：
- 立即新增 incident 檔到 D:\CodexRuntime\rental\rebuild\coordination\incidents\
- 不要硬推送

交付時請回報：
- git status 結果
- 是否已建立 commit
- 是否已成功 push
- 若未 push，卡在哪一步
```
