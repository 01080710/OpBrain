"""
Independent report for the 5-employee VN subset, using the exact same
calculation logic, date range, raw data, and output format as
generate_ac_report.py -- just scoped to config.VN5_EMPLOYEE_NAMES
instead of the full 55-employee list, and written to a separate output
file so it never overwrites the main report.

Run:
    python generate_vn5_report.py
"""

import sys

import config
from generate_ac_report import generate_report


def main():
    _, ok = generate_report(
        config.VN5_EMPLOYEE_NAMES, config.VN5_OUTPUT_FILENAME, config.VN5_MAIN_SHEET_NAME
    )
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
