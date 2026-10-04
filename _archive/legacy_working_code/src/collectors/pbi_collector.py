"""
Power BI report collector -- PBI Download Tool V1.

Downloads three Power BI reports (OP Workload P.1, OP Workload P.2,
WD WL by Group) for a given date range, via Playwright attached over
CDP to a Microsoft Edge session that has already been logged into
Power BI manually (MFA cannot be automated).

The interaction logic below (selectors, click strategy, date/hour
input handling, download detection) is copied unchanged from the
version validated across hundreds of real downloads during
development. Do not redesign or "clean up" this logic without
re-testing against a live Power BI session -- the specific choices
here (dispatch_event clicks, CDP Page.setDownloadBehavior, mtime-based
download detection, order-safe date range updates) were each arrived
at only after a failure mode that a more "obvious" approach did not
handle.

To start a browser session for this collector to attach to, launch
Microsoft Edge with a remote debugging port and log in manually:
    msedge --remote-debugging-port=9333 --user-data-dir=<temp dir>
then open the Power BI report URL and complete login + MFA by hand.
This module does not launch or log in a browser itself.
"""

import time
from datetime import date as _date, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

REMOTE_DEBUGGING_PORT = 9333
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = PROJECT_ROOT / "data" / "raw"
DOWNLOAD_TIMEOUT_SECONDS = 45

REPORTS = [
    ("OP Workload P.1", "OP_Workload_P1"),
    ("OP Workload P.2", "OP_Workload_P2"),
    ("WD WL by Group", "WD_WL_by_Group"),
]
REPORT_NAMES = [name for name, _ in REPORTS]
FILE_PREFIX_BY_REPORT = {name: prefix for name, prefix in REPORTS}


# ---------------------------------------------------------------------------
# Core interaction logic (validated; do not modify without re-testing)
# ---------------------------------------------------------------------------

def get_date_inputs(page):
    all_inputs = page.locator("input.date-slicer-datepicker").all()
    start_input = end_input = None
    for inp in all_inputs:
        label = inp.get_attribute("aria-label") or ""
        if "開始日期" in label:
            start_input = inp
        elif "結束日期" in label:
            end_input = inp
    return start_input, end_input


def set_input_value(input_locator, value_str):
    input_locator.fill(value_str)
    input_locator.press("Tab")


def parse_date(d):
    y, m, dd = d.split("/")
    return (int(y), int(m), int(dd))


def set_date_range(page, new_start, new_end):
    start_input, end_input = get_date_inputs(page)
    if start_input is None or end_input is None:
        raise RuntimeError("Could not locate start/end date inputs")

    current_start = start_input.input_value()
    current_end = end_input.input_value()
    cur_start_t, cur_end_t = parse_date(current_start), parse_date(current_end)
    new_start_t, new_end_t = parse_date(new_start), parse_date(new_end)

    if (current_start, current_end) == (new_start, new_end):
        return

    if new_start_t > cur_end_t:
        set_input_value(end_input, new_end)
        set_input_value(start_input, new_start)
    elif new_end_t < cur_start_t:
        set_input_value(start_input, new_start)
        set_input_value(end_input, new_end)
    else:
        set_input_value(start_input, new_start)
        set_input_value(end_input, new_end)

    page.wait_for_timeout(250)
    final_start = start_input.input_value()
    final_end = end_input.input_value()
    if parse_date(final_start) != new_start_t or parse_date(final_end) != new_end_t:
        raise RuntimeError(f"Date did not apply correctly: got {final_start}->{final_end}")


def get_hour_inputs(page):
    wrapper = page.locator(".visual-slicer").filter(has=page.locator("h3[title='hour']"))
    if wrapper.count() == 0:
        return None, None
    inputs = wrapper.locator("input.date-slicer-input")
    return inputs.nth(0), inputs.nth(1)


def set_hour_range(page):
    start_input, end_input = get_hour_inputs(page)
    if start_input is None:
        return

    current_start = start_input.input_value()
    current_end = end_input.input_value()
    if current_start == "0" and current_end == "24":
        return

    set_input_value(end_input, "24")
    set_input_value(start_input, "0")
    page.wait_for_timeout(250)

    final_start = start_input.input_value()
    final_end = end_input.input_value()
    if final_start != "0" or final_end != "24":
        raise RuntimeError(f"Hour did not apply correctly: got {final_start}-{final_end}")


def ensure_row_expanded(page):
    button = page.locator("div.expandCollapseButton").first
    if button.count() == 0:
        return
    icon = button.locator("i.glyphicon").first
    aria = icon.get_attribute("aria-label") if icon.count() > 0 else None
    if aria == "已展開":
        return
    button.dispatch_event("click")
    page.wait_for_timeout(250)


def find_visual_more_options(page):
    page.mouse.move(600, 350)
    page.wait_for_timeout(200)

    candidates = page.get_by_role("button", name="更多選項").all()
    target = None
    for b in candidates:
        box = b.bounding_box()
        if box and box["y"] > 150:
            target = b
    return target


