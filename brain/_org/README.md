# _org — 組織層

> 命名：`_org/` 指「組織」；`brain/<領域>/domain.md` 的 domain 指「業務領域」，兩者無關。

這個組織（OP）專屬、但所有 Skill 共用的東西。換到別的組織時，這一層要重寫；框架層 `brain/_framework/` 不用動。

| 檔案 | 內容 |
|---|---|
| `conventions.md` | 跨 Skill 慣例與工作原則（必讀） |
| `glossary.md` | 全專案共用名詞 |
| `data-layout.md` | `data/` 每個資料夾的用途 |

框架層（`brain/_framework/`）：`framework.md`（三層架構、資料分區與機敏等級、稽核紀錄規範）、`lib/opbrain/`（共用程式庫）、`tools/`（維護工具）。

`_org` 不是 Skill，沒有 Skill 的文件結構；它的規則若涉及業務（例如 Roster 讀法），擁有者是對應的 Skill（team-structure）。
