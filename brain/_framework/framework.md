# 金融科技框架（資料夾架構 + 稽核紀錄）

> 目標：這套架構能直接用在金融科技團隊（受稽核、處理個資與交易資料）。
> 這份文件定義**資料夾架構**與**稽核紀錄規範**。標為「預留」的部分已定好規則、尚未實作；
> 標為 `[待確認]` 的是合規政策，由使用者（或公司法遵）決定，AI 不得自行填值。

---

## 一、資料夾架構

### 1. 程式與文件：三層，依賴只能往下

```
brain/
├── skill.md            入口：① 領域對照表（唯一註冊到 .claude/skills/ 的入口）
├── _framework/         第 1 層 框架：任何團隊都能直接搬走（不含任何業務名詞）
├── _org/               第 2 層 組織：這個組織專屬的名詞、資料配置、共用主檔介面
└── <領域>/
    ├── domain.md       分流：② 面向 → 子 Skill 對照表
    └── <skill>/        第 3 層 業務：一個業務主題一個 Skill，放在擁有它的領域底下
```

- 「領域」是分流用的目錄，不是一層程式（依賴方向不變）：Skill 放在**擁有它的領域**底下（`brain/<領域>/<skill>/`），和該領域的 `domain.md` 同一層；其他領域需要時，在自己的 `domain.md` 用路徑跨資料夾引用（例如未來的財務領域引用 `brain/management/team-structure/skill.md`）。同一個 Skill 只有一個擁有領域，對應 F-2。
- 「組織」（`_org/`）是這個組織共用的名詞與資料配置，和業務領域無關。
- 分流流程與檢查（E-1～E-4）見專案根目錄 `SystemDesign.md`。

| 規則 | 說明 |
|---|---|
| F-1 依賴方向 | Skill → 組織 → 框架。框架不得 import、讀取或寫死任何 Skill 名稱與業務欄位 |
| F-2 主檔單一擁有者 | 每份主檔（Roster、客戶、帳戶…）只有一個 Skill 能寫；其他 Skill 只能透過介面讀 |
| F-3 合規文件 | 處理個資或受監管資料的 Skill，必須有 `compliance.md`（範本：`_framework/tools/template/compliance.md`） |
| F-4 稽核 | 所有流程經 `opbrain.workflow` 執行，自動寫稽核紀錄（見第二節）；不得另寫繞過執行器的流程 |

**目前對照（2026-10-05）：**

| 位置 | 內容 | 狀態 |
|---|---|---|
| `_framework/lib/opbrain/` | `common`、`config`、`env`、`paths`、`workflow`、`audit` | 已搬移，符合 F-1 |
| `_framework/tools/` | 檢查、建立新 Skill、產生入口、回歸比對、稽核驗證 | 已搬移，符合 F-1 |
| `_org/` | `conventions.md`、`glossary.md`、`data-layout.md` | 已搬移 |
| `_framework/lib/opbrain/roster.py` | 讀 Roster（實作 team-structure 的規則） | **不符合 F-1**（框架層寫死 team-structure 與 OP 欄位）；目標位置是 `_org/` 或 team-structure |

`roster.py` 搬移會動到所有讀 Roster 的腳本 import，必須另外排程，並以 `regression_check.py` 確認結果不變。

### 2. 資料：依用途分區、依機敏等級管理

| 分區 | 路徑 | 用途 | 可刪改？ | 機敏等級 | 保存期限 |
|---|---|---|---|---|---|
| 原始 | `data/raw/` | 取得時的原樣 | 不可改；可依期限刪 | `[待確認]` | `[待確認]` |
| 產出 | `data/COMBINE/`、`data/reports/` | 可重算的成品 | 可重算 | `[待確認]` | `[待確認]` |
| 暫存 | `data/work/` | 每次執行的中間檔 | 可刪 | `[待確認]` | `[待確認]` |
| 知識 | `data/knowledge/` | 主管紀錄 | 只增修，不刪 | `[待確認]` | `[待確認]` |
| 基準 | `data/_baseline/` | 回歸測試標準答案 | 僅經確認更新 | `[待確認]` | `[待確認]` |
| **稽核** | `data/audit/` | 稽核紀錄 | **只能附加，不可刪改** | 內部 | `[待確認]` |

