"""
Generate the AC and/or DW Fresh reports for a date range, using every
OP Name in a given Roster file -- without editing config.py.

Output files are named after the date range:
    output/AC Fresh Report <start> - <end>.xlsx
    output/DW Fresh Report <start> - <end>.xlsx

Run:
    python run_reports.py --start 2026-09-01 --end 2026-09-30 \
        --roster "input/Roster 202609.xlsx" --reports ac dw

The last line printed is "RESULT_JSON: {...}" so that
src/workflows/fresh_pipeline.py can read the outcome.
"""

import argparse
import json
import sys
from pathlib import Path

import config
from generate_ac_report import generate_report, load_employee_names
from generate_dw_report import generate_dw_report

AC_SHEET_NAME = "fresh Template Batch (AC)"
DW_SHEET_NAME = config.DW_MAIN_SHEET_NAME


def run(start_date, end_date, roster_file, reports=("ac", "dw")) -> dict:
    roster_path = Path(roster_file)
    if not roster_path.is_absolute():
        roster_path = config.BASE_DIR / roster_path
    employee_names = load_employee_names(list_file=roster_path)

    results = {}
    if "ac" in reports:
        print("\n===== AC Fresh Report =====", flush=True)
        path, ok = generate_report(
            employee_names,
            f"AC Fresh Report {start_date} - {end_date}.xlsx",
            AC_SHEET_NAME,
            start_date=start_date,
            end_date=end_date,
        )
        results["ac"] = {"output_path": str(path), "validation_passed": ok}
    if "dw" in reports:
        print("\n===== DW Fresh Report =====", flush=True)
        path, ok, totals = generate_dw_report(
            employee_names,
            f"DW Fresh Report {start_date} - {end_date}.xlsx",
            DW_SHEET_NAME,
            start_date,
            end_date,
        )
        results["dw"] = {"output_path": str(path), "validation_passed": ok, "module_totals": totals}
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="YYYY-MM-DD, inclusive")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD, inclusive")
    ap.add_argument("--roster", required=True, help="Roster .xlsx (names in first column)")
    ap.add_argument("--reports", nargs="+", default=["ac", "dw"], choices=["ac", "dw"])
    args = ap.parse_args()

    results = run(args.start, args.end, args.roster, args.reports)
    print("RESULT_JSON: " + json.dumps(results, ensure_ascii=False))
    if not all(r["validation_passed"] for r in results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
