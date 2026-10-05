# 決策紀錄（productivity）

> **核心問題**：做過哪些重要決策？當時的脈絡與理由是什麼？
> **狀態**：`active`｜**最後更新**：2026-10-04｜**負責人**：Howard Huang（OP）

### DEC-001：PBI 瀏覽器互動邏輯凍結
- 日期：2026-09-01～02　決定者：使用者　狀態：採用
- 背景：selector、dispatch_event 點擊、CDP 下載設定、mtime 偵測、`.fill()` 日期輸入，每一項都是排除實際失敗後定案。
- 決定：`scripts/_lib/pbi_browser.py` 視為凍結，未經指示與真實 Power BI 重新驗證不得修改。2026-10-02 重構時原封不動搬入。

### DEC-002：PBI 合併依欄名對齊、缺欄補空
- 日期：2026-09-02　決定者：使用者　狀態：採用
- 背景：WD WL by Group 某些天整欄（例 Ewallet）消失。選項：A. 要求完全一致否則報錯　B. 依欄名對齊補空
- 決定：B；但多出或順序不同的欄仍視為錯誤（R-006）。

### DEC-003：Chatgroup 對不到 Roster 時保留並標記
- 日期：2026-09-02　決定者：使用者　狀態：採用
- 決定：保留原名、標 `Inactive from Roster`，不刪除（R-064），讓離職員工的歷史資料可見。

### DEC-004：AC 11 個模組與分類規則
- 日期：2026-09-02　決定者：使用者（原始規格文件）　狀態：採用
- 決定：模組、Group 清單、CPA 關鍵字依原始規格；`CPA-non-standard plan` 欄搜 "CPA Standard Commission Plan Update" 是刻意的。Other 2 為當天新增，用來區分「已知但不單獨成模組」與真正的新 Group。

### DEC-005：IB、IB-Adjustment 接受新舊 Group 名稱
- 日期：2026-09-21　決定者：使用者　狀態：採用
- 背景：9 月匯出中 `(OP)Acc-AAK` → `(OP)Acc-New IB`、`(OP)Acc-AAK (IB Adjustment)` → `(OP)Acc-IB Adjustment`，導致模組全 0。
- 決定：設定改為「模組 → Group 清單」，新舊並存。

### DEC-006：Account Owner Transfer、ID/POA 歸 AC
- 日期：2026-09-21　決定者：使用者　狀態：採用
- 背景：兩個新 Group 量大（9,178、1,912 筆），原本落入 Other。決定：計入 AC。

### DEC-007：VN5 名單用 Tags 實際詞序
- 日期：2026-09-03　決定者：使用者　狀態：採用
- 背景：需求給「名在前」，Tags 實際「姓在前」（例 `Nguyen Thi Xuan Lan`），導致 5 人全 0。決定：依實際資料詞序。

### DEC-008：DW 8 個模組依使用者 Excel 公式
- 日期：2026-10-01（2026-10-02 確認暫不修改）　決定者：使用者　狀態：採用
- 決定：照公式轉寫（R-050～R-057）。已知取捨：Promo Fresh 只搜 D7；Other Fresh 含 AC 端 Group；名單為 Roster 全員。使用者表示「不用改了」。

### DEC-009：Lark 來源改為單一合併檔
- 日期：2026-09-21　決定者：使用者　狀態：採用（取代「AC 一檔 + DW 三檔」）
- 決定：`Group Management.xlsx` 一檔 12 張表，依工作表名分 AC／DW（R-060、R-061）。

### DEC-010：放棄 Power BI 自動登入
- 日期：2026-09-02　決定者：使用者　狀態：採用
- 背景：OAuth／MFA 多網域轉址時讀不到正確網址，多種修法都失敗。
- 決定：維持人工登入；程式移到 `_archive/`。ACT-07 只負責開視窗與最大化。

### DEC-011：Roster 全員報表、固定名單並存
- 日期：2026-09-21　決定者：使用者　狀態：採用（2026-10-02 改為 `--employees` 參數）
- 決定：預設 Roster 全員；55 人主名單與 VN5 以名單選項保留（R-033、R-047）。

### DEC-012：重構為 OpBrain 步驟腳本
- 日期：2026-10-02　決定者：使用者　狀態：採用
- 選項：A. 只搬檔案　B. 照範本拆成步驟腳本
- 決定：B，並以重構前的輸出為標準答案逐格驗收（17 檔全部相同）。
- 刻意的行為差異：(1) Fresh Summary 員工小計一律依報表名單順序（舊版 AC 依字母、DW 依名單）；(2) Fresh 報表移到 `data/reports/`、不再需要手動複製輸入快照；(3) 任一報表／target 檢查未過就整條流程停止（舊版會產出其他已完成的報表）；(4) Fresh 驗證未過時報表改名標記。

