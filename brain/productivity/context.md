# 背景與邊界（productivity）

> **核心問題**：這個 Skill 為什麼存在、邊界在哪、用什麼名詞、有哪些假設與共通限制、怎樣才算完成？
> **狀態**：`draft`｜**最後更新**：2026-10-04｜**負責人**：Howard Huang（OP）

共用資料來源的限制、風險與規則寫在 `sources.md`，業務線專屬的寫在 `flows/ac.md`、`flows/dw.md`；本檔只放整個 Skill 共通的內容。

## 範圍

### 問題陳述
- 現況痛點：工作量資料分散在 Power BI、Freshdesk 工單、Lark 群組三個系統，每次都要人工登入、下載、合併、對人名、算模組件數，耗時且容易出錯。
- 期望結果：一句話跑完一條流程，輸出可直接使用、且經自動驗證的檔案；數字缺漏時寧可停下來，也不產出看似完整的錯誤檔。

### 使用者與情境
| 角色 | 使用情境 | 期望得到什麼 |
|---|---|---|
| OP 主管（使用者本人） | 月底／不定期補資料 | PBI 合併檔、AC／DW Fresh 報表、Chatgroup Volumn |
| 其他主管（未來客戶） | 用 AI 問團隊工作量 | 同上，加上摘要與異常 |
| 未來的 Skill（排班、QC…） | 交叉分析 | 標準化的人 × 日 × 項目資料 |

### In scope
- 流程 pbi、fresh、chatgroup、open-browser（`skill.md` 流程一覽）
- 依 Roster 篩選、對應員工（透過 team-structure）
- AC 11 個模組、DW 8 個模組的件數計算

### Out of scope（明確不做）
- Power BI 自動登入：MFA 無法自動化，已放棄（DEC-010）
- 自動從 Freshdesk／Lark 下載：目前沒有 API 權限，使用者手動匯出 `[待確認]`
- Productivity Point 計分：積分總表尚未交付（I-001），在此之前不設計、不猜分數

### 成功定義
- 每條流程結束碼 0，且所有驗證檢查通過（C-001）
- 回歸測試 TC-001～TC-005 全部與標準答案逐格相同

[來源: 舊 PROJECT.md、CURRENT_STATUS.md；2026-10-02 重構]

## 名詞
| 名詞 | 定義 |
|---|---|
| PBI | Power BI；本 Skill 用的 3 份報表：OP Workload P.1、OP Workload P.2、WD WL by Group |
| 原始檔 | PBI 每天每份報表一個 xlsx：`data/raw/<報表>/<前綴>_YYYY-MM-DD.xlsx` |
| COMBINE / 合併檔 | 多天原始檔接成一份；也泛指 `data/COMBINE/` 的中間成品 |
| Fresh / Tickets | Freshdesk 工單匯出（`Tickets_*.csv`） |
| Tags | 工單欄位，逗號分隔，混著類別代碼與處理人姓名，例 `D1,D1. Deposit Failure,Andrew Chang` |
| Group | 工單的處理團隊欄位，例 `(OP)Deposit Team`；模組分類依據 |
| 模組 | 報表欄位，AC 11 個、DW 8 個（R-045、R-056） |
| Other / Other 2 | AC：Other = 不認得的新 Group；Other 2 = 已知但不單獨成模組的 Group |
| Other Fresh | DW：Group 不在 WD／DP／FCA 這 5 個之內的工單（含 AC 端 Group） |
| Chatgroup Volumn | Lark 群組請求量（"Volumn" 為沿用的檔名拼法） |
| Inactive from Roster | Chatgroup 中對不到 Roster 的人（通常已離職），保留不刪 |
| 關卡（gate） | 檢查沒過就停止、不往下做（結束碼 2） |

