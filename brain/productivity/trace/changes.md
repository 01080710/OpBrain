# 變更紀錄（productivity）

> **核心問題**：這個 Skill 的文件、設定、腳本改了什麼、何時、為什麼？
> **狀態**：`active`｜**最後更新**：2026-10-04｜**負責人**：Howard Huang（OP）

由 `brain/_tools/kb_log_change.py` 自動新增；表格必須是本檔最後一個表格。

重構前的歷史（2026-09-01～10-01）摘要：PBI 下載／合併穩定（09-02）；Lark Chatgroup、Tickets 篩選、Fresh AC 報表建立（09-02）；PBI Pipeline、VN5（09-03）；Lark 單檔格式、IB 改名、Roster 全員報表（09-21）；DW Fresh 報表、大小寫修正、Fresh 一次跑完（10-01～02）。完整舊紀錄在 `Desktop/OP_Workforce_AI_backup_20261002.zip`。

| 版本 | 日期 | 檔案 | 摘要 | 原因 | 作者 |
|---|---|---|---|---|---|
| 1.0.0 | 2026-10-02 | 全部 | 依 OpBrain 格式重建：3 條具名流程、18 個步驟腳本、5 份設定檔、40 份文件；回歸測試 17 檔逐格相同 | DEC-012 | Claude（與使用者確認） |
| 1.1.0 | 2026-10-04 | skill.md,context.md,decision.md,flows/pbi.md,flows/fresh.md,flows/chatgroup.md,trace/decisions.md,trace/issues.md,trace/changes.md,scripts/*.py（僅 docstring 文件路徑）,config/*.yaml（僅註解） | 文件由 11 資料夾 40 份改為 9 份：必備檔 + 每條流程一份 flows/；所有 ID 保留；腳本邏輯與設定值不變 | DEC-016 | Claude（與使用者確認） |
| 1.2.0 | 2026-10-04 | skill.md,sources.md,flows/ac.md,flows/dw.md,context.md,trace/decisions.md,trace/issues.md | 文件依業務線拆分：flows/ac.md、flows/dw.md + 共用 sources.md（取代 flows/pbi、fresh、chatgroup）；新增 I-010；指令、腳本邏輯、設定值不變 | DEC-017 | Claude（與使用者確認） |
| 1.2.1 | 2026-10-04 | trace/decisions.md,_core/framework.md,_core/lib/opbrain/audit.py,_core/lib/opbrain/workflow.py,_core/lib/opbrain/paths.py,_tools/audit_verify.py,_tools/_kb.py,_tools/template/compliance.md,_core/conventions.md,_core/data-layout.md | 預留金融科技框架（三層架構、資料分區與機敏等級、compliance 範本）；流程執行器自動寫入 data/audit/ 雜湊鏈稽核紀錄；腳本邏輯、設定值、報表輸出不變（回歸測試 17 檔相同，2 份 Tickets CSV 僅換行字元 CRLF/LF 不同，屬 Mac/Windows 差異） | DEC-018 | Claude（與使用者確認） |
