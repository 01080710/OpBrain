# data/knowledge — 主管共同紀錄

規則見 `brain/_core/conventions.md` 第 6 節。這裡放「發生過的事」，不是規則：
事故、對某段數據的註解、人員異動說明、會議結論。AI 分析團隊狀況時會一併讀取並標明出處。

## 結構
```
knowledge/
├── events/   事故與事件：一件事一個檔  YYYY-MM-DD_<簡短標題>.md
└── notes/    對數據的註解、會議結論：   YYYY-MM-DD_<簡短標題>.md
```
一筆紀錄一個檔，多人同時寫入不會互相覆蓋。

## 檔案格式
```markdown
---
type: event            # event | note
date: 2026-09-15       # 發生日期
end_date: 2026-09-15   # 選填
skills: [productivity] # 相關的 Skill
teams: [DW]            # 選填：相關團隊／標籤
recorded_by: Howard Huang
recorded_at: 2026-10-02
---
# 出入金系統事故

- 影響：DW 處理約 3 小時停擺
- 影響量體：…
- 解決：…
```
