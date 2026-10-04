# 資料配置（data/）

> 路徑的唯一程式定義：`brain/_core/lib/opbrain/paths.py`。`data/` 整個不入版控。
> 未來規劃：原始資料與標準化資料改放 Lark Drive（權限限主管與核心成員），本機只留快取；
> 程式只透過 `opbrain.paths` 取得路徑，屆時只改這一處。

```
data/
├── raw/                    原始資料，只放取得時的原樣
│   ├── OP Workload P.1/    PBI 原始檔（productivity:S-01）
│   ├── OP Workload P.2/
│   ├── WD WL by Group/
│   ├── tickets_export/     Freshdesk 匯出 Tickets_*.csv（每批整批替換）
│   ├── lark_chatgroup/     Group Management.xlsx
│   └── roster/Roster.xlsx  現行 Roster（擁有者 team-structure）
├── COMBINE/                合併／篩選後的中間成品（PBI 合併檔、Chatgroup Volumn、Tickets 篩選）
├── reports/                最終報表（AC／DW Fresh Report…）
├── knowledge/              主管共同紀錄：事故、註解、會議結論（見 knowledge/README.md）
├── work/                   每次執行的工作目錄 <skill>/<flow>/<時間>/（可隨時刪除）
│   └── _regression/        回歸測試輸出
└── _baseline/              回歸測試的標準答案（勿手動修改）
```

| 路徑 | 寫入者 | 可刪除？ |
|---|---|---|
| raw/ | 下載步驟、匯入步驟、使用者 | 否（重算的來源） |
| COMBINE/、reports/ | 各 Skill 的輸出步驟 | 可（可重算），但通常保留 |
| knowledge/ | 主管（透過 AI） | 否 |
| work/ | 流程執行器 | 可 |
| _baseline/ | 只在規則刻意改變、經確認後更新 | 否 |
