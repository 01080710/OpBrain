# OP Workforce AI — 大腦（brain/）

這個資料夾是整個專案的「大腦」：所有業務規則、作業程序、工具程式都在這裡。
任何 AI（Claude、Cursor、Codex…）或開發者進到專案，都從這裡開始。

## 這個產品是什麼
給 OP 主管用的團隊營運 AI。主管用問的方式掌握團隊各面向（人效、排班、加班、進線量、QC、業務概況…），
並能交叉分析、產出報告、共同記錄與更新。每個業務主題是一個獨立的 Skill，共用同一套名詞、員工名冊與資料層。

## Skill 一覽

| Skill | 業務主題 | 狀態 | 依賴 | 入口 |
|---|---|---|---|---|
| `team-structure` | 團隊架構：Roster、人員標籤、名字對照 | active | — | `team-structure/skill.md` |
| `productivity` | 人效：PBI、Fresh（AC／DW）、Chatgroup 的取得與計算 | active | team-structure | `productivity/skill.md` |
| （規劃中）`scheduling` | 排班、自動排班腳本 | — | team-structure | 用 `_tools/new_skill.py` 建立 |
| （規劃中）`overtime` | 加班時數、加班健康度 | — | team-structure、scheduling | |
| （規劃中）`incoming-volume` | 進線量分析、自動計算 | — | team-structure | |
| （規劃中）`qc` | 內部質檢、錯誤評估 | — | team-structure、productivity | |
| （規劃中）`team-health` | 團隊健康度 | — | 多個 | |
| （規劃中）`business-overview` | 業務概況：事故、解決、影響量體、漲幅預估 | — | 多個 | |

## 怎麼找東西
1. 使用者的需求屬於哪個業務主題 → 讀該 Skill 的 `skill.md`（有「使用者的話 → 指令」對照）
2. 跨 Skill 的規則與慣例 → `_core/conventions.md`（**新進 AI 必讀**）
3. 全專案共用名詞 → `_core/glossary.md`；資料放哪裡 → `_core/data-layout.md`

## 資料夾
```
brain/
├── README.md          本檔：產品與 Skill 地圖
├── _core/             共用層：慣例、名詞、資料配置、共用程式庫 lib/opbrain
├── _tools/            維護工具：檢查、建立新 Skill、產生 .claude 入口、回歸比對；template/ 是 Skill 範本
├── team-structure/    Skill（skill.md、context.md、rules.md、decision.md、flows/、trace/ + config/ + scripts/）
└── productivity/      Skill
```

## 改完大腦一定要做
```
python brain/_tools/check_all.py                       # 結構、引用、程式與文件 ID、入口同步、機密掃描
python brain/_tools/kb_log_change.py --skill <名稱> --files ... --summary ... --reason DEC-xxx
python brain/productivity/scripts/regression_check.py  # 改了 productivity 的程式或設定時
```
