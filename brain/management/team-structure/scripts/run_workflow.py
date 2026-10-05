#!/usr/bin/env python3
"""
（流程總控）team-structure 的具名流程。

流程：
  check   ACT-01 檢查 Roster 健康狀況

用法：python run_workflow.py --flow check [--roster <檔案>]
結束碼：0 成功   1 輸入錯誤   2 關卡擋下   3 緊急停止
"""
import argparse
from pathlib import Path

import _bootstrap  # noqa: F401
from opbrain.common import new_workdir, run
from opbrain.workflow import Step, run_steps

SCRIPT_DIR = Path(__file__).resolve().parent


def main() -> int:
    ap = argparse.ArgumentParser(description="team-structure 流程總控")
    ap.add_argument("--flow", choices=["check"], default="check")
    ap.add_argument("--roster")
    a = ap.parse_args()
    steps = [Step("ACT-01", "roster_check.py", ["--roster", a.roster] if a.roster else [])]
    wd = new_workdir("team-structure", a.flow)
    code = run_steps(SCRIPT_DIR, steps, wd, a.flow)
    print(f"\n===== flow {a.flow}: {'COMPLETE' if code == 0 else 'STOPPED (exit ' + str(code) + ')'} =====")
    return code


if __name__ == "__main__":
    run(main)
