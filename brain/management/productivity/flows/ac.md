# 業務線 AC：帳戶業務的工作量（productivity）

> **核心問題**：AC 業務的工作量從哪些資料、依什麼規則算出來？產出哪些檔案？
> **狀態**：`active`｜**最後更新**：2026-10-04｜**負責人**：Howard Huang（OP）

資料的取得、Tickets 篩選、共通計算與檢查見 `sources.md`；本檔只寫 AC 專屬的部分。

## 範圍
| 資料 | AC 的部分 | 產出 |
|---|---|---|
| Freshdesk 工單（S-02） | AC Group 清單與 CPA 關鍵字，共 11 個模組（R-040～R-045） | AC Fresh Report |
| Lark Group Management（S-03） | DW 3 張以外的 9 張工作表（R-061），OP 欄 `OP Name (Actual)` | AC Chatgroup Volumn |
| Power BI（S-01） | P.1／P.2 哪些欄位屬於 AC `[待確認]`（I-010） | — |

## 使用者的話 → 指令
| 使用者說 | 指令參數 |
|---|---|
| 出 AC fresh 報表 9/1～9/30 | `--flow fresh --start ... --end ... --reports ac`（不加 `--reports` 時 AC、DW 一起出） |
| 55 人主報表 / VN5 | `--flow fresh --reports ac --employees main55`（或 `vn5`） |
| 跑 AC Chatgroup Volumn | `--flow chatgroup --start ... --end ...`（AC、DW 一起產出） |

## 規則（值：`config/fresh_ac.yaml`）
| 規則 ID | 條件 | 結果 | 依據 |
|---|---|---|---|
| R-034 | AC 的 Group 比對 | 完全相同（區分大小寫與空白）；Group 空白不屬於任何 Group 模組 | 原始規格 |
| R-040 | Group 在 `ac_groups` | 計入 AC | DEC-004、DEC-006 |
| R-041 | Group 在 `group_module_map` 某模組的清單 | 計入該模組（Cpa-Ac、Cpa-Payment、IB、IB-Adjustment、FCA；新舊名稱並存） | DEC-005 |
| R-042 | Group 在 `other2_groups` | 計入 Other 2 | DEC-004 |
| R-043 | Group 非空白且不在以上任何清單 | 計入 Other，並列在 Other Groups 工作表供檢查 | DEC-004 |
| R-044 | Tags 含 CPA 關鍵字（不分大小寫子字串） | 計入對應 CPA plan 模組（不看 Group）；non-standard plan 欄搜的是 "CPA Standard Commission Plan Update"，刻意如此 | DEC-004 |
| R-045 | 欄位順序 | AC、Cpa-Ac、Cpa-Payment、IB、IB-Adjustment、FCA、Other、CPA-Multi plan、CPA-hybrid plan、CPA-non-standard plan、Other 2 | DEC-004 |
| R-046 | 輸出 | 工作表 `fresh Template Batch (AC)`；檔名 `AC Fresh Report <start> - <end>.xlsx` | DEC-014 |
| R-047 | 指定 `--employees main55 / vn5` | 改用固定名單，檔名加上名單名稱 | DEC-007、DEC-011 |

名詞：Other = 不認得的新 Group；Other 2 = 已知但不單獨成模組的 Group。

## 品質檢查（AC 專屬）
- AC 報表 `Other Groups` 工作表是否有新 Group（C-003）；有就列出 Group 與筆數，依 D-002 詢問使用者，不依名稱相似度猜。
- Group 改名的實例：`(OP)Acc-AAK` → `(OP)Acc-New IB`、`(OP)Acc-AAK (IB Adjustment)` → `(OP)Acc-IB Adjustment`（E-001、DEC-005）。

## 輸出
| 輸出 | 位置 | 檔名 | 結構 |
|---|---|---|---|
| AC Fresh 報表 | `data/reports/` | `AC Fresh Report <start> - <end>.xlsx`（固定名單加 `main55`／`vn5`） | 共通結構（`sources.md`）；Other 清單工作表為 `Other Groups` |
| AC Chatgroup Volumn | `data/COMBINE/` | `AC Chatgroup Volumn <start> to <end>.xlsx` | Date（yyyy/mm/dd）、OP Name、Group Name、Source、Roster Status |

## 相關決策與問題
- 決策：DEC-004（11 個模組）、DEC-005（IB 新舊名稱）、DEC-006（Account Owner Transfer、ID/POA 歸 AC）、DEC-007（VN5 詞序）、DEC-011（全員與固定名單並存）、DEC-014（報表命名）
- 問題：I-002（55 人名單是否完整）、I-004（Group 改名沒有自動偵測）

[來源: 舊 generate_ac_report.py；config/fresh_ac.yaml；舊 fresh-ac-report SKILL]
