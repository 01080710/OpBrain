---
name: opbrain
description: OP Workforce AI 的唯一入口——OP 主管問團隊營運的任何事都從這裡開始：先判斷領域，再找面向與子 Skill。涵蓋團隊架構（檢查 Roster、換新的 Roster、某人為什麼對不到、團隊有幾個人、各國/各團隊人數、Roster 新增欄位/標籤）、人效（下載 PBI 9/1～9/6、補跑 PBI、強制重跑、Combine P1、開 PBI 登入頁、出 AC 跟 DW fresh 報表、跑 Tickets_Export 資料夾、彙總下載資料、跑 Lark Chatgroup Volumn）；排班、加班、進線量、QC、團隊健康度、業務概況為規劃中，會回報尚未支援。
---

# OpBrain 母入口（brain/skill.md）

> **核心問題**：使用者的這句話屬於哪個領域？要進哪個資料夾？
> 本檔只負責 ① 找領域，不放任何業務規則或指令。設計見專案根目錄 `SystemDesign.md`。

## 怎麼走
1. **① 找領域**：依下表的「判斷依據」決定領域；一個問題可以同時命中多個領域。
2. **② 找面向**：讀命中領域的 `domain.md`，決定要用哪些子 Skill。
3. **③ 找指令**：讀子 Skill 的 `skill.md`，照「使用者的話 → 指令」執行。

- 判斷不出領域 → 問使用者，不猜。
- 領域對得到、但對應的子 Skill 還沒建立 → 回報「尚未支援」，不自己寫腳本補。
- 不可略過 ①②，直接跳進子 Skill。

## 領域對照表

| 領域 | 判斷依據（任務目的／使用者會怎麼說） | 進入 |
|---|---|---|
| management | 團隊的人、名冊、工作量、排班、加班、進線量、品質、團隊健康度、業務概況 | `brain/management/domain.md` |

新增領域：建立 `brain/<領域>/domain.md`，在上表加一列，再跑 `python brain/_framework/tools/sync_claude_skills.py`。

## 共用
- 跨 Skill 慣例（必讀）：`brain/_org/conventions.md`
- 產品與 Skill 地圖：`brain/README.md`
