---
name: team-structure
description: 團隊架構（Team Structure）— Roster 員工名冊的唯一擁有者：誰在團隊、正式姓名、Lark 顯示名、主管、班別、團隊、國家（Office）等標籤，以及各系統名字對照。所有其他 Skill 都依賴它。使用者說「檢查 Roster」「換新的 Roster」「某人為什麼對不到」「團隊有幾個人」「各國/各團隊人數」「Roster 新增欄位/標籤」時使用。
version: 1.1.1
status: active
depends_on: []
provides: [roster_file, op_name_set, lark_to_op_map, employee_list, roster_tags]
---

# 團隊架構（team-structure）

> **核心問題**：這個 Skill 是什麼、何時該用、第一步該讀哪裡？
> **狀態**：`active`｜**最後更新**：2026-10-04｜**負責人**：Howard Huang（OP）

## 一句話定位
team-structure 讓 OP 主管與其他 Skill 能在任何分析前，取得「團隊有誰、每個人在各系統叫什麼名字、屬於哪個團隊／國家／主管」的唯一正確答案。

## 何時使用 / 何時不使用
- 使用：更換 Roster、檢查 Roster 是否有問題、查詢團隊組成、某人在其他報表對不到時查名字對照、新增或調整人員標籤
- 不使用：計算工作量或人效（→ `productivity`）；排班、加班、QC 等（→ 各自的 Skill）

## 使用者的話 → 指令
所有指令從專案根目錄執行。

| 使用者說 | 做法 |
|---|---|
| 檢查 Roster / 團隊有幾個人 / 各國、各團隊人數 | `python brain/team-structure/scripts/run_workflow.py --flow check` |
| 換新的 Roster（給了新檔） | `flows/check.md` 的「換新的 Roster」 |
| 某人為什麼對不到 | `flows/check.md` 的「查某人為什麼對不到」 |
| Roster 新增欄位／標籤、欄名改了 | `decision.md` D-002、D-003 |

## 文件地圖
| 文件 | 回答的問題 |
|---|---|
| `context.md` | 為什麼存在、邊界、名詞、假設、限制與風險 |
| `rules.md` | 讀 Roster 的規則（所有 Skill 共用，實作在 `opbrain.roster`） |
| `decision.md` | 哪些情況要使用者決定；主管判讀 |
| `flows/check.md` | 流程 check：換 Roster、檢查 Roster、查對不到的人 |
| `trace/decisions.md` | 做過的決策與理由（DEC） |
| `trace/issues.md` | 未解問題、調查、經驗 |
| `trace/changes.md` | 版本變更紀錄 |

## 與其他 Skill 的關係
- **被依賴**：所有 Skill 讀 Roster 一律透過 `opbrain.roster`（實作本 Skill 的 R-001～R-006），不得自行讀檔
- **未來**：員工主檔（含 employee_id）與 Item list（工作項目目錄）都以本 Skill 的人員為基礎（I-001、I-006）

## 程式碼（scripts/、config/）
| 腳本 | 動作 ID | 對應文件 |
|---|---|---|
| `roster_check.py` | ACT-01 | `flows/check.md` |
| `run_workflow.py` | （總控） | `flows/check.md` |

規則的值：`config/roster.yaml`（每段標註 R-ID）；共用讀取程式：`brain/_core/lib/opbrain/roster.py`。
結束碼：0 成功｜1 輸入錯誤｜2 被關卡擋下｜3 被緊急停止。

## 完成度總覽
| 文件 | 狀態 |
|---|---|
| `context.md` | active |
| `rules.md` | active |
| `decision.md` | active |
| `flows/check.md` | active |
| `trace/decisions.md` | active |
| `trace/issues.md` | active |
| `trace/changes.md` | active |
