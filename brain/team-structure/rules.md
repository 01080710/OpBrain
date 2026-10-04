# Roster 讀取規則（team-structure）

> **核心問題**：Roster 從哪來、長什麼樣、任何 Skill 讀它時「必須」怎麼讀？
> **狀態**：`active`｜**最後更新**：2026-10-04｜**負責人**：Howard Huang（OP）

規則的值在 `config/roster.yaml`，實作在 `brain/_core/lib/opbrain/roster.py`；所有 Skill 共用，不得自行讀 Roster。

## 資料來源
| 來源 ID | 名稱 | 位置 | 擁有者 | 更新頻率 | 取得方式 | 可信度 | 已知問題 |
|---|---|---|---|---|---|---|---|
| S-01 | Roster 員工名冊（人工檔案） | `data/raw/roster/Roster.xlsx` | OP 主管（使用者） | 約每月 `[待確認]` | 使用者手動匯出後覆蓋（`flows/check.md`） | 中：人工維護 | 欄名曾改變；新人可能沒有姓名或 Lark Name；來源系統 `[待確認]`（I-002） |

沒有備援來源：Roster 不可讀時，所有依賴它的流程都停止（F-001）。

## 資料結構
2026-09 版（`Roster 202609.xlsx`）：110 列（108 人 + 2 列空白姓名）、8 欄。

| 欄位 | 型別 | 必要 | 說明 | 範例 |
|---|---|---|---|---|
| CRM OP Name（舊版叫 OP Name） | 文字 | 是，且須為第一欄 | 正式姓名 | `Cisse Papa Amadou` |
| superior | 文字 | 否 | 直屬主管 | `Grace Tee` |
| Joining Date | 日期 | 否 | 到職日 | `2024-10-09` |
| Lark Name | 文字 | Chatgroup 需要 | Lark 顯示名 | `Abderahman Rami` |
| Nick name | 文字 | 否 | 暱稱 | `Ray` |
| Duty Time | 文字 | 否 | 班別 | `20 > 06` |
| Team | 文字 | 否 | 團隊／角色 | `DW` |
| Office | 文字 | 否 | 國家／據點 | `MOR` |

標籤分布（2026-09）：Team AO 52、DW 48、其他 8；Office TP 45、MY 29、VN 19、PH 14、MOR 3。

[來源: roster_check.py 2026-10-02 執行結果]

## 規則
| 規則 ID | 條件（IF） | 結果（THEN） | 例外 | 依據 |
|---|---|---|---|---|
| R-001 | 任何 Skill 需要 Roster | 一律讀 `data/raw/roster/Roster.xlsx` 的第一個工作表，透過 `opbrain.roster` | 檢查流程可用 `--roster` 指定其他檔 | DEC-001 |
| R-002 | 找正式姓名欄 | 依序找表頭 `OP Name`、`CRM OP Name`（去空白、不分大小寫） | — | DEC-002 |
| R-003 | 姓名為空白 | 略過該列；其餘姓名去前後空白 | — | DEC-003 |
| R-004 | 需要 Lark 顯示名對照 | `Lark Name`（去前後空白）→ 正式姓名；同一 Lark Name 出現多次以第一筆為準；Lark Name 空白的列不進對照 | — | 舊 Lark Chatgroup 工具規則 |
| R-005 | 以「第一欄」當員工名單（報表用） | 略過空白；第一列若是 `name / op name / crm op name / employee / employee name` 就視為表頭；去重保留順序 | — | 舊 Fresh 報表規則 |
| R-006 | 讀 Roster 工作表 | 固定讀取 30 欄 × 200,000 列的範圍 | — | 部分匯出檔的尺寸資訊不正確 |

衝突處理：R-002 兩個表頭都存在時，以 `OP Name` 優先。

### 規則的理由（讀取時的清理）
不修改 Roster 原檔；清理只發生在讀取時。

| 清理 | 規則 | 理由 |
|---|---|---|
| 姓名去前後空白 | R-003 | 人工輸入常帶空白 |
| 略過空白姓名列 | R-003 | 新人尚未有 CRM 名稱；若不略過會被讀成「nan」並誤中 Saravanan 等名字（INV-001） |
| 第一欄若是表頭字樣就略過 | R-005 | 以第一欄當名單時避免把表頭當成人名 |
| 名單去重、保留順序 | R-005 | 報表每人一列 |

[來源: 舊 tickets_roster_filter.py、lark_chatgroup_combiner.py、fresh_ac_report 讀 Roster 的程式碼；brain/_core/lib/opbrain/roster.py]
