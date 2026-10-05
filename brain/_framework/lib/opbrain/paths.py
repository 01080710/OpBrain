"""專案路徑（唯一定義處）。資料夾用途見 brain/_org/data-layout.md。

測試用：設定環境變數 OPBRAIN_OUTPUT_DIR 時，COMBINE 與 REPORTS 都改寫到該目錄，
用於回歸測試（brain/management/productivity/scripts/regression_check.py），不會覆蓋正式輸出。
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
KNOWLEDGE = DATA / "knowledge"   # 主管共同記錄：事故、註解（見 _org/conventions.md）
BASELINE = DATA / "_baseline"    # 回歸測試用的標準答案
AUDIT = DATA / "audit"           # 稽核紀錄：只能附加、不可刪改（不受 OPBRAIN_OUTPUT_DIR 影響）

ROSTER_FILE = RAW / "roster" / "Roster.xlsx"

if os.environ.get("OPBRAIN_OUTPUT_DIR"):
    COMBINE = REPORTS = Path(os.environ["OPBRAIN_OUTPUT_DIR"])


def skill_dir(name: str) -> Path:
    """Skill 資料夾：brain/<領域>/<skill>/（Skill 放在擁有它的領域底下）。"""
    hits = [d / name for d in sorted(BRAIN.iterdir())
            if d.is_dir() and not d.name.startswith("_") and (d / name / "skill.md").is_file()]
    if len(hits) != 1:
        raise FileNotFoundError(f"Skill {name!r}: expected exactly one brain/<domain>/{name}/skill.md, found {len(hits)}")
    return hits[0]