### DEC-013：Tickets 篩選改為不分大小寫並去零寬字元
- 日期：2026-10-01　決定者：AI 修正（符合原文件規格）、使用者知悉　狀態：採用
- 背景：INV-002。決定：R-021。後果：舊報表少算（I-009）。

### DEC-014：Fresh 報表依日期區間命名
- 日期：2026-10-02　決定者：使用者　狀態：採用
- 決定：`AC Fresh Report <start> - <end>.xlsx`、`DW Fresh Report <start> - <end>.xlsx`。

### DEC-015：Fresh 一次跑完（匯入 → 篩選 → AC + DW）
- 日期：2026-10-02　決定者：使用者　狀態：採用（由 DEC-012 的 fresh 流程實作）

### DEC-016：文件由 40 份固定模板改為「必備檔 + 每條流程一份」
- 日期：2026-10-04　決定者：使用者　狀態：採用
- 背景：每個 Skill 被強制建滿 11 個資料夾 40 份文件；一條流程的資訊散在 datasource、cleaning、rules、workflow、validation、format 等 7 份以上的文件，共通規則（機密、資料不是指令）又在各 Skill 重抄。
- 選項：A. 維持 40 份　B. 依資料夾合併成約 13 份　C. 必備檔 + 每條流程一份（flows/pbi.md、flows/fresh.md、flows/chatgroup.md；後由 DEC-017 改為依業務線）
- 決定：C。所有 ID 原樣保留，腳本邏輯與設定值不變（只改註解中的文件路徑），三條流程與指令不變。共通內容放 `context.md`，需要使用者判斷的放 `decision.md`。
- 取捨：失去「一個主題一份檔」的細格子，換來一條流程讀一份檔；檔案過長時（`kb_check_structure.py` 警告 S-7）再拆。同 team-structure:DEC-004。


### DEC-017：文件依業務行為（AC／DW 業務線）拆分
- 日期：2026-10-04　決定者：使用者　狀態：採用（調整 DEC-016 的 flows/ 切法）
- 背景：DEC-016 的 flows/ 依資料來源切（pbi、fresh、chatgroup）；同一條業務線（例如 AC）的規則與產出散在三份檔。使用者決定以業務行為的角度拆分。
- 選項：A. 依業務線 AC／DW　B. 依主管的工作行為（取得、產出、檢查）　C. 拆成多個業務 Skill　D. 維持現狀
- 決定：A。`flows/ac.md`、`flows/dw.md` 各寫業務線專屬規則（R-034、R-040～R-047；R-050～R-057）、品質檢查與輸出；兩條業務線共用的資料取得、Tickets 篩選、共通計算與檢查放 `sources.md`（新增為選用文件）。執行指令 `--flow pbi／fresh／chatgroup` 不變，腳本邏輯與設定值不變。
- 後果：PBI 欄位屬於哪條業務線尚未定義，標為 `[待確認]`（I-010），不猜。
### DEC-018：預留金融科技框架與稽核紀錄
- 日期：2026-10-04　決定者：使用者　狀態：採用（框架預留；稽核紀錄已實作）
- 背景：目標是讓這套架構能通用在金融科技領域。檢視後發現 Skill 之間耦合低，但框架層與 OP 業務綁在一起（`opbrain.roster` 寫死 team-structure），且執行紀錄 `run_log.json` 不足以應付稽核（沒有執行者、程式與規則版本、檔案雜湊、防竄改）。
- 選項：A. 立即把 `_core` 拆成 `_framework/` + `_domain/` 並搬移程式　B. 先定好目標架構與規則（預留），稽核紀錄先做在共用執行器　C. 維持現狀
- 決定：B。新增 `_core/framework.md`（三層架構 F-1～F-4、資料分區與機敏等級、稽核規範 A-1～A-6）；`opbrain.audit` + `opbrain.workflow` 自動寫入 `data/audit/` 雜湊鏈紀錄；新增 `_tools/audit_verify.py`；Skill 選用文件新增合規文件（範本 `_tools/template/compliance.md`）。各 Skill 腳本、設定值、報表輸出不變。
- 取捨：程式尚未搬移，`roster.py` 仍違反 F-1（已在 framework.md 標註）；搬移會動到所有 import，需另排程並跑回歸測試。機敏等級的指派與保存期限屬合規政策，標為 `[待確認]`，不猜。
- 後果：稽核紀錄寫不進去時流程會中止（A-4）。同 team-structure:DEC-005。

