"""
Independent report using EVERY OP Name found in a Roster export (not
the curated 55-employee list) for its own date range, with the exact
same calculation logic and output format as generate_ac_report.py.

Employee list source, date range, and output filename are all set in
config.py (ROSTER_REPORT_*) -- edit those, not this file.

Run:
    python generate_roster_report.py
"""

import sys

import config
from generate_ac_report import generate_report, load_employee_names


def main():
    employee_names = load_employee_names(list_file=config.ROSTER_REPORT_EMPLOYEE_LIST_FILE)
    print(f"  {len(employee_names)} employees loaded from Roster.", flush=True)

    _, ok = generate_report(
        employee_names,
        config.ROSTER_REPORT_OUTPUT_FILENAME,
        config.ROSTER_REPORT_MAIN_SHEET_NAME,
        start_date=config.ROSTER_REPORT_START_DATE,
        end_date=config.ROSTER_REPORT_END_DATE,
    )
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
