# OP Workforce AI — 大腦（brain/）

這個資料夾是整個專案的「大腦」：所有業務規則、作業程序、工具程式都在這裡。
任何 AI（Claude、Cursor、Codex…）或開發者進到專案，都從這裡開始。

## 這個產品是什麼
給 OP 主管用的團隊營運 AI。主管用問的方式掌握團隊各面向（人效、排班、加班、進線量、QC、業務概況…），
並能交叉分析、產出報告、共同記錄與更新。每個業務主題是一個獨立的 Skill，共用同一套名詞、員工名冊與資料層。

## Skill 一覽

| Skill | 業務主題 | 狀態 | 依賴 | 入口 |
|---|---|---|---|---|
| `team-structure` | 團隊架構：Roster、人員標籤、名字對照 | active | — | `management/team-structure/skill.md` |
| `productivity` | 人效：PBI、Fresh（AC／DW）、Chatgroup 的取得與計算 | active | team-structure | `management/productivity/skill.md` |
| （規劃中）`scheduling` | 排班、自動排班腳本 | — | team-structure | 用 `_framework/tools/new_skill.py --domain management` 建立 |
| （規劃中）`overtime` | 加班時數、加班健康度 | — | team-structure、scheduling | |
| （規劃中）`incoming-volume` | 進線量分析、自動計算 | — | team-structure | |
| （規劃中）`qc` | 內部質檢、錯誤評估 | — | team-structure、productivity | |
| （規劃中）`team-health` | 團隊健康度 | — | 多個 | |
| （規劃中）`business-overview` | 業務概況：事故、解決、影響量體、漲幅預估 | — | 多個 | |

## 怎麼找東西
1. 使用者的需求 → 從母入口 `skill.md` 開始：① 找領域 → ② 讀該領域的 `domain.md` 找子 Skill → ③ 讀子 Skill 的 `skill.md`（有「使用者的話 → 指令」對照）。設計見專案根目錄 `SystemDesign.md`
2. 跨 Skill 的規則與慣例 → `_org/conventions.md`（**新進 AI 必讀**）
3. 全專案共用名詞 → `_org/glossary.md`；資料放哪裡 → `_org/data-layout.md`
4. 資料夾分層、機敏等級、稽核紀錄 → `_framework/framework.md`

## 資料夾
```
brain/
├── README.md          本檔：產品與 Skill 地圖
├── skill.md           母入口：① 領域對照表（唯一註冊到 .claude/skills/ 的入口）
├── _framework/        框架層：framework.md、共用程式庫 lib/opbrain、維護工具 tools/（template/ 是 Skill 範本）
├── _org/              組織層：慣例、名詞、資料配置
└── management/        領域
    ├── domain.md      ② 面向 → 子 Skill 對照表
    ├── team-structure/  Skill（skill.md、context.md、rules.md、decision.md、flows/、trace/ + config/ + scripts/）
    └── productivity/    Skill
```

## 改完大腦一定要做
```
python brain/_framework/tools/check_all.py                       # 結構、引用、程式與文件 ID、入口同步、機密掃描
python brain/_framework/tools/kb_log_change.py --skill <名稱> --files ... --summary ... --reason DEC-xxx
python brain/management/productivity/scripts/regression_check.py  # 改了 productivity 的程式或設定時
```
