"""
PBI end-to-end pipeline: login -> download (auto-retry failures) ->
verify completeness -> combine.

Ties together, unmodified:
  - src/collectors/pbi_login.py     (ensure_logged_in)
  - src/collectors/pbi_collector.py (download_date_range)
  - src/processors/pbi_combiner.py  (combine_date_range)

This is the single entry point meant to be handed to someone else to
run end-to-end: they run it, a browser window opens for them to log
into manually, and everything else (download retries, completeness
check, combine) happens automatically.

Download Tool and Combine Tool remain independent and unmodified --
this module only calls their existing official entry points and
translates between the two naming conventions they each already use
(download wants report display names, combine wants report keys).
"""

import sys

from src.collectors.pbi_login import ensure_logged_in
from src.collectors.pbi_collector import download_date_range
from src.processors.pbi_combiner import combine_date_range, REPORT_SPECS

MAX_DOWNLOAD_ATTEMPTS = 3


def _report_keys_to_display_names(keys):
    return [REPORT_SPECS[k]["display_name"] for k in keys]


def run_pbi_pipeline(start_date: str, end_date: str, reports=None) -> dict:
    """
    Args:
        start_date, end_date: "YYYY-MM-DD", inclusive
        reports: list of report keys ("op_workload_p1", "op_workload_p2",
            "wd_wl_by_group"); None = all 3

    Returns {"download": <download_date_range result>,
             "combine": <combine_date_range result> or None if Combine
             was skipped because Download never fully completed}.
    """
    for key in reports or []:
        if key not in REPORT_SPECS:
            raise ValueError(f"Unknown report '{key}'. Valid: {list(REPORT_SPECS)}")

    download_report_names = _report_keys_to_display_names(reports) if reports else None

    playwright, browser = ensure_logged_in()

    download_result = None
    for attempt in range(1, MAX_DOWNLOAD_ATTEMPTS + 1):
        print(f"\n=== Download attempt {attempt}/{MAX_DOWNLOAD_ATTEMPTS} ===", flush=True)
        download_result = download_date_range(
            start_date, end_date, reports=download_report_names, force=False
        )
        if not download_result["failed"]:
            break
        print(
            f"{len(download_result['failed'])} item(s) failed, "
            f"retrying just those on the next attempt...",
            flush=True,
        )

    if download_result["failed"]:
        print(
            "\nDownload did not fully complete after "
            f"{MAX_DOWNLOAD_ATTEMPTS} attempts. Skipping Combine.",
            flush=True,
        )
        return {"download": download_result, "combine": None}

    print("\n=== All requested raw files present. Running Combine. ===", flush=True)
    combine_result = combine_date_range(start_date, end_date, reports=reports)

    return {"download": download_result, "combine": combine_result}


if __name__ == "__main__":
    start = sys.argv[1]
    end = sys.argv[2]
    run_pbi_pipeline(start, end)
