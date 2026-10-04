# Actions（動作）

> **核心問題**：有哪些可執行的原子動作？各自的前置條件、效果與可逆性是什麼？
> **狀態**：`skeleton`（尚未填寫）｜ **最後更新**：— ｜ **負責人**：—

## 本文件負責
- 動作目錄：輸入、前置、效果、權限、冪等性、可逆性

## 本文件不負責（請放到別處）
- 動作的排序 → `execution/workflow.md`
- 動作是否該自動執行 → `execution/automation.md`

## 內容

| 動作 ID | 說明 | 實作 | 輸入 | 前置條件 | 效果（副作用） | 所需權限 | 冪等 | 可逆（如何） |
|---|---|---|---|---|---|---|---|---|
| ACT-01 | 取得原始資料 | `scripts/fetch_data.py` | 來源路徑或 https URL | 來源可讀取 | 寫入 raw.csv、fetch_manifest.json | 讀來源、寫工作目錄 | Y | Y（刪除輸出） |
| ACT-02 | 驗證輸入結構 | `scripts/validate_input.py` | raw.csv | ACT-01 完成 | 寫入 input_check.json | 讀寫工作目錄 | Y | Y |
| ACT-03 | 清洗資料 | `scripts/clean_data.py` | raw.csv | ACT-02 通過 | 寫入 cleaned.csv、rejected.csv、cleaning_log.json；中止時移除舊 cleaned.csv | 讀寫工作目錄 | Y | Y（raw.csv 不變） |
| ACT-04 | 資料處理（重塑） | `scripts/process_data.py` | cleaned.csv | ACT-03 成功 | 寫入 processed.csv、processing_log.json | 讀寫工作目錄 | Y | Y |
| ACT-05 | 指標計算 | `scripts/compute_metrics.py` | processed.csv | ACT-04 完成 | 寫入 metrics.json | 讀寫工作目錄 | Y | Y |
| ACT-06 | 套用確定性規則 | `scripts/apply_rules.py` | processed.csv | ACT-04 完成 | 寫入 decisions.csv、decision_summary.json | 讀寫工作目錄 | Y | Y |
| ACT-07 | 評估衡量標準 | `scripts/evaluate_criteria.py` | cleaning_log.json、decisions.csv | ACT-03、ACT-06 完成 | 寫入 criteria_result.json；有 fail 時結束碼 2（關卡） | 讀寫工作目錄 | Y | Y |
| ACT-08 | 驗證輸出 | `scripts/validate_output.py` | 工作目錄內全部輸出 | ACT-13 完成 | 寫入 validation_result.json；未通過時結束碼 2（關卡） | 讀寫工作目錄 | Y | Y |
| ACT-09 | 品質檢查 | `scripts/quality_check.py` | cleaned.csv | ACT-03 成功 | 寫入 quality_report.json（只評分，不阻擋） | 讀寫工作目錄 | Y | Y |
| ACT-10 | 產出報告 | `scripts/build_report.py` | metrics、criteria、cleaning_log、decisions | ACT-05、06、07 完成 | 寫入 report.md（不含個資） | 讀寫工作目錄 | Y | Y |
| ACT-11 | 打包交付物 | `scripts/package_deliverables.py` | report.md、metrics.json、decisions_masked.csv | ACT-08 通過且 ACT-07 非 fail | 建立 dist/<version>/ 與 MANIFEST.json；同版本不可覆寫 | 寫入交付目錄 | N（同版本重跑會失敗，屬設計） | N（刪除版本需授權者） |
| ACT-12 | 機密掃描 | `scripts/scan_secrets.py` | 指定目錄 | 無 | 只讀；發現時結束碼 2（關卡），不印出內容 | 唯讀 | Y | Y（無副作用） |
| ACT-13 | 個資遮罩 | `scripts/mask_pii.py` | decisions.csv、要遮罩的欄位 | ACT-06 完成 | 寫入 decisions_masked.csv、pii_mask_log.json；原檔不變 | 讀寫工作目錄 | Y | Y |

> 上表由 `scripts/` 的範本實作登記而來（以範例資料驅動）；導入實際主題時請逐列改寫，並維持「動作 ID ↔ 腳本 docstring ↔ `scripts/run_workflow.py`」一致。
> 另有 `scripts/run_workflow.py`（總控）與 `kb_*.py`（知識庫維護）不屬於業務動作，不在此登記。

> 不可逆動作必須在 `safety/safety.md` 登記人工確認點。

## 依據來源（Evidence）
- `[待填]` 每項內容標註來源：`[來源: 路徑#行號 / 文件 / 訪談]`、`[假設 A-xxx]` 或 `[待確認]`

## 完成標準
- [ ] 有副作用的動作都標註可逆性
- [ ] 不可逆動作已連結到人工確認點
- [ ] 所有 `[待填]` 已替換，或明確標為 `[不適用：理由]`
