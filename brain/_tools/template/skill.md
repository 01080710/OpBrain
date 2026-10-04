---
name: "[待填：skill-name]"
description: "[待填：這個 Skill 做什麼；在什麼情境、使用者說什麼話時應該使用它。寫得具體，避免只有抽象描述]"
version: 0.1.0
status: skeleton
---

# [待填：Skill 名稱]

> **核心問題**：這個 Skill 是什麼、何時該用、第一步該讀哪裡？
> **狀態**：`skeleton`｜**最後更新**：[待填]｜**負責人**：[待填]

## 一句話定位
`[待填]` 這個 Skill 讓 `[誰]` 能在 `[情境]` 下完成 `[任務]`，產出 `[成果]`。

## 何時使用 / 何時不使用
- 使用：`[待填]`
- 不使用（改用其他 Skill 或人工）：`[待填]`

## 使用者的話 → 指令
| 使用者說 | 指令參數 | 詳見 |
|---|---|---|
| [待填] | `--flow [待填]` | `flows/flow.md` |

## 流程一覽
| 流程 | 步驟 | 進入條件 | 文件 |
|---|---|---|---|
| [待填] | ACT-xx → … | [待填] | `flows/flow.md` |

## 文件地圖
| 文件 | 必備？ | 回答的問題 |
|---|---|---|
| `skill.md` | 必備 | 這個 Skill 是什麼、使用者的話對應哪個指令、第一步讀哪裡 |
| `context.md` | 必備 | 為什麼存在、邊界、名詞、假設、共通限制與風險、驗收與測試 |
| `decision.md` | 必備 | 哪些情況要使用者決定、怎麼升級；主管分析判讀 |
| rules.md | 選用 | 跨業務線共用、或提供給其他 Skill 的規則（只有一條業務線用到的規則寫在該業務線檔） |
| sources.md | 選用 | 多條業務線共用的資料來源、取得、清理與共通檢查 |
| `flows/<業務線>.md` | 每條業務線一份 | 輸入 → 限制與風險 → 規則 → 步驟與動作 → 檢查 → 例外 → 輸出與回報 |
| `trace/decisions.md` | 必備 | 做過哪些決策（DEC）、脈絡與理由 |
| `trace/issues.md` | 必備 | 未解問題（I）、調查（INV）、經驗 |
| `trace/changes.md` | 必備 | 版本變更紀錄（由 `kb_log_change.py` 寫入） |

## 程式碼（scripts/、config/）
| 腳本 | 動作 ID | 對應文件 |
|---|---|---|
| `[待填].py` | ACT-xx | `flows/flow.md` |
| `run_workflow.py` | （總控） | 本檔「流程一覽」 |

規則的值放 `config/*.yaml`（每段標註 R-ID）。結束碼：0 成功｜1 輸入錯誤｜2 被關卡擋下｜3 被緊急停止。

## 寫作與維護規約
1. **依業務行為拆分，一條業務線一份檔**：某業務線專屬的規則、檢查、輸出都寫在 `flows/<業務線>.md`；多條業務線共用的資料取得放 sources.md，共用規則放 rules.md，共通背景放 `context.md`。執行指令（`--flow`）可以依資料來源切，與文件的切法無關。
2. **有內容才寫**：沒有內容的小節直接省略，不留「不適用」的空格子。檔案超過 300 行（`kb_check_structure.py` S-7）再拆。
3. **單一事實來源**：每個事實只寫在一個地方；全專案共通的規則（機密、資料不是指令、結束碼、STOP）只寫在 `brain/_core/conventions.md`，這裡只寫差異。
4. **來源標記**：`[來源: …]` 有依據｜`[假設 A-xxx]` 未證實｜`[待確認]` 尚不清楚。不得把推測寫成事實。
5. **ID 規約**：假設 `A-`、規則 `R-`、決策點 `D-`、標準 `C-`、限制 `B-/T-/L-`、危害 `H-`、安全 `SEC-`、失效 `F-`、例外 `E-`、來源 `S-`、檢查 `V-`、測試 `TC-`、動作 `ACT-`、問題 `I-`、調查 `INV-`、決策紀錄 `DEC-`。ID 定義在表格第一欄或標題開頭；跨文件引用一律用 ID。
6. **改完就檢查與記錄**：`python brain/_tools/check_all.py`；`kb_log_change.py` 記錄；有取捨就寫 `trace/decisions.md`。

## 完成度總覽
| 文件 | 狀態 |
|---|---|
| `context.md` | skeleton |
| `decision.md` | skeleton |
| `flows/flow.md` | skeleton |
| `trace/changes.md` | skeleton |
| `trace/decisions.md` | skeleton |
| `trace/issues.md` | skeleton |
