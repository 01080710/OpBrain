#!/usr/bin/env python3
"""
（流程總控）productivity 的具名流程。遇到失敗或關卡擋下就停止，後續步驟不執行。

流程（詳見 skill.md「流程一覽」、sources.md 與 flows/ac.md、flows/dw.md）：
  pbi           [ACT-01 下載（最多重試 3 次）] → 02 檢查原始檔 → 03 清理 → 04 合併 → 05 寫檔 → 06 驗證
                --no-download 只合併現有原始檔（原 PBI Combine）
  fresh         ACT-10 匯入新資料（選擇性）→ 11 檢查 → 12 依 Roster 篩選
                → 每種報表（--reports ac dw）：13 計算 → 14 寫報表 → 15 驗證
  chatgroup     ACT-20 檢查 → 21 擷取 → 22 姓名轉換 → 23 寫檔 → 24 驗證
  open-browser  ACT-07 開啟 Power BI 登入用的 Edge（最大化）

工作目錄：data/work/productivity/<flow>/<時間>/（中間檔、run_log.json）
緊急停止：在工作目錄放一個 STOP 檔，下一步開始前就會停止（結束碼 3）
結束碼：0 全部成功   1 某步輸入錯誤   2 某步被關卡擋下   3 被緊急停止

用法：
  python run_workflow.py --flow pbi --start 2026-09-21 --end 2026-09-30
  python run_workflow.py --flow pbi --start 2026-09-21 --end 2026-09-30 --no-download
  python run_workflow.py --flow fresh --start 2026-09-01 --end 2026-09-30 \
      --source-folder "C:/Users/.../Fresh Sept" --roster "C:/Users/.../Roster 202609.xlsx"
  python run_workflow.py --flow chatgroup --start 2026-09-01 --end 2026-09-30
  python run_workflow.py            （不帶參數 = 互動模式，逐項詢問）
"""
import argparse
import sys
from pathlib import Path

import _bootstrap  # noqa: F401
from opbrain import config
from opbrain.common import EXIT_INPUT, InputError, new_workdir, read_json, run
from opbrain.workflow import Step, run_steps

SCRIPT_DIR = Path(__file__).resolve().parent
FLOWS = ["pbi", "fresh", "chatgroup", "open-browser"]


def build_steps(a):
    rng = ["--start", a.start, "--end", a.end] if a.start else []
    if a.flow == "open-browser":
        return [Step("ACT-07", "pbi_open_browser.py")]
    if a.flow == "pbi":
        rep = ["--reports", *a.reports] if a.reports else []
        steps = []
        if not a.no_download:
            tries = config.load("productivity", "pbi")["max_download_attempts"]
            steps.append(Step("ACT-01", "pbi_fetch.py", rng + rep + (["--force"] if a.force else []), retries=tries))
        steps += [Step("ACT-02", "pbi_validate_input.py", rng + rep),
                  Step("ACT-03", "pbi_clean.py"), Step("ACT-04", "pbi_process.py"),
                  Step("ACT-05", "pbi_build_output.py"), Step("ACT-06", "pbi_validate_output.py")]
        return steps
    if a.flow == "fresh":
        intake = (["--source-folder", a.source_folder] if a.source_folder else []) + \
                 (["--roster", a.roster] if a.roster else [])
        steps = [Step("ACT-10", "tickets_intake.py", intake),
                 Step("ACT-11", "tickets_validate_input.py"), Step("ACT-12", "tickets_clean.py")]
        for kind in (a.reports or ["ac", "dw"]):
            if kind not in ("ac", "dw"):
                raise InputError(f"fresh --reports must be ac and/or dw, got {kind!r}")
            k = ["--kind", kind]
            steps += [Step("ACT-13", "fresh_compute.py", k + rng + ["--employees", a.employees]),
                      Step("ACT-14", "fresh_build_report.py", k),
                      Step("ACT-15", "fresh_validate_output.py", k)]
        return steps
    if a.flow == "chatgroup":
        tg = ["--targets", *a.reports] if a.reports else []
        return [Step("ACT-20", "chatgroup_validate_input.py", rng + tg),
                Step("ACT-21", "chatgroup_process.py"), Step("ACT-22", "chatgroup_apply_rules.py"),
                Step("ACT-23", "chatgroup_build_output.py"), Step("ACT-24", "chatgroup_validate_output.py")]
    raise InputError(f"unknown flow {a.flow!r}; valid: {FLOWS}")


def print_outputs(flow, wd):
    files = {"pbi": "pbi_outputs.json", "chatgroup": "chatgroup_outputs.json"}
    found = []
    if flow in files and (wd / files[flow]).exists():
        found = [o["output_path"] for o in read_json(wd / files[flow]).values()]
    if flow == "fresh":
        found = [read_json(p)["output_path"] for p in sorted(wd.glob("fresh_*_validation.json"))]
        if (wd / "tickets_clean.json").exists():
            t = read_json(wd / "tickets_clean.json")
            print(f"Tickets: scanned {t['rows_scanned']}, kept {t['rows_kept']}")
    for f in found:
        print(f"  OUTPUT: {f}")


def interactive(a):
    print("Flows: " + ", ".join(FLOWS))
    a.flow = input("Flow: ").strip()
    if a.flow != "open-browser":
        a.start = input("Start date (YYYY-MM-DD): ").strip()
        a.end = input("End date (YYYY-MM-DD): ").strip()
    if a.flow == "fresh":
        a.source_folder = input("New Tickets export folder (Enter = reuse existing): ").strip().strip('"') or None
        a.roster = input("New Roster file (Enter = reuse existing): ").strip().strip('"') or None
    return a


def main() -> int:
    ap = argparse.ArgumentParser(description="productivity 流程總控")
    ap.add_argument("--flow", choices=FLOWS)
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--reports", nargs="*", default=None,
                    help="pbi: 報表 key；fresh: ac / dw；chatgroup: ac / dw；不填 = 全部")
    ap.add_argument("--no-download", action="store_true", help="pbi：只合併現有原始檔")
    ap.add_argument("--force", action="store_true", help="pbi：已存在的原始檔也重新下載")
    ap.add_argument("--source-folder", help="fresh：新的 Tickets 匯出資料夾")
    ap.add_argument("--roster", help="fresh：新的 Roster 檔")
    ap.add_argument("--employees", default="roster", help="fresh：roster（預設）/ main55 / vn5")
    a = ap.parse_args()
    if a.flow is None:
        a = interactive(a)
    if a.flow != "open-browser" and not (a.start and a.end):
        raise InputError("--start and --end are required")

    steps = build_steps(a)
    wd = new_workdir("productivity", a.flow)
    print(f"Workdir: {wd}")
    code = run_steps(SCRIPT_DIR, steps, wd, a.flow)
    print(f"\n===== flow {a.flow}: {'COMPLETE' if code == 0 else 'STOPPED (exit ' + str(code) + ')'} =====")
    print_outputs(a.flow, wd)
    return code


if __name__ == "__main__":
    run(main)
