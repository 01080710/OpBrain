# OP Workforce AI

給 OP 主管用的團隊營運 AI：用問的方式掌握人效、排班、加班、進線量、QC 與業務狀況，
並能交叉分析、產出報告、共同記錄。整個產品的「大腦」在 [brain/](brain/README.md)。

## 安裝（第一次）
```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m playwright install msedge   # 只有要下載 Power BI 時需要
copy .env.example .env                                   # 填入 PBI_REPORT_URL
```

## 使用
在 VS Code 開啟本資料夾，用 Claude Code（或其他 AI）直接說需求，例如：
- 「下載 PBI 9/21～9/30 三份報表再 combine」
- 「用桌面的 Fresh Sept 資料夾和新 Roster，出 9 月 AC 跟 DW fresh 報表」
- 「跑 Lark Chatgroup Volumn 9/1～9/30」
- 「檢查 Roster」

不用 AI 也可以直接執行（不帶參數會逐項詢問）：
```
.venv\Scripts\python.exe brain\productivity\scripts\run_workflow.py
```

## 資料夾
| 資料夾 | 內容 |
|---|---|
| `brain/` | 大腦：每個業務主題一個 Skill（規則、作業程序、程式）＋共用層 |
| `data/` | 所有真實資料與輸出（不入版控），見 `brain/_core/data-layout.md` |
| `_archive/` | 已停用的舊程式，只供參考，不要使用 |
| `.claude/skills/` | 自動產生的 Claude 入口，不要手改 |
