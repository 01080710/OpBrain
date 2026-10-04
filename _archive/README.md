# _archive — 已停用的程式（只供參考，不要使用、不要 import）

2026-10-02 重構為 OpBrain 格式（productivity DEC-012）後封存。現行版本全部在 `brain/`。

| 資料夾 | 內容 | 為什麼封存 |
|---|---|---|
| `abandoned_pbi_auto_login/` | Power BI 自動登入嘗試（pbi_login.py、_pbi_login_wait.py、pbi_workflow.py、run_pbi.bat） | 未完成即放棄（productivity DEC-010） |
| `skeleton_never_implemented/` | 最初的每日 Pipeline 骨架（main.py、metrics、reports、ai、lark_collector…）、舊 config/settings.py、空的 tests/output/logs | 全是 `NotImplementedError`，從未接上任何資料 |
| `legacy_working_code/` | 重構前可用的舊工具（src/、fresh_ac_report/、run_*.py） | 已拆成 `brain/productivity/scripts/` 的步驟腳本，並逐格驗證輸出相同 |

舊的專案文件（PROJECT.md、DECISIONS.md…）內容已搬進各 Skill，原檔在
`Desktop/OP_Workforce_AI_backup_20261002.zip`（含舊的 Git 歷史）。
