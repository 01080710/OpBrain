# 變更紀錄（team-structure）

> **核心問題**：這個 Skill 的文件、設定、腳本改了什麼、何時、為什麼？
> **狀態**：`active`｜**最後更新**：2026-10-04｜**負責人**：Howard Huang（OP）

由 `brain/_tools/kb_log_change.py` 自動新增；表格必須是本檔最後一個表格。

| 版本 | 日期 | 檔案 | 摘要 | 原因 | 作者 |
|---|---|---|---|---|---|
| 1.0.0 | 2026-10-02 | 全部 | 依 OpBrain 格式建立；Roster 規則從 3 個舊工具整併為 R-001～R-006；新增 roster_check.py | DEC-001 | Claude（與使用者確認） |
| 1.1.0 | 2026-10-04 | skill.md,context.md,rules.md,decision.md,flows/check.md,trace/decisions.md,trace/issues.md,trace/changes.md,scripts/roster_check.py（僅 docstring）,config/roster.yaml（僅註解） | 文件由 11 資料夾 40 份改為 8 份：必備檔 + rules.md + flows/check.md；所有 ID 保留；腳本邏輯與設定值不變 | DEC-004 | Claude（與使用者確認） |
| 1.1.1 | 2026-10-04 | trace/decisions.md | check 流程自動寫入稽核紀錄（共用執行器）；腳本與設定值不變 | DEC-005 | Claude（與使用者確認） |