**機敏等級（框架預設，可由法遵調整）：**

| 等級 | 定義 | 例子 |
|---|---|---|
| L1 公開 | 可對外 | 產品說明 |
| L2 內部 | 公司內可看 | 流程文件、彙總統計 |
| L3 機密 | 限相關主管 | 員工工作量、個人績效 |
| L4 高度機密 | 限指定人員、需遮罩或加密 | 身分證號、帳號、交易明細 |

所有 `data/` 永不入版控（`.gitignore`）。L4 資料進入本專案前，必須先在該 Skill 的 `compliance.md` 寫明遮罩方式。

---

## 二、稽核紀錄

### 1. 原則
| 規則 | 說明 |
|---|---|
| A-1 自動 | 由 `opbrain.workflow` 寫入，Skill 腳本不必（也不應）自己寫 |
| A-2 只能附加 | 檔案只附加新行；任何修改、刪除、插入都會讓雜湊鏈斷掉 |
| A-3 不記資料內容 | 只記誰、何時、哪版程式與設定、檔案雜湊值、結果；**不記姓名、工單文字、金額等資料值** |
| A-4 寫不進就停 | 稽核紀錄寫入失敗時，流程不得繼續（例外直接中止） |
| A-5 時間一律 UTC | ISO 8601，到毫秒，例：`2026-10-04T08:15:30.123Z` |
| A-6 可驗證 | `python brain/_framework/tools/audit_verify.py` 重算整條雜湊鏈 |

### 2. 位置與格式
- `data/audit/audit-YYYY-MM.jsonl`（UTC 月份），一行一筆 JSON（鍵排序、無空白）
- 每次流程執行寫入：`flow_start` → 每個步驟一筆 `step_end` → `flow_end`，以 `run_id` 串起來
- `run_id` 也寫進該次工作目錄的 `run_log.json`，兩邊可以對照

### 3. 欄位

| 欄位 | 事件 | 說明 |
|---|---|---|
| `schema` | 全部 | 格式版本（目前 1）；欄位變動時遞增 |
| `ts` | 全部 | UTC 時間 |
| `event` | 全部 | `flow_start`／`step_end`／`flow_end` |
| `run_id` | 全部 | 本次執行的 UUID |
| `skill`、`flow` | 全部 | 哪個 Skill 的哪條流程 |
| `actor` | flow_start | `os_user`（作業系統帳號）、`git_email` |
| `host`、`python` | flow_start | 執行的主機、Python 版本 |
| `code` | flow_start | `git_commit`；`dirty`＝程式有未提交的修改（結果可能無法重現） |
| `config_digest` | flow_start | 所有 `brain/*/config/*.yaml` 的 SHA-256：證明當下用的是哪一版規則 |
| `argv`、`planned_steps`、`workdir` | flow_start | 指令參數、預計步驟、工作目錄 |
| `regression` | flow_start | 是否為回歸測試執行 |
| `act`、`script`、`args` | step_end | 步驟 ID、腳本、參數 |
| `status`、`exit_code`、`attempts`、`seconds` | step_end、flow_end | 結果（ok／error／gate_blocked／stopped） |
| `artifacts` | step_end | 本步驟在工作目錄新增或變更的檔案 → SHA-256 |
| `skipped_steps` | flow_end | 因失敗或停止而沒執行的步驟 |
| `prev_hash`、`hash` | 全部 | 雜湊鏈：`hash` = SHA-256（除 `hash` 外的整筆內容，含 `prev_hash`） |

### 4. 預留的擴充（尚未實作）
- **原始輸入檔雜湊**：目前只記工作目錄內的檔案；`data/raw/` 的輸入檔與 `COMBINE/`、`reports/` 的最終產出，日後可由步驟腳本呼叫 `audit.file_digest()` 寫入
- **集中保存**：本機檔案可被有權限的人整檔刪除；正式上線時應同步到唯寫（WORM）儲存或公司 SIEM
- **同時執行**：兩條流程同一時間寫入可能讓鏈分岔（`audit_verify.py` 會報錯）；需要時再加檔案鎖
- 保存期限 `[待確認]`
