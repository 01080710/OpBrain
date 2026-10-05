# 管理領域（brain/management/domain.md）

> **核心問題**：這個管理問題涉及哪些面向？要用哪些子 Skill？
> 本檔只負責 ② 找面向，不放業務規則或指令；指令在各子 Skill 的 `skill.md`。

## 面向對照表

一個問題可以同時命中多個面向；命中多個子 Skill 時，依各 `skill.md` frontmatter 的 `depends_on` 排順序（被依賴的先跑）。

| 面向 | 使用者會怎麼問 | 子 Skill | 狀態 |
|---|---|---|---|
| 團隊架構 | 檢查／換新 Roster、某人為什麼對不到、團隊幾個人、各國／各團隊人數 | `brain/management/team-structure/skill.md` | active |
| 人效 | PBI 下載／合併、AC／DW Fresh 報表、Chatgroup Volumn | `brain/management/productivity/skill.md` | active |
| 排班 | 排班、班表、人力缺口 | `scheduling` | 尚未建立 → 回報「尚未支援」 |
| 加班 | 加班時數、加班健康度 | `overtime` | 尚未建立 → 回報「尚未支援」 |
| 進線量 | 進線量分析 | `incoming-volume` | 尚未建立 → 回報「尚未支援」 |
| 品質 | 內部質檢、錯誤評估 | `qc` | 尚未建立 → 回報「尚未支援」 |
| 團隊健康度 | 團隊健康度 | `team-health` | 尚未建立 → 回報「尚未支援」 |
| 業務概況 | 事故、解決、影響量體、漲幅預估 | `business-overview` | 尚未建立 → 回報「尚未支援」 |

## 備註
- 本領域擁有的子 Skill 放在本資料夾底下（`brain/management/<skill>/`）；其他領域需要時，在自己的 `domain.md` 跨資料夾引用。
- 新增子 Skill：`python brain/_framework/tools/new_skill.py --domain management --name <skill> ...` 建好後，在上表把「子 Skill」改成 `brain/management/<skill>/skill.md` 並把狀態改為 active；沒收錄的 Skill，`check_all.py` 會擋下（E-3）。
