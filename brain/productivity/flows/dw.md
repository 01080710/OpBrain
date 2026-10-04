# 業務線 DW：出入金業務的工作量（productivity）

> **核心問題**：DW 業務的工作量從哪些資料、依什麼規則算出來？產出哪些檔案？
> **狀態**：`active`｜**最後更新**：2026-10-04｜**負責人**：Howard Huang（OP）

資料的取得、Tickets 篩選、共通計算與檢查見 `sources.md`；本檔只寫 DW 專屬的部分。

## 範圍
| 資料 | DW 的部分 | 產出 |
|---|---|---|
| Freshdesk 工單（S-02） | WD／DP／FCA 這 5 個 Group 與關鍵字，共 8 個模組（R-050～R-056） | DW Fresh Report |
| Lark Group Management（S-03） | `Deposit Support`、`Withdrawal Support`、`Deposit & Withdrawal Support` 3 張工作表（R-061），OP 欄 `OP name` | DW Chatgroup Volumn |
| Power BI（S-01） | WD WL by Group，以及 P.1／P.2 哪些欄位屬於 DW `[待確認]`（I-010） | — |

## 使用者的話 → 指令
| 使用者說 | 指令參數 |
|---|---|
| 出 DW fresh 報表 9/1～9/30 / 只出 DW | `--flow fresh --start ... --end ... --reports dw` |
| 跑 DW Chatgroup Volumn | `--flow chatgroup --start ... --end ...`（AC、DW 一起產出） |

## 規則（值：`config/fresh_dw.yaml`）
| 規則 ID | 條件 | 結果 | 依據 |
|---|---|---|---|
| R-050 | Group = `(OP)Withdrawal Team` | WD fresh | DEC-008 |
| R-051 | Group ∈ `(OP)Deposit Team`、`(HA)Deposit Team`、`Settlement Team ` | DP fresh | DEC-008 |
| R-052 | Group = `(OP)FCA-Tickets` | FCA Fresh | DEC-008 |
| R-053 | Group 不在上述 5 個之內（含空白、含 AC 端 Group） | Other Fresh，並列在 Other Fresh Groups 工作表 | DEC-008 |
| R-054 | Tags 含關鍵字 | Promo Fresh（只搜 "deposit bonus issue"）、Inst -WD、Inst -DP、EXTRAOPWork | DEC-008 |
| R-055 | DW 的 Group 比對 | 不分大小寫、完全相同（同 Excel COUNTIF） | DEC-008 |
| R-056 | 欄位順序 | WD fresh、DP fresh、Promo Fresh、Other Fresh、Inst -WD、Inst -DP、FCA Fresh、EXTRAOPWork | DEC-008 |
| R-057 | 輸出 | 工作表 `fresh Template Batch (DW)`；檔名 `DW Fresh Report <start> - <end>.xlsx` | DEC-014 |

名詞：Other Fresh = Group 不在 WD／DP／FCA 這 5 個之內的工單（含 AC 端 Group）。

與 Excel 公式的對應：`=SUMPRODUCT(COUNTIF(類別, Group) * ISNUMBER(SEARCH(姓名, Tags)) * (日期=A2))` 等，詳見 DEC-008。2026-09 資料以全部原始列直接套公式重算，8 個模組總數完全一致。

## 品質檢查（DW 專屬）
- DW 報表 `Other Fresh Groups` 的分布（C-003）；出現新的 DW Group 時依 D-002 詢問。
- 已知取捨（使用者 2026-10-02 表示暫不修改，I-005）：Inst -WD、EXTRAOPWork 2026-09 整月 0；Promo 只搜 D7 不搜 D8；Other Fresh 含 AC 端 Group。

## 輸出
| 輸出 | 位置 | 檔名 | 結構 |
|---|---|---|---|
| DW Fresh 報表 | `data/reports/` | `DW Fresh Report <start> - <end>.xlsx` | 共通結構（`sources.md`）；Other 清單工作表為 `Other Fresh Groups` |
| DW Chatgroup Volumn | `data/COMBINE/` | `DW Chatgroup Volumn <start> to <end>.xlsx` | Date（yyyy/mm/dd）、OP Name、Group Name、Source、Roster Status |

## 相關決策與問題
- 決策：DEC-008（8 個模組依使用者 Excel 公式）、DEC-009（Lark 單一合併檔）、DEC-014（報表命名）
- 問題：I-005（DW 已知取捨）

[來源: 使用者 2026-10-01 DW Excel 公式；舊 generate_dw_report.py；config/fresh_dw.yaml]
