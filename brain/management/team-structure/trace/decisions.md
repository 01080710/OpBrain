# 決策紀錄（team-structure）

> **核心問題**：做過哪些重要決策？當時的脈絡與理由是什麼？
> **狀態**：`active`｜**最後更新**：2026-10-04｜**負責人**：Howard Huang（OP）

### DEC-001：team-structure 是 Roster 的唯一擁有者
- 日期：2026-10-02　決定者：使用者　狀態：採用
- 背景：Roster 由 3 個工具各自讀取，規則不一致（大小寫、表頭、空白處理）。
- 選項：A. 各工具各自讀　B. 一個 Skill 擁有、共用程式讀取
- 決定與理由：B。使用者確認「架構」= 團隊組織架構，其他 Skill（含未來 Item list）都依賴它。
- 後果：其他 Skill 不得自行讀 Roster；規則改動只改本 Skill。

### DEC-002：接受 `CRM OP Name` 作為正式姓名欄
- 日期：2026-10-01　決定者：AI 修正、使用者知悉　狀態：採用
- 背景：2026-09 Roster 把 `OP Name` 改名為 `CRM OP Name`，內容相同（只多了 Marcus）。
- 決定：兩個表頭都接受（R-002）。

### DEC-003：空白姓名列一律略過
- 日期：2026-10-01　狀態：採用
- 背景：見 INV-001。決定：略過（R-003），並在檢查報告中提醒。

### DEC-004：文件由 40 份固定模板改為「必備檔 + 每條流程一份」
- 日期：2026-10-04　決定者：使用者　狀態：採用
- 背景：每個 Skill 被強制建滿 11 個資料夾 40 份文件；本 Skill 只有一條流程，40 份中有 3 份「不適用」、19 份內容不到 200 字，且安全、合規等共通規則在各 Skill 重抄。
- 選項：A. 維持 40 份　B. 依資料夾合併成約 13 份　C. 必備檔 + 每條流程一份（flows/）
- 決定：C。`skill.md`、`context.md`、`decision.md`、`trace/` 三份為必備；跨流程共用規則放選用的 `rules.md`；流程專屬的輸入、規則、步驟、檢查、輸出、例外寫在 `flows/<流程>.md`。所有 ID 原樣保留，腳本邏輯與設定值不變（只改註解中的文件路徑）。
- 取捨：失去「一個主題一份檔」的細格子，換來一條流程讀一份檔；檔案過長時（`kb_check_structure.py` 警告 S-7）再拆。
- 後果：新 Skill 用 `brain/_tools/template/` 的新骨架；舊版備份在 `OP_Workforce_AI_brain_backup_20261004.tar.gz`（專案上一層）。

### DEC-005：預留金融科技框架與稽核紀錄
- 日期：2026-10-04　決定者：使用者　狀態：採用
- 決定：同 productivity:DEC-018。本 Skill 的 `check` 流程同樣自動寫入 `data/audit/`；腳本、設定值不變。
- 後果：`_core/lib/opbrain/roster.py` 在框架層寫死本 Skill 與 OP 欄位，違反 `_core/framework.md` F-1；搬移到本 Skill 或 `_domain/` 時另行決定。

### DEC-006：只註冊母入口 brain/skill.md，修復 _core 拆分後的路徑
- 日期：2026-10-05　決定者：使用者　狀態：採用
- 決定：同 productivity:DEC-019。本 Skill 改由 `brain/management/domain.md` 收錄；`scripts/_bootstrap.py` 改指向 `brain/_framework/lib`；`roster.py` 留在 `brain/_framework/lib/opbrain/`（DEC-005 所述 F-1 問題未變，搬移另行決定）。腳本、設定值不變。

### DEC-007：Skill 扁平放置、組織層 _domain 改名 _org
- 日期：2026-10-05　決定者：使用者　狀態：採用
- 決定：同 productivity:DEC-020。本 Skill 留在 `brain/team-structure/`，可被多個領域的 `brain/<領域>/domain.md` 收錄；文件中的 `_domain/` 路徑改為 `_org/`。腳本、設定值不變。

### DEC-008：Skill 放在擁有它的領域底下
- 日期：2026-10-05　決定者：使用者　狀態：採用（取代 DEC-007 的扁平放置）
- 決定：同 productivity:DEC-021。本 Skill 搬到 `brain/management/team-structure/`，由 management 擁有；其他領域需要 Roster 時，在自己的 `brain/<領域>/domain.md` 跨資料夾引用本 Skill。腳本、設定值不變。
