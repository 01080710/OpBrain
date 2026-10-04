"""
Fresh Report Pipeline: Tickets export -> Roster filter -> AC + DW reports.

Chains, unmodified:
  - src/processors/tickets_roster_filter.py (filter_tickets_by_roster,
    filter_tickets_short)
  - fresh_ac_report/run_reports.py (AC Fresh Report + DW Fresh Report),
    run as a subprocess because fresh_ac_report/ is an independent
    sub-project whose `config` module would clash with this project's
    `config` package if imported in the same process.

Steps:
  1. (optional) Replace data/raw/tickets_export/Tickets_*.csv with the
     files from a new export folder -- checked first, old files removed
     only after the new ones pass the checks.
  2. (optional) Replace data/raw/roster/Roster.xlsx with a new Roster.
  3. Run the Roster filter (full + short outputs to data/COMBINE/).
  4. Copy the short output into fresh_ac_report/input/ (the manual
     "copy the snapshot" step).
  5. Generate the AC and/or DW reports for the date range, every Roster
     OP Name included, files named "<AC|DW> Fresh Report <start> - <end>.xlsx".

Never writes reports from a failed step: any failure stops the pipeline
with status FAILED.
"""

import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import openpyxl
import pandas as pd

from src.processors.tickets_roster_filter import (
    ROSTER_PATH,
    SOURCE_DIR,
    filter_tickets_by_roster,
    filter_tickets_short,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRESH_DIR = PROJECT_ROOT / "fresh_ac_report"
FRESH_INPUT = FRESH_DIR / "input"
SHORT_CSV = PROJECT_ROOT / "data" / "COMBINE" / "Tickets Roster Tagged Short.csv"
REQUIRED_TICKET_COLUMNS = ["Created Time", "Group", "Tags"]
ROSTER_NAME_HEADERS = ("op name", "crm op name")


def _fail(result, msg):
    result["status"] = "FAILED"
    result["error"] = msg
    print(f"\nFresh pipeline FAILED: {msg}", flush=True)
    return result


def _check_tickets_folder(folder: Path):
    files = sorted(folder.glob("Tickets_*.csv"))
    if not files:
        return None, f"No Tickets_*.csv files in {folder}"
    ref = None
    for f in files:
        cols = pd.read_csv(f, dtype=str, nrows=0).columns.tolist()
        missing = [c for c in REQUIRED_TICKET_COLUMNS if c not in cols]
        if missing:
            return None, f"{f.name} is missing column(s) {missing}"
        if ref is None:
            ref = cols
        elif cols != ref:
            return None, f"{f.name} has different columns than {files[0].name}"
    return files, None


def _check_roster(path: Path):
    if not path.exists():
        return f"Roster file not found: {path}"
    wb = openpyxl.load_workbook(path, read_only=True)
    header = next(wb[wb.sheetnames[0]].iter_rows(max_row=1, values_only=True), ())
    wb.close()
    first = str(header[0]).strip().lower() if header and header[0] is not None else ""
    if first not in ROSTER_NAME_HEADERS:
        return (
            f"Roster's first column must be 'OP Name' or 'CRM OP Name' "
            f"(the reports read names from the first column), found {header[0]!r}"
        )
    return None


def run_fresh_reports(
    start_date: str,
    end_date: str,
    tickets_folder=None,
    roster_file=None,
    reports=("ac", "dw"),
) -> dict:
    """
    Args:
        start_date, end_date: "YYYY-MM-DD", inclusive
        tickets_folder: folder with a new Tickets_*.csv export, or None to
            reuse what is already in data/raw/tickets_export/
        roster_file: a new Roster .xlsx, or None to reuse
            data/raw/roster/Roster.xlsx
        reports: any of "ac", "dw"

    Returns {"status", "filter", "reports", "error"}.
    """
    result = {"status": None, "filter": None, "reports": None, "error": None}

    for d in (start_date, end_date):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
            return _fail(result, f"Date must be YYYY-MM-DD, got {d!r}")
    if datetime.strptime(start_date, "%Y-%m-%d") > datetime.strptime(end_date, "%Y-%m-%d"):
        return _fail(result, "start_date is after end_date")
    reports = [r.lower() for r in reports]
    if not reports or any(r not in ("ac", "dw") for r in reports):
        return _fail(result, f"reports must be 'ac' and/or 'dw', got {reports}")

    # 1-2. Check new inputs before touching anything.
    new_files = None
    if tickets_folder:
        new_files, err = _check_tickets_folder(Path(tickets_folder))
        if err:
            return _fail(result, err)
    if roster_file:
        err = _check_roster(Path(roster_file))
        if err:
            return _fail(result, err)

    if new_files:
        for old in SOURCE_DIR.glob("Tickets_*.csv"):
            old.unlink()
        SOURCE_DIR.mkdir(parents=True, exist_ok=True)
        for f in new_files:
            shutil.copy2(f, SOURCE_DIR / f.name)
        print(f"[1/4] Replaced tickets export with {len(new_files)} file(s) from {tickets_folder}", flush=True)
    else:
        print(f"[1/4] Reusing existing tickets export in {SOURCE_DIR}", flush=True)

    if roster_file:
        ROSTER_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(roster_file, ROSTER_PATH)
        print(f"      Replaced Roster with {roster_file}", flush=True)
    err = _check_roster(ROSTER_PATH)
    if err:
        return _fail(result, err)

    # 3. Roster filter.
    print("[2/4] Running Tickets Roster Filter...", flush=True)
    try:
        full = filter_tickets_by_roster()
        short = filter_tickets_short()
    except PermissionError as e:
        return _fail(result, f"Cannot write {e.filename} -- close it in Excel and run again")
    result["filter"] = {"full": full, "short": short}
    if full["status"] != "COMPLETE" or short["status"] != "COMPLETE":
        return _fail(result, "Tickets Roster Filter did not complete")

    # 4. Refresh the report input snapshot.
    stray = [p.name for p in FRESH_INPUT.glob("*.csv") if p.name != SHORT_CSV.name]
    if stray:
        return _fail(
            result,
            f"fresh_ac_report/input/ has other .csv files that would be merged in: {stray}",
        )
    FRESH_INPUT.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(SHORT_CSV, FRESH_INPUT / SHORT_CSV.name)
    except PermissionError as e:
        return _fail(result, f"Cannot write {e.filename} -- close it in Excel and run again")
    print("[3/4] Copied filtered data into fresh_ac_report/input/", flush=True)

    # 5. Reports.
    print(f"[4/4] Generating {', '.join(r.upper() for r in reports)} report(s)...", flush=True)
    proc = subprocess.run(
        [sys.executable, "run_reports.py", "--start", start_date, "--end", end_date,
         "--roster", str(ROSTER_PATH), "--reports", *reports],
        cwd=FRESH_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    print(proc.stdout, flush=True)
    line = next((l for l in reversed(proc.stdout.splitlines()) if l.startswith("RESULT_JSON: ")), None)
    if line is None:
        if "PermissionError" in proc.stderr:
            return _fail(result, "Cannot write a report file -- close the AC/DW Fresh Report in Excel and run again")
        return _fail(result, f"Report generation crashed:\n{proc.stderr[-2000:]}")
    result["reports"] = json.loads(line[len("RESULT_JSON: "):])
    if proc.returncode != 0:
        return _fail(result, "Report validation failed -- do not use the output files")

    result["status"] = "COMPLETE"
    print("\nFresh pipeline COMPLETE", flush=True)
    for key, r in result["reports"].items():
        print(f"  {key.upper()}: {r['output_path']}", flush=True)
    return result
