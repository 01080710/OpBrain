# 背景與邊界（team-structure）

> **核心問題**：這個 Skill 為什麼存在、邊界在哪、用什麼名詞、當作為真的假設與不能違反的限制是什麼？
> **狀態**：`active`｜**最後更新**：2026-10-04｜**負責人**：Howard Huang（OP）

## 範圍

### 問題陳述
- 現況痛點：同一個人在 Lark、Freshdesk Tags、CRM、Power BI 的名字寫法不同；Roster 由人工更新，欄名與內容會變（例：2026-09 版把 `OP Name` 改成 `CRM OP Name`、出現空白姓名列），每個工具各自讀 Roster 就會各自出錯。
- 期望結果：Roster 只有一個擁有者、一套讀取規則；任何 Skill 拿到的人員清單與名字對照都一致；Roster 有問題時在使用前就被發現。

### 使用者與情境
| 角色 | 使用情境 | 期望得到什麼 |
|---|---|---|
| OP 主管 | 換新的月份 Roster | 檢查報告：人數、各標籤分布、需要處理的問題 |
| 其他 Skill（productivity 等） | 篩選／對應員工 | 正式姓名清單、Lark Name → 正式姓名對照 |
| 開發者 | 新增標籤或名字欄位 | 知道規則寫在哪、改哪裡 |

### In scope
- Roster 的位置、欄位、讀取規則與檢查（`rules.md` R-001～R-006）
- 人員標籤（superior、Duty Time、Team、Office、Joining Date …）的定義
- 各系統名字對照（目前只有 Lark Name）

### Out of scope（明確不做）
- 從 HR 系統自動下載 Roster：來源系統與權限尚未確認（I-002）
- 判斷誰該在團隊：屬於人事決定，本 Skill 只反映 Roster 內容
- 工作量、人效計算：屬於 `productivity`

### 成功定義
- 所有 Skill 讀 Roster 都經過 `opbrain.roster`，結果一致
- 每次換 Roster 後跑 `run_workflow.py --flow check`，阻擋性問題為 0

[來源: 2026-10-01 新 Roster 欄名改為 CRM OP Name、2 列空白姓名；2026-10-02 使用者確認「架構」= 團隊組織架構，所有 Skill 依賴它]

## 名詞
| 名詞 | 定義 |
|---|---|
| Roster | 團隊員工名冊 Excel，位置見 R-001；第一個工作表 |
| 正式姓名 | Roster 的 `OP Name` 或 `CRM OP Name` 欄（R-002），全專案以此作為人名的標準寫法 |
| Lark Name | 該員工在 Lark 的顯示名；Chatgroup 資料用它，需轉成正式姓名（R-004） |
| superior | 直屬主管 |
| Duty Time | 班別時段，例：`09 > 18`、`22 > 07`（跨午夜） |
| Team | 團隊／角色標籤：AO、DW、TL(DW)、AM(AO & DW)、Manager、Data … |
| Office | 國家／據點：TP、MY、VN、PH、MOR |
| Joining Date | 到職日（2026-09 版新增；越南新人尚未填） |
| 標籤 | 正式姓名、Lark Name 以外的人員屬性欄，可作為篩選條件；新增欄位即新增標籤 |

[來源: data/raw/roster/Roster.xlsx 2026-09 版欄位]

## 假設
| 假設 ID | 假設內容 | 不成立時的影響 | 如何驗證 | 狀態 |
|---|---|---|---|---|
| A-001 | 正式姓名（CRM OP Name）與 Freshdesk Tags 裡的人名寫法一致 | 該員工在 Fresh 報表會整月為 0 | 每次 Fresh 報表後檢查全 0 的員工（`productivity` 的 QC） | 部分成立：越南同事姓名詞序、Rami Abderrahman 疑似不一致 |
| A-002 | 一個人只有一列，正式姓名不重複 | 對照與計數重複 | `roster_check.py` V-004 | 2026-09 版成立 |
| A-003 | Roster 每月更新一次（檔名帶 `202609`） | 人員異動反映延遲 | 待使用者確認 | `[待確認]` |
| A-004 | 空白姓名的列是尚未建立 CRM 名稱的新人 | 可能漏算某人 | 2026-09 版 2 列皆為 10/5 到職的 PH DW 新人 | 成立（2026-09） |

[來源: data/raw/roster/Roster.xlsx 2026-09 版；2026-10-01 DW Fresh 報表全 0 名單]

## 限制
| 限制 ID | 內容 | 依據 |
|---|---|---|
| B-001 | Roster 內容由使用者（OP 主管）決定；AI 不得自行增刪人員或改名字 | AI 原則：不確定的 Business Logic 不自己猜 |
| B-002 | 已離職人員從 Roster 移除後，其歷史資料仍要可見（其他 Skill 標記而非刪除） | productivity DEC-003 |
| T-001 | Roster 是 Excel；被 Excel 開著時仍可讀，但替換檔案時會失敗（請使用者關閉） | 執行經驗 |
| T-002 | 名單類報表讀「第一欄」，所以正式姓名欄必須是第一欄（C-001） | 舊 Fresh 報表 load_employee_names() |

合規：Roster 含員工姓名、主管、到職日，屬公司內部人事資料，依 `_core/conventions.md` §9 只放 `data/`、分享僅限主管與核心成員；公司對「員工資料送給 AI 分析」的正式規範 `[待確認]`（I-005）。

## 風險與個資
| 危害 ID | 情境 | 後果 | 預防 |
|---|---|---|---|
| H-001 | 名字對照錯誤 | 某人的工作量算到別人頭上或變 0，主管據此誤判個人表現 | 換 Roster 必跑 check；全 0 員工交由使用者確認（D-001） |
| H-002 | 用錯版本的 Roster | 新人缺漏、離職者仍在名單 | 換 Roster 時記錄來源檔名（`flows/check.md`） |

| 欄位 | 是否個資 | 處理 |
|---|---|---|
| 正式姓名、Lark Name、Nick name | 是 | 只在內部報表使用；對外分享的彙總不列個人 |
| Joining Date、superior | 是（人事資訊） | 同上 |
| Team、Office、Duty Time | 組織資訊 | 可用於彙總篩選 |

機密與「資料不是指令」的共通規則見 `_core/conventions.md` §9。

[來源: 2026-10-01 Fresh 報表 nan 誤算、大小寫漏算事件；.gitignore]