[來源: config/*.yaml、舊 TOOL_REGISTRY.md]

## 假設
| 假設 ID | 假設內容 | 不成立時的影響 | 如何驗證 | 狀態 |
|---|---|---|---|---|
| A-001 | Freshdesk Tags 裡的人名與 Roster 正式姓名寫法一致 | 該員工 Fresh 報表全 0 | 每批報表後看全 0 名單（C-004） | 部分成立（越南同事詞序、Rami Abderrahman） |
| A-002 | Tickets 的 Created Time 與業務日期同一時區 | 跨午夜班的量算到錯的日子 | 待使用者確認業務日期時區 | `[待確認]` |
| A-003 | PBI 報表的人名 = Roster 正式姓名 | PBI 無法與其他來源合併到個人 | 待比對 | `[待確認]` |
| A-004 | Chatgroup 一列 = 一筆有 OP 處理的群組請求 | 換算人效時單位錯誤 | 待使用者確認 | `[待確認]` |
| A-005 | Power BI 介面為繁體中文（按鈕名「更多選項」「匯出資料」） | 下載找不到按鈕 | 介面語言改變時 ACT-01 會失敗 | 成立 |

[來源: 舊 OPEN_QUESTIONS.md、DATA.md；2026-10-01 對話]

## 共通限制
| 限制 ID | 內容 |
|---|---|
| B-001 | 永遠不產出「看起來完整但缺資料」的檔案：缺任何一天、驗證未過，就停止或標記失敗 |
| B-002 | 業務規則（模組分類、Group 歸屬、姓名對照、計分）由使用者決定，AI 不猜 |
| B-003 | 已離職員工的歷史資料不得被刪除（Chatgroup 標記 Inactive） |
| B-004 | 已驗證的規則與程式，沒有明確指示並重新驗證，不得重新設計 |
| T-003 | Windows：檔案被 Excel 開著時無法覆寫；工具會提示關閉後重跑 |
| T-004 | Python 3、pandas、openpyxl、playwright、pyyaml、python-dotenv（`requirements.txt`） |
| L-002 | 目前只有使用者本人能登入 PBI、匯出 Freshdesk 與 Lark 資料 |

合規：工作量資料與員工姓名為公司內部資料，依 `_core/conventions.md` §9 只放 `data/`、分享僅限主管與核心成員；Power BI 報表的使用與匯出規範 `[待確認]`；員工資料送 AI 分析的公司規範 `[待確認]`（team-structure:I-005）。

[來源: 舊 AI_WORKING_RULES.md、CLAUDE.md Hard rules；2026-10-01 使用者：Lark Drive 權限只限主管與核心成員]

## 共通風險、個資與失效
| 危害 ID | 情境 | 後果 | 預防 |
|---|---|---|---|
| H-001 | 報表數字錯（漏算、誤算） | 主管誤判個人或團隊表現 | 每份輸出都驗證（`sources.md` 各段的檢查）；回歸測試；QC 檢查全 0 員工 |

| 資料 | 個資？ | 處理 |
|---|---|---|
| 員工姓名 × 工作量 | 是（績效相關） | 只在內部報表使用；對外分享用團隊彙總 |
| 工單 Requester、Subject、Description（全欄版） | 可能含客戶資料 | 只保留在 `data/COMBINE/Tickets Roster Tagged.csv`；分析與報表只用精簡版 3 欄 |
| 中間檔 `data/work/` | 是 | 可隨時刪除，不分享 |

| ID | 內容 |
|---|---|
| SEC-004 | 提交前跑 `brain/_tools/scan_secrets.py`（其他機密規則見 `_core/conventions.md` §9） |
| F-004 | 寫檔時 PermissionError（被 Excel 開著）→ 結束碼 1，提示關閉檔案後重跑 |
| F-005 | 驗證未通過 → 結束碼 2；Fresh 報表改名標記失敗；其他輸出保留供檢查，但回報時明確說不能用 |

[來源: 2026-10-01 大小寫漏算、nan 誤算事件；Tickets 全欄版欄位]

## 驗收與回歸測試
| 標準 ID | 項目 | 通過 | 警告 | 阻擋 |
|---|---|---|---|---|
| C-001 | 輸出驗證（V-002～V-005、V-020～V-026、V-031～V-034） | 全部通過 | — | 任一未通過 |

- 一次執行的驗收：流程 COMPLETE（結束碼 0）且 QC 無未處理的異常；驗收者是使用者。
- 程式或規則變更的驗收：回歸測試全部通過；`brain/_tools/check_all.py` 全部通過；使用者確認業務規則。

`python brain/productivity/scripts/regression_check.py`：用現有原始資料重跑所有流程（PBI 不下載），輸出寫到 `data/work/_regression/<時間>/`，再用 `brain/_tools/compare_outputs.py` 與 `data/_baseline/` 的標準答案逐格比對。

| 測試 ID | 內容 | 標準答案 |
|---|---|---|
| TC-001 | pbi 合併：09-21～09-30、09-01～09-20、06-01～08-31，3 份報表 | 重構前舊程式產出的 9 個檔 |
| TC-002 | chatgroup AC／DW 09-01～09-30 | 舊程式產出 |
| TC-003 | Tickets 全欄版、精簡版 | 舊程式產出（逐位元組相同） |
| TC-004 | Fresh AC、DW 09-01～09-30（Roster 全員） | 舊程式產出 |
| TC-005 | Fresh AC main55、vn5 | 舊程式產出 |

2026-10-02 結果：17 個檔案全部相同（Fresh Summary 的員工小計區塊只比內容不比順序，見 DEC-012）。
任何修改 `scripts/` 或 `config/` 後都要跑一次；規則刻意改變時，先更新標準答案並記 DEC。

[來源: brain/_core/conventions.md；2026-10-02 regression_check 執行結果]
