# _core — 共用層

所有 Skill 共用、不屬於任何單一業務主題的東西：

| 檔案 | 內容 |
|---|---|
| `conventions.md` | 跨 Skill 慣例與工作原則（必讀） |
| `glossary.md` | 全專案共用名詞 |
| `data-layout.md` | `data/` 每個資料夾的用途 |
| `lib/opbrain/` | 共用程式庫：`paths`（路徑）、`common`（結束碼、工作目錄、讀寫）、`config`（讀設定檔）、`roster`（讀 Roster，實作 team-structure 的規則）、`workflow`（流程執行器）、`env`（讀 .env） |

`_core` 不是 Skill，沒有 Skill 的文件結構；它的規則若涉及業務（例如 Roster 讀法），擁有者是對應的 Skill（team-structure）。
