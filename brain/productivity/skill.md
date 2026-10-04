---
name: productivity
description: 人效（Productivity）— 取得、整理、計算 OP 團隊的工作量資料。三條流程：pbi（下載＋合併 Power BI 的 OP Workload P.1、P.2、WD WL by Group）、fresh（Freshdesk 工單依 Roster 篩選後產出 AC／DW Fresh 模組報表）、chatgroup（Lark Group Management 匯出 → AC／DW Chatgroup Volumn）。使用者說「下載 PBI 9/1～9/6」「補跑 PBI」「強制重跑」「Combine P1」「開 PBI 登入頁」「出 AC 跟 DW fresh 報表」「跑桌面這份 Tickets_Export 資料夾」「彙總下載資料」「跑 Lark Chatgroup Volumn 9/1～9/30」時使用。
version: 1.2.0
status: active
depends_on: [team-structure]
provides: [pbi_combine_files, tickets_roster_tagged, fresh_ac_report, fresh_dw_report, chatgroup_volumn_files]
---

# 人效（productivity）

> **核心問題**：這個 Skill 是什麼、何時該用、第一步該讀哪裡？
> **狀態**：`active`｜**最後更新**：2026-10-04｜**負責人**：Howard Huang（OP）

## 一句話定位
productivity 讓 OP 主管用一句話完成「取得各系統工作量資料 → 依 Roster 對應到人 → 產出可直接使用的合併檔與模組報表」，作為人效分析（未來的 Productivity Point 計分）的資料基礎。

## 何時使用 / 何時不使用
- 使用：下載／合併 PBI 報表、產出 AC／DW Fresh 報表、產出 AC／DW Chatgroup Volumn、開 PBI 登入頁
- 不使用：Roster 本身的問題（→ `team-structure`）；排班、加班、QC（→ 各自的 Skill，尚未建立）；Productivity Point 計分（積分總表尚未交付，I-001）

## 使用者的話 → 指令
所有指令從專案根目錄執行：`.venv\Scripts\python.exe brain/productivity/scripts/run_workflow.py ...`。
日期一律 `YYYY-MM-DD`、含頭尾；使用者只說月日時年份用今年。

| 使用者說 | 指令參數 | 詳見 |
|---|---|---|
| 開 PBI 登入頁 / 幫我跳出登入頁 | `--flow open-browser` | `sources.md` A |
| 下載 PBI 9/21～9/30（三份） / 下載＋Combine | `--flow pbi --start 2026-09-21 --end 2026-09-30` | `sources.md` A |
| 下載 OP Workload P.1 8/1～8/7 | `--flow pbi ... --reports op_workload_p1` | `sources.md` A |
| 補跑 PBI | 同上（已存在的檔自動跳過） | `sources.md` A |
| 強制重跑 / 全部重新下載 | 加 `--force` | `sources.md` A |
| Combine PBI 9/1～9/20 / Combine P1、P2、WD | `--flow pbi --no-download ...`（`--reports op_workload_p1 / op_workload_p2 / wd_wl_by_group`） | `sources.md` A |
| 出 AC 跟 DW fresh 報表 9/1～9/30，用桌面這份資料夾和新 Roster | `--flow fresh --start ... --end ... --source-folder "<資料夾>" --roster "<Roster>"` | `flows/ac.md`、`flows/dw.md` |
| 只出 DW | 加 `--reports dw` | `flows/dw.md` |
| 55 人主報表 / VN5 | `--flow fresh --reports ac --employees main55`（或 `vn5`） | `flows/ac.md` |
| 彙總下載資料（只要篩選結果） | 跑 fresh 後取 `data/COMBINE/Tickets Roster Tagged*.csv` | `sources.md` B |
| 跑 Lark Chatgroup Volumn 9/1～9/30 | `--flow chatgroup --start ... --end ...`；新的 Group Management 先覆蓋到 `data/raw/lark_chatgroup/` | `sources.md` C |

## 業務線與流程
文件依業務行為拆分：AC（帳戶業務）、DW（出入金業務）各一份；兩條業務線共用的資料取得在 `sources.md`。執行指令仍依資料來源分成以下流程，指令不變。

