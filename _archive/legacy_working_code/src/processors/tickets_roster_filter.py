"""
Tickets export + Roster tag filter.

Reads every "Tickets_*.csv" file from data/raw/tickets_export/ (a
paginated export -- e.g. Tickets_1.csv .. Tickets_15.csv -- the user
manually re-downloads and overwrites these files; there is no
automated download yet), concatenates them in numeric filename order,
and keeps only the rows whose "Tags" column contains at least one name
that also appears in data/raw/roster/Roster.xlsx's "OP Name" column.

"Tags" is a single comma-separated string mixing category codes (e.g.
"D1", "D1. Deposit Failure") with OP agent names, e.g.:
    "D1,D1. Deposit Failure,Andrew Chang,Aida Zaki,Tan Kian Chung"
A row is kept if ANY comma-separated piece, after stripping
whitespace, EXACTLY matches a Roster OP Name (not a substring check --
tag pieces like "D1. Deposit Failure" should never accidentally match
a name).

No date filtering, no deduplication of Ticket Id across the 15 files
-- neither was requested. All original columns are kept as-is in the
output; nothing is renamed or reordered.

Output: one CSV file under data/COMBINE/.
"""

import re
from pathlib import Path

import openpyxl
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "data" / "raw" / "tickets_export"
ROSTER_PATH = PROJECT_ROOT / "data" / "raw" / "roster" / "Roster.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "data" / "COMBINE"

MAX_COL_BOUND = 30
MAX_ROW_BOUND = 200000

TAGS_COLUMN = "Tags"


def _find_col(header_row, *candidates):
    normalized = {}
    for i, h in enumerate(header_row):
        if h is None:
            continue
        normalized.setdefault(str(h).strip().lower(), i)
    for cand in candidates:
        idx = normalized.get(cand.strip().lower())
        if idx is not None:
            return idx
    return None


def _load_roster_op_names(roster_path: Path) -> set:
    if not roster_path.exists():
        raise RuntimeError(f"Roster file not found: {roster_path}")

    wb = openpyxl.load_workbook(roster_path, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = ws.iter_rows(
        min_row=1, max_row=MAX_ROW_BOUND, min_col=1, max_col=MAX_COL_BOUND, values_only=True
    )
    header_row = next(rows, None)
    if header_row is None:
        wb.close()
        raise RuntimeError(f"Roster file has no header row: {roster_path}")

    op_col = _find_col(header_row, "OP Name", "CRM OP Name")
    if op_col is None:
        wb.close()
        raise RuntimeError(f"Roster file is missing 'OP Name' column: {roster_path}")

    names = set()
    for row in rows:
        v = row[op_col] if op_col < len(row) else None
        if v is not None and str(v).strip():
            names.add(str(v).strip())
    wb.close()
    return names


def _natural_file_sort_key(path: Path):
    m = re.search(r"(\d+)", path.stem)
    return (int(m.group(1)) if m else 0, path.stem)


def _load_filtered_tickets():
    """
    Reads all Tickets_*.csv, concatenates them, and returns
    (kept_dataframe, result_dict, error). result_dict always has
    source_files_found/rows_scanned filled in; kept_dataframe/error are
    None on failure (check error first).
    """
    result = {"source_files_found": 0, "rows_scanned": 0}

    if not SOURCE_DIR.exists():
        return None, result, f"Source folder not found: {SOURCE_DIR}"

    files = sorted(SOURCE_DIR.glob("Tickets_*.csv"), key=_natural_file_sort_key)
    if not files:
        return None, result, f"No Tickets_*.csv files found in {SOURCE_DIR}"
    result["source_files_found"] = len(files)

    try:
        roster_names = _load_roster_op_names(ROSTER_PATH)
    except RuntimeError as e:
        return None, result, str(e)

    ref_columns = None
    frames = []
    for f in files:
        df = pd.read_csv(f, dtype=str, keep_default_na=False)
        if ref_columns is None:
            ref_columns = df.columns.tolist()
        elif df.columns.tolist() != ref_columns:
            return None, result, (
                f"{f.name} has different columns than {files[0].name}: "
                f"{df.columns.tolist()} vs {ref_columns}"
            )
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    result["rows_scanned"] = len(combined)

    if TAGS_COLUMN not in combined.columns:
        return None, result, f"'{TAGS_COLUMN}' column not found in source files"

    # Case-insensitive, as documented. Zero-width spaces are stripped too:
    # the source system sometimes stores a tag as "​Martin Lin".
    roster_names_lower = {n.lower() for n in roster_names}

    def _row_has_roster_name(tags_value):
        if not tags_value:
            return False
        parts = [p.replace("​", "").strip().lower() for p in str(tags_value).split(",")]
        return any(p in roster_names_lower for p in parts)

    mask = combined[TAGS_COLUMN].apply(_row_has_roster_name)
    kept = combined[mask]
    return kept, result, None


def filter_tickets_by_roster(output_name: str = "Tickets Roster Tagged.csv") -> dict:
    """
    Official entry point.

    Returns a summary dict: source_files_found, rows_scanned, rows_kept,
    output_path, status ("COMPLETE" / "FAILED"). Prints a human-readable
    summary. Writes the output file only if status is COMPLETE.
    """
    kept, result, error = _load_filtered_tickets()
    result["output_path"] = None
    result["status"] = "FAILED"
    if error:
        result["rows_kept"] = 0
        _print_summary(result, error=error)
        return result

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_name
    kept.to_csv(output_path, index=False, encoding="utf-8-sig")

    result["rows_kept"] = len(kept)
    result["output_path"] = str(output_path)
    result["status"] = "COMPLETE"
    _print_summary(result)
    return result


def filter_tickets_short(output_name: str = "Tickets Roster Tagged Short.csv") -> dict:
    """
    Same filter as filter_tickets_by_roster(), but the output only has
    3 columns: Created Time (date-only, "YYYY/MM/DD"), Group, Tags.
    """
    kept, result, error = _load_filtered_tickets()
    result["output_path"] = None
    result["status"] = "FAILED"
    if error:
        result["rows_kept"] = 0
        _print_summary(result, error=error)
        return result

    short = kept[["Created Time", "Group", TAGS_COLUMN]].copy()
    short["Created Time"] = (
        pd.to_datetime(short["Created Time"]).dt.strftime("%Y/%m/%d")
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_name
    short.to_csv(output_path, index=False, encoding="utf-8-sig")

    result["rows_kept"] = len(short)
    result["output_path"] = str(output_path)
    result["status"] = "COMPLETE"
    _print_summary(result)
    return result


def _print_summary(result, error=None):
    print("Tickets Roster Filter Completed")
    print()
    print(f"Source files found: {result['source_files_found']}")
    print(f"Rows scanned: {result['rows_scanned']}")
    print(f"Rows kept (Tags matched a Roster OP Name): {result['rows_kept']}")
    if error:
        print(f"Error: {error}")
    print(f"Status: {result['status']}")
    if result["output_path"]:
        print()
        print("Output:")
        print(result["output_path"])
