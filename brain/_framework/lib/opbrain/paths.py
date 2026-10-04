"""專案路徑（唯一定義處）。資料夾用途見 brain/_core/data-layout.md。

測試用：設定環境變數 OPBRAIN_OUTPUT_DIR 時，COMBINE 與 REPORTS 都改寫到該目錄，
用於回歸測試（brain/_tools/regression_check.py），不會覆蓋正式輸出。
"""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
BRAIN = PROJECT_ROOT / "brain"

DATA = PROJECT_ROOT / "data"
RAW = DATA / "raw"               # 原始資料：只放取得時的原樣
COMBINE = DATA / "COMBINE"       # 合併／篩選後的中間成品（PBI、Chatgroup、Tickets）
REPORTS = DATA / "reports"       # 最終報表（Fresh AC / DW …）
WORK = DATA / "work"             # 每次執行的工作目錄（中間檔、run_log）
KNOWLEDGE = DATA / "knowledge"   # 主管共同記錄：事故、註解（見 _core/conventions.md）
BASELINE = DATA / "_baseline"    # 回歸測試用的標準答案
AUDIT = DATA / "audit"           # 稽核紀錄：只能附加、不可刪改（不受 OPBRAIN_OUTPUT_DIR 影響）

ROSTER_FILE = RAW / "roster" / "Roster.xlsx"

if os.environ.get("OPBRAIN_OUTPUT_DIR"):
    COMBINE = REPORTS = Path(os.environ["OPBRAIN_OUTPUT_DIR"])


def skill_dir(name: str) -> Path:
    return BRAIN / name
