"""
Build the AC and DW Fresh reports for a date range, in one run.

For a colleague running this in VS Code: open this file, then use
"Run Python File". You do NOT need to edit this file -- it asks for
everything it needs when it runs.

What it does:
1. Asks for a start date and end date (YYYY-MM-DD).
2. Asks for a new Tickets export folder (the folder containing
   Tickets_1.csv, Tickets_2.csv, ...) and a new Roster file. Press
   Enter to skip either one and reuse the data already in the project.
3. Filters the tickets down to rows that tag a Roster OP Name, then
   builds both reports with every Roster OP Name included:
       fresh_ac_report/output/AC Fresh Report <start> - <end>.xlsx
       fresh_ac_report/output/DW Fresh Report <start> - <end>.xlsx
4. Prints a summary. If any step fails, it says so and the output
   files from that run must not be used.
"""

import sys

from src.workflows.fresh_pipeline import run_fresh_reports


def _prompt_date(label: str) -> str:
    while True:
        value = input(f"{label} (YYYY-MM-DD): ").strip()
        if len(value) == 10 and value[4] == "-" and value[7] == "-":
            return value
        print("  Please use the format YYYY-MM-DD, e.g. 2026-09-01")


def _prompt_path(label: str):
    value = input(f"{label} (press Enter to reuse existing): ").strip().strip('"')
    return value or None


def main():
    start = _prompt_date("Start date")
    end = _prompt_date("End date")
    tickets = _prompt_path("New Tickets export folder")
    roster = _prompt_path("New Roster file")
    result = run_fresh_reports(start, end, tickets_folder=tickets, roster_file=roster)
    if result["status"] != "COMPLETE":
        sys.exit(1)


if __name__ == "__main__":
    main()