| 流程 | 步驟 | 進入條件 | 產出給 | 文件 |
|---|---|---|---|---|
| pbi | ACT-01（`--no-download` 時略過）→ 02 → 03 → 04 → 05 → 06 | 已登入 Edge（只有下載需要） | 業務線對應 `[待確認]`（I-010） | `sources.md` A |
| open-browser | ACT-07 | `.env` 有 PBI_REPORT_URL | — | `sources.md` A |
| fresh | ACT-10 → 11 → 12 → 每條業務線（ac、dw）各跑 13 → 14 → 15 | Tickets 與 Roster 可用 | AC、DW Fresh 報表 | `sources.md` B、`flows/ac.md`、`flows/dw.md` |
| chatgroup | ACT-20 → 21 → 22 → 23 → 24 | 來源檔與 Roster 可用 | AC、DW Chatgroup Volumn | `sources.md` C、`flows/ac.md`、`flows/dw.md` |

共通執行方式（`opbrain.workflow`）：
- 任一步非 0 結束，後續步驟一律不執行；重跑同一指令即可（已成功的下載自動跳過）。
- 每次執行的中間檔與 `run_log.json`（ok／error／gate_blocked／stopped／skipped）放在 `data/work/productivity/<flow>/<時間>/`。
- 緊急停止：在該次工作目錄放 `STOP` 檔，下一步開始前停止（結束碼 3）。
- 觸發：使用者一句話 → AI 執行 `run_workflow.py`；同事可不帶參數執行進入互動模式。目前沒有排程。
- 結束碼：0 成功｜1 輸入錯誤｜2 被關卡擋下｜3 被緊急停止。

回報原則：先講結論（成功／停在哪一步）；失敗時說明缺什麼、使用者要做什麼；openpyxl 的樣式 UserWarning 是雜訊，不回報。各流程的回報內容見 `sources.md` 的步驟。

## 文件地圖
| 文件 | 回答的問題 |
|---|---|
| `context.md` | 為什麼存在、邊界、名詞、假設、共通限制與風險、驗收與回歸測試 |
| `decision.md` | 哪些情況要使用者決定、怎麼升級；主管判讀 |
| `sources.md` | AC、DW 共用：A. Power BI、B. Freshdesk 工單、C. Lark Chatgroup 的取得、清理、共通計算與檢查 |
| `flows/ac.md` | 業務線 AC：11 個模組規則、AC 報表與 Chatgroup 輸出 |
| `flows/dw.md` | 業務線 DW：8 個模組規則、DW 報表與 Chatgroup 輸出 |
| `trace/decisions.md` | 做過的決策與理由（DEC） |
| `trace/issues.md` | 未解問題、調查、經驗 |
| `trace/changes.md` | 版本變更紀錄 |

## 與其他 Skill 的關係
- 依賴 `team-structure`：所有 Roster 讀取經 `opbrain.roster`（team-structure:R-001）
- 未來排班、QC 等 Skill 會讀本 Skill 的輸出（`flows/ac.md`、`flows/dw.md` 與 `sources.md` 的「輸出」）做交叉分析

## 程式碼（scripts/、config/）
| 腳本 | 動作 ID | 對應文件 |
|---|---|---|
| `pbi_fetch.py` … `pbi_open_browser.py` | ACT-01～07 | `sources.md` A |
| `tickets_*.py`、`fresh_*.py` | ACT-10～15 | `sources.md` B；模組規則在 `flows/ac.md`、`flows/dw.md` |
| `chatgroup_*.py` | ACT-20～24 | `sources.md` C |
| `run_workflow.py` | （總控） | 本檔「業務線與流程」 |
| `regression_check.py` | （回歸測試） | `context.md` TC-001～TC-005 |

規則的值：`config/pbi.yaml`、`tickets.yaml`、`chatgroup.yaml`（`sources.md`）、`fresh_ac.yaml`（`flows/ac.md`）、`fresh_dw.yaml`（`flows/dw.md`），每段標註 R-ID。

## 完成度總覽
| 文件 | 狀態 |
|---|---|
| `context.md` | draft |
| `decision.md` | active |
| `flows/ac.md` | active |
| `flows/dw.md` | active |
| `sources.md` | active |
| `trace/changes.md` | active |
| `trace/decisions.md` | active |
| `trace/issues.md` | active |