def export_current_page(page, cdp, report_dir, filename):
    cdp.send("Page.setDownloadBehavior", {"behavior": "allow", "downloadPath": str(report_dir)})

    click_time = time.time()

    more_options = find_visual_more_options(page)
    if more_options is None:
        raise RuntimeError("Could not find the visual's '更多選項' button")
    more_options.dispatch_event("click")
    page.wait_for_timeout(250)

    export_item = page.get_by_role("menuitem", name="匯出資料")
    export_item.dispatch_event("click")
    page.wait_for_timeout(400)

    current_config_radio = page.get_by_role("radio", name="具有目前配置的資料")
    if current_config_radio.count() > 0 and not current_config_radio.is_checked():
        current_config_radio.dispatch_event("click")
        page.wait_for_timeout(200)

    export_btn = page.get_by_role("button", name="匯出", exact=True)
    export_btn.click()

    new_file = None
    deadline = time.monotonic() + DOWNLOAD_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        candidates = [
            f for f in report_dir.glob("*")
            if f.is_file()
            and f.stat().st_mtime > click_time
            and not f.name.endswith(".crdownload")
            and not f.name.startswith("~$")
            and f.name.lower().startswith("data")
        ]
        if candidates:
            candidate = max(candidates, key=lambda f: f.stat().st_mtime)
            size1 = candidate.stat().st_size
            time.sleep(0.4)
            size2 = candidate.stat().st_size
            if size1 == size2 and size1 > 0:
                new_file = candidate
                break
        time.sleep(0.2)

    if new_file is None:
        raise RuntimeError("No new file appeared in folder within timeout")

    dest_path = report_dir / filename
    if dest_path.exists():
        dest_path.unlink()

    last_err = None
    for _ in range(8):
        try:
            new_file.rename(dest_path)
            last_err = None
            break
        except PermissionError as e:
            last_err = e
            time.sleep(0.3)
    if last_err is not None:
        raise last_err

    return dest_path


def export_one(page, cdp, date_str, report_name, file_prefix):
    y, m, d = date_str.split("/")
    date_tag = f"{y}-{int(m):02d}-{int(d):02d}"

    report_dir = OUTPUT_ROOT / report_name
    report_dir.mkdir(parents=True, exist_ok=True)

    page.keyboard.press("Escape")
    page.wait_for_timeout(100)

    nav_item = page.get_by_text(report_name, exact=True).first
    nav_item.click()
    page.locator("input.date-slicer-datepicker").first.wait_for(state="attached", timeout=10000)
    page.wait_for_timeout(150)

    set_date_range(page, date_str, date_str)
    set_hour_range(page)
    ensure_row_expanded(page)

    filename = f"{file_prefix}_{date_tag}.xlsx"
    return export_current_page(page, cdp, report_dir, filename)


# ---------------------------------------------------------------------------
# Official entry point
# ---------------------------------------------------------------------------

def _slash_date(d: _date) -> str:
    return f"{d.year}/{d.month}/{d.day}"


def _date_tag(d: _date) -> str:
    return d.strftime("%Y-%m-%d")


def _daterange(start: _date, end: _date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def _is_valid_raw_file(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def _connect_page():
    p = sync_playwright().start()
    try:
        browser = p.chromium.connect_over_cdp(f"http://localhost:{REMOTE_DEBUGGING_PORT}")
        context = browser.contexts[0]
        page = context.pages[0]
        cdp = context.new_cdp_session(page)
    except Exception as e:
        p.stop()
        raise RuntimeError(
            "Could not connect to the Power BI browser session on port "
            f"{REMOTE_DEBUGGING_PORT}. Launch Edge with "
            f"--remote-debugging-port={REMOTE_DEBUGGING_PORT} and log into "
            "Power BI manually (including MFA) before calling download_date_range()."
        ) from e
    return p, page, cdp


def download_date_range(start_date: str, end_date: str, reports=None, force: bool = False) -> dict:
    """
    PBI Download Tool V1 -- official entry point.

    Args:
        start_date: "YYYY-MM-DD", inclusive.
        end_date: "YYYY-MM-DD", inclusive.
        reports: list of report display names to download
            (subset of REPORT_NAMES); None = all 3 reports.
        force: if False (default), a date/report combo whose raw file
            already exists and is non-empty is skipped rather than
            re-downloaded.

    Returns:
        dict with keys: start_date, end_date, expected, downloaded,
        skipped, failed (list of {"date", "report", "error"}).
        Also prints a human-readable summary before returning.
    """
    start = _date.fromisoformat(start_date)
    end = _date.fromisoformat(end_date)
    target_reports = reports if reports else REPORT_NAMES

    dates = list(_daterange(start, end))
    expected = len(dates) * len(target_reports)

    downloaded = 0
    skipped = 0
    failed = []

    p, page, cdp = _connect_page()
    try:
        for d in dates:
            for report_name in target_reports:
                prefix = FILE_PREFIX_BY_REPORT[report_name]
                report_dir = OUTPUT_ROOT / report_name
                report_dir.mkdir(parents=True, exist_ok=True)
                dest_path = report_dir / f"{prefix}_{_date_tag(d)}.xlsx"

                if not force and _is_valid_raw_file(dest_path):
                    skipped += 1
                    continue

                try:
                    export_one(page, cdp, _slash_date(d), report_name, prefix)
                    downloaded += 1
                except Exception as e:
                    failed.append({"date": _date_tag(d), "report": report_name, "error": str(e)})
    finally:
        p.stop()

    summary = {
        "start_date": start_date,
        "end_date": end_date,
        "expected": expected,
        "downloaded": downloaded,
        "skipped": skipped,
        "failed": failed,
    }
    _print_summary(summary)
    return summary


def _print_summary(summary: dict) -> None:
    print("PBI Download Completed")
    print()
    print("Date Range:")
    print(f"{summary['start_date']} -> {summary['end_date']}")
    print()
    print(f"Expected: {summary['expected']}")
    print(f"Downloaded: {summary['downloaded']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Failed: {len(summary['failed'])}")
    if summary["failed"]:
        print()
        print("Failed:")
        for item in summary["failed"]:
            print(f"{item['date']} | {item['report']}: {item['error']}")


def fetch():
    """
    Placeholder for the future daily-pipeline entry point (called by
    src/main.py). Not implemented in PBI Download Tool V1 -- use
    download_date_range() directly for now.
    """
    raise NotImplementedError("pbi_collector.fetch() is not implemented yet.")
