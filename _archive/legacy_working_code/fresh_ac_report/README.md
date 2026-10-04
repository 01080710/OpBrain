# AC Daily Module Report

讀取 Fresh 工單原始資料(已經過 Roster 過濾的 `Tickets Roster Tagged Short.csv`,
只有 `Created Time` / `Group` / `Tags` 三欄),計算「每天 × 每位員工 × 每個工作模塊」
的工單數量,產出一份完整格式化的 Excel 報表。這支工具**從零計算**,不依賴、不讀取任何
舊的公式 Excel 模板。

## 資料夾結構

```
fresh_ac_report/
├─ input/                原始資料放這裡(*.csv,欄位需符合 config.py 的 COLUMN_MAPPING)
├─ output/                產出的 Excel 報表會存在這裡
├─ config.py               所有可調整設定(日期範圍、員工名單、模塊規則...)
├─ generate_ac_report.py   主程式
├─ requirements.txt
└─ README.md
```

## 使用方式

```bash
pip install -r requirements.txt
python generate_ac_report.py
```

執行後會依序:

1. 讀取 `config.py` 的員工名單
2. 讀取 `input/` 資料夾內所有 CSV
3. 找出日期無法解析 / Tags 空白 / Group 空白 的異常資料(記錄到 `Invalid Data` 工作表,不會讓程式中斷)
4. 篩選出 `START_DATE` ~ `END_DATE` 範圍內的資料
5. 逐一員工計算每天在各模塊的工單數
6. 建立「每天 × 每位員工」完整表格(沒有工單的模塊填 0,不會漏掉任何一天或任何一位員工)
7. 輸出格式化 Excel 到 `output/`
8. 自動跑驗證(日期是否齊全、員工是否齊全、數字是否非負整數、列數是否正確、隨機抽查至少 3 組「日期＋員工」逐筆重新計算比對),驗證失敗會在畫面上列出失敗原因並以非 0 結束碼結束;驗證通過會印出輸出檔案的完整路徑

## 什麼時候要改 `config.py`,不要改 `generate_ac_report.py`

| 要調整的東西 | 改 `config.py` 的哪個變數 |
| --- | --- |
| 報表日期範圍 | `START_DATE` / `END_DATE` |
| 原始檔案欄位名稱對不上 | `COLUMN_MAPPING` |
| 新增 / 刪除 / 調整順序 員工名單 | `EMPLOYEE_NAMES`(照順序排列,報表列順序會照這個走) |
| 改成從另一份名單檔讀取員工名單 | `EMPLOYEE_LIST_FILE` 設成該檔案路徑(.csv 或 .xlsx,姓名放第一欄) |
| AC 模塊涵蓋哪些 Group | `AC_GROUPS` |
| 單一 Group 對應的模塊(Cpa-Ac / Cpa-Payment / IB / IB-Adjustment / FCA) | `GROUP_MODULE_MAP` |
| CPA 三個關鍵字模塊要搜尋的字串 | `KEYWORD_RULES` |
| 輸出檔名 / 主要工作表名稱 | `OUTPUT_FILENAME` / `MAIN_SHEET_NAME` |

**注意**:`CPA-non-standard plan` 這個輸出欄名,實際搜尋的關鍵字是
`"CPA Standard Commission Plan Update"`(不是 non-standard 字面文字),這是原始需求
明確指定的規則,不是打錯字,不要「修正」它。

## 員工名單現況

`config.py` 裡的 `EMPLOYEE_NAMES` 目前是完整 55 位。如果之後要新增/刪除/調整順序,直接編輯
`EMPLOYEE_NAMES` 這個 list,或改用 `EMPLOYEE_LIST_FILE` 指向一份完整名單檔即可,不需要
改動 `generate_ac_report.py` 任何一行。

## 產出的 4 張工作表

- **`fresh Template Batch (AC)`**(主表):第一列模塊大標題(淺藍底)、第二列格式參考列
  (淡黃底,無公式)、第三列起為實際計算結果(淡黃底,整數,無公式),凍結前兩列、開啟篩選、
  日期格式 `yyyy/m/d`。模塊欄位共 11 欄(C~M),最後一欄是 `Other 2`
- **`Summary`**:原始資料總筆數、日期範圍內資料筆數、每個模塊總數、每位員工總處理數、每日總處理數
- **`Other Groups`**:被歸類為 `Other`(真正未知/新出現)的 Group 名稱與筆數,方便檢查是否
  出現新的 Group。`Other 2` 清單裡的 Group 不會出現在這裡
- **`Invalid Data`**:日期無法解析 / Tags 空白 / Group 空白 的原始資料列,含原始列號與異常原因

## 計算規則摘要

每一筆原始資料,先同時符合「日期在範圍內」+「Tags 包含該員工姓名(不分大小寫、包含比對,
非完全相等)」,才會進一步判斷要計入哪個模塊:

- **AC**:Group 完全等於 `AC_GROUPS` 清單中任一項
- **Cpa-Ac / Cpa-Payment / IB / IB-Adjustment / FCA**:Group 完全等於 `GROUP_MODULE_MAP`
  對應的單一 Group 名稱
- **Other 2**:Group 完全等於 `OTHER2_GROUPS` 清單中任一項 —— 這是「已知但沒有獨立模塊」的
  Group(例如 `(OP)Withdrawal Team`、`(OP)Deposit Team`、`Settlement Team ` 等 18 種),放在
  報表最後一欄,和真正未知的 `Other` 分開
- **Other**:Group 不是空白,且不在 `KNOWN_GROUPS`(= `AC_GROUPS` + 上述 5 個單一 Group +
  `OTHER2_GROUPS`)清單內 —— 只有真正沒見過的新 Group 才會落到這裡
- **CPA-Multi plan / CPA-hybrid plan / CPA-non-standard plan**:不看 Group,只看 Tags 是否
  同時包含員工姓名 + `KEYWORD_RULES` 指定的關鍵字

一筆原始資料的 Tags 若同時包含多位員工姓名,會分別計入每一位員工(不會只算一次);
同一筆資料也可能同時命中一個 Group 模塊 + 一個 CPA 關鍵字模塊(因為 CPA 三個模塊獨立於
Group 判斷之外)。原始資料不去重,兩筆完全相同的資料一律各自算一筆。