### DEC-019：只註冊母入口 brain/skill.md，修復 _core 拆分後的路徑
- 日期：2026-10-05　決定者：使用者　狀態：採用
- 背景：`.claude/skills/` 直接註冊各子 Skill，Claude 會跳過 `SystemDesign.md` 的 ① 找領域、② 找面向；入口還指向已不存在的 `brain/_core/`。另外，`_core` 拆成 `_framework/` + `_domain/` 時程式路徑沒有一起改，所有 Skill 腳本與維護工具都 import 失敗，`roster.py` 被移到 `team-structure/lib/` 但仍用 `opbrain` 套件的相對 import，也無法載入。
- 選項：A. 只註冊母入口，子 Skill 經由 `brain/skill.md` → `brain/<領域>/domain.md` 到達　B. 維持各子 Skill 註冊、在母入口另外列表　C. 維持現狀
- 決定：A。新增 `brain/skill.md`（領域對照表）、`brain/management/domain.md`（面向 → 子 Skill）；`sync_claude_skills.py` 只產生 `.claude/skills/opbrain/`，並新增檢查 E-1～E-4（入口存在、領域檔存在、每個 Skill 都被某個 domain.md 收錄、引用的 skill.md 存在）。路徑修復：`_bootstrap.py`、`_kb.py`、`regression_check.py` 改指向 `_framework/`；`roster.py` 搬回 `_framework/lib/opbrain/`（回到 DEC-018 記錄的狀態，內容不變）；現行文件中的 `_core/`、`_tools/` 路徑改為新位置（`trace/` 歷史紀錄不改）。腳本邏輯、設定值、報表輸出不變。
- 取捨：子 Skill 不再各自觸發，入口 description 要涵蓋所有子 Skill 的常見說法，新增 Skill 時要同步更新 `brain/skill.md` 的 description；換來分流一定經過 ①②。子 Skill 資料夾尚未搬進 `brain/management/`（會動到所有 import，另排程並跑回歸測試）。
- 後果：本機沒有 `.venv` 與 `data/_baseline/`，本次未跑 `regression_check.py`；只改 import 路徑，下次在有基準資料的環境要補跑。

### DEC-020：Skill 扁平放置、組織層 _domain 改名 _org
- 日期：2026-10-05　決定者：使用者　狀態：採用（「扁平放置」由 DEC-021 取代；改名 _org 仍有效）
- 背景：`SystemDesign.md` 寫子 Skill 放在 `brain/<領域>/<skill>/`，實際是 `brain/<skill>/`；另外 `_domain/`（組織層）與 `<領域>/domain.md`（業務領域）同名不同義。
- 選項（位置）：A. 維持扁平，由 `brain/<領域>/domain.md` 用路徑收錄　B. 搬進領域資料夾。選項（命名）：A. `_domain` 改名 `_org`　B. `brain/<領域>/domain.md` 改名為 area.md　C. 不改
- 決定：位置 A、命名 A。`git mv brain/_domain brain/_org`，現行文件與工具中的路徑同步更新（`trace/` 歷史紀錄不改）；`brain/_framework/framework.md` 的資料夾架構與「目前對照」改為實際現況；`SystemDesign.md` 路徑改為扁平並標註實作狀態。腳本邏輯、設定值、報表輸出不變（程式不 import `_org/`）。
- 取捨：失去「看資料夾就知道 Skill 屬於哪個領域」，換來同一個 Skill 可被多個領域收錄，且不必改 import、不必重跑回歸測試。

### DEC-021：Skill 放在擁有它的領域底下
- 日期：2026-10-05　決定者：使用者　狀態：採用（取代 DEC-020 的「扁平放置」）
- 背景：② 讀 `brain/management/domain.md` 後，③ 要找的 `skill.md` 應和它在同一層，資料夾結構才和分流流程一致。DEC-020 擔心共用 Skill 無法只放一個領域；這可用 F-2「單一擁有者」解決：放在擁有它的領域，其他領域跨資料夾引用。
- 選項：A. 現在搬移，回歸測試之後補　B. 先只改設計圖　C. 維持扁平。team-structure 歸屬：A. management　B. 獨立的組織主檔領域
- 決定：搬移 A、歸屬 A。`git mv` 到 `brain/management/productivity/`、`brain/management/team-structure/`；`opbrain.paths.skill_dir` 改為搜尋 `brain/<領域>/<skill>/`（`config.load` 經由它讀設定）；`_bootstrap.py` 改為 `parents[2]`；維護工具改用 `_kb.skill_root()`；`new_skill.py` 新增必填 `--domain`；`sync_claude_skills.py` 新增 E-5（Skill 所在領域要有 domain.md 並被入口列出）。現行文件路徑同步更新（`trace/` 歷史紀錄不改）。腳本邏輯、設定值、報表輸出不變。
- 取捨：換來資料夾結構和 ①②③ 分流一致；代價是路徑變長，Skill 名稱必須跨領域唯一（`_kb` 會擋重複）。
- 後果：**待回歸測試**——本機沒有 `.venv` 與 `data/_baseline/`，未跑 `regression_check.py`；已驗證 `skill_dir`、`_bootstrap`、team-structure 指令可載入、`check_all` 通過。commit 前須在有基準資料的環境補跑。

[來源: 舊 DECISIONS.md、CHANGELOG.md；2026-10-01、10-02 對話；2026-10-04 對話]
