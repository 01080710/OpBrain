"""
Download + Combine PBI reports for a date range, in one run.

For a colleague running this in VS Code: open this file, then use
"Run Python File" (the triangle button, or right-click > Run Python
File in Terminal). You do NOT need to edit this file to change the
date range -- it will ask you for it when it runs.

--------------------------------------------------------------------
BEFORE YOU RUN THIS: log into Power BI manually
--------------------------------------------------------------------
MFA cannot be automated, so you must open the browser and log in
yourself first, every time:

1. Open a terminal and run (this opens a NEW Edge window -- your
   normal Edge windows are not affected):

       msedge --remote-debugging-port=9333 --user-data-dir="%TEMP%\\pbi_edge_profile"

2. In that new Edge window, open the Power BI report URL (the same one
   saved in this project's .env as PBI_REPORT_URL -- ask whoever gave
   you this project for that link if you don't have .env yet) and log
   in (including 2FA) by hand.

3. Make sure that report tab is the ONLY tab open in that Edge window
   (this script always attaches to the first tab) -- close any other
   tabs that opened along the way (e.g. a "welcome" tab).

4. Leave that Edge window open. Come back here and run this script.
   Keep the Edge window open for the whole run -- closing it closes
   the browser this script downloads through.

--------------------------------------------------------------------
What this script does
--------------------------------------------------------------------
1. Asks for a start date and end date (YYYY-MM-DD).
2. Downloads all 3 reports for that range into data/raw/ (anything
   already downloaded is skipped, not re-downloaded).
3. If -- and only if -- every file downloaded successfully, combines
   each report's files for that range into one Excel file per report
   under data/COMBINE/.
4. Prints a summary at the end.

If some downloads fail, Combine is skipped for that run (so it never
produces a file that looks complete but is missing data) -- just
re-run this script with the same date range afterward; anything that
already succeeded is skipped automatically, so it only retries what's
missing.
"""

import sys

from src.workflows.pbi_pipeline import run_pbi_pipeline


def _prompt_date(label: str) -> str:
    while True:
        value = input(f"{label} (YYYY-MM-DD): ").strip()
        if len(value) == 10 and value[4] == "-" and value[7] == "-":
            return value
        print("  Please enter a date in YYYY-MM-DD format, e.g. 2026-09-10")


def main():
    print(__doc__)

    if len(sys.argv) >= 3:
        start_date, end_date = sys.argv[1], sys.argv[2]
    else:
        start_date = _prompt_date("Start date")
        end_date = _prompt_date("End date")

    print(f"\nRunning PBI pipeline for {start_date} to {end_date}...\n", flush=True)

    try:
        result = run_pbi_pipeline(start_date, end_date)
    except RuntimeError as e:
        print(f"\n{e}")
        print(
            "\nMake sure you completed the manual login step above "
            "before running this script."
        )
        sys.exit(1)

    print("\n=== Summary ===")
    d = result["download"]
    print(
        f"Download -- expected: {d['expected']}, downloaded: {d['downloaded']}, "
        f"skipped: {d['skipped']}, failed: {len(d['failed'])}"
    )

    if result["combine"] is None:
        print("Combine was skipped because Download did not fully complete.")
    else:
        for report_key, r in result["combine"].items():
            print(f"Combine [{report_key}] -- status: {r['status']}, output: {r['output_path']}")


if __name__ == "__main__":
    main()
