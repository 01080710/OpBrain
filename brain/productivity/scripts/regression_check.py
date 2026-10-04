#!/usr/bin/env python3
"""
（回歸測試）用現有原始資料重跑所有流程，逐格比對 data/_baseline/ 的標準答案。

對應：context.md TC-001～TC-005
- 輸出寫到 data/work/_regression/<時間>/（OPBRAIN_OUTPUT_DIR），不覆蓋正式輸出、不受 Excel 開檔影響
- PBI 不下載（--no-download），只用現有原始檔
- Fresh Summary 的「Employee Totals」區塊只比內容不比順序（DEC-012：排序統一改為報表名單順序）

用法：python regression_check.py
結束碼：0 全部相同   2 有差異或流程失敗
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import _bootstrap  # noqa: F401
from opbrain import paths

HERE = Path(__file__).resolve().parent
COMPARE = paths.BRAIN / "_tools" / "compare_outputs.py"
EMP_BLOCK = "Summary:Employee Totals (all modules combined)"

RUNS = [  # (說明, run_workflow 參數)
    ("TC-001 pbi 09-21~09-30", ["--flow", "pbi", "--no-download", "--start", "2026-09-21", "--end", "2026-09-30"]),
    ("TC-001 pbi 09-01~09-20", ["--flow", "pbi", "--no-download", "--start", "2026-09-01", "--end", "2026-09-20"]),
    ("TC-001 pbi 06-01~08-31", ["--flow", "pbi", "--no-download", "--start", "2026-06-01", "--end", "2026-08-31"]),
    ("TC-002 chatgroup", ["--flow", "chatgroup", "--start", "2026-09-01", "--end", "2026-09-30"]),
    ("TC-003/004 fresh ac+dw", ["--flow", "fresh", "--start", "2026-09-01", "--end", "2026-09-30"]),
    ("TC-005 fresh main55", ["--flow", "fresh", "--reports", "ac", "--employees", "main55",
                             "--start", "2026-09-01", "--end", "2026-09-30"]),
    ("TC-005 fresh vn5", ["--flow", "fresh", "--reports", "ac", "--employees", "vn5",
                          "--start", "2026-09-01", "--end", "2026-09-30"]),
]

PAIRS = [  # (標準答案, 新產出檔名, 額外參數)
    *[(f"pbi/{n}", n.split("/")[-1], []) for n in [
        f"COMBINE-OP_Workload_P1__{r}.xlsx" for r in ("2026-09-21 to 2026-09-30", "2026-09-01 to 2026-09-20", "2026-06-01 to 2026-08-31")
    ] + [
        f"COMBINE-OP_Workload_P2_{r}.xlsx" for r in ("2026-09-21 to 2026-09-30", "2026-09-01 to 2026-09-20", "2026-06-01 to 2026-08-31")
    ] + [
        f"COMBINE-WD_WL_by_Group_{r}.xlsx" for r in ("2026-09-21 to 2026-09-30", "2026-09-01 to 2026-09-20", "2026-06-01 to 2026-08-31")
    ]],
    ("chatgroup/AC Chatgroup Volumn 2026-09-01 to 2026-09-30.xlsx", "AC Chatgroup Volumn 2026-09-01 to 2026-09-30.xlsx", []),
    ("chatgroup/DW Chatgroup Volumn 2026-09-01 to 2026-09-30.xlsx", "DW Chatgroup Volumn 2026-09-01 to 2026-09-30.xlsx", []),
    ("tickets/Tickets Roster Tagged.csv", "Tickets Roster Tagged.csv", []),
    ("tickets/Tickets Roster Tagged Short.csv", "Tickets Roster Tagged Short.csv", []),
    ("fresh/AC Fresh Report 2026-09-01 - 2026-09-30.xlsx", "AC Fresh Report 2026-09-01 - 2026-09-30.xlsx", ["--ignore-order-block", EMP_BLOCK]),
    ("fresh/DW Fresh Report 2026-09-01 - 2026-09-30.xlsx", "DW Fresh Report 2026-09-01 - 2026-09-30.xlsx", ["--ignore-order-block", EMP_BLOCK]),
    ("fresh/AC55.xlsx", "AC Fresh Report main55 2026-09-01 - 2026-09-30.xlsx", ["--ignore-order-block", EMP_BLOCK]),
    ("fresh/VN5.xlsx", "AC Fresh Report vn5 2026-09-01 - 2026-09-30.xlsx", ["--ignore-order-block", EMP_BLOCK]),
]


def main() -> int:
    out = paths.WORK / "_regression" / datetime.now().strftime("%Y%m%d-%H%M%S")
    out.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "OPBRAIN_OUTPUT_DIR": str(out)}
    failed = False
    for label, argv in RUNS:
        code = subprocess.run([sys.executable, str(HERE / "run_workflow.py"), *argv], env=env,
                              capture_output=True, text=True, encoding="utf-8", errors="replace").returncode
        print(f"{'OK  ' if code == 0 else 'FAIL'} {label} (exit {code})")
        failed |= code != 0
    print()
    for base, new, extra in PAIRS:
        code = subprocess.run([sys.executable, str(COMPARE), str(paths.BASELINE / base), str(out / new), *extra]).returncode
        failed |= code != 0
    print(f"\nRegression {'FAILED' if failed else 'PASSED'} -- outputs in {out}")
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
