#!/usr/bin/env python3
"""
ACT-01  下載 Power BI 原始報表

職責：連上已人工登入的 Edge（除錯 port），逐日、逐報表匯出原始 .xlsx 到
      data/raw/<報表名稱>/<前綴>_YYYY-MM-DD.xlsx。不修正、不合併（見 ACT-03～05）。
      已存在且非空的檔案預設跳過（R-008）。單一檔案失敗不中斷整批，記錄後繼續。

文件對應：sources.md A S-01、R-001～R-003、R-008、R-009、
          F-001～F-003
輸入：--start --end [--reports ...] [--force]
輸出：<workdir>/fetch_result.json（expected / downloaded / skipped / failed）
結束碼：0 全部到齊   1 連不上瀏覽器（未登入）   2 有檔案下載失敗（可重試）

用法：python pbi_fetch.py --workdir <dir> --start 2026-09-21 --end 2026-09-30
"""
import argparse

import _bootstrap  # noqa: F401
import pbi_browser
from opbrain import paths
from opbrain.common import InputError, add_workdir, parse_date_arg, run, write_json
from pbi_common import add_range_args, cfg, daterange, raw_dir, report_keys


def _connect(port):
    from playwright.sync_api import sync_playwright
    p = sync_playwright().start()
    try:
        browser = p.chromium.connect_over_cdp(f"http://localhost:{port}")
        context = browser.contexts[0]
        page = context.pages[0]
        cdp = context.new_cdp_session(page)
    except Exception as e:
        p.stop()
        raise InputError(
            f"Could not connect to the Power BI browser session on port {port}. "
            "Run pbi_open_browser.py (or launch Edge with --remote-debugging-port) and log into "
            "Power BI manually (including MFA) first."
        ) from e
    return p, page, cdp


def main() -> int:
    ap = argparse.ArgumentParser(description="下載 Power BI 原始報表")
    add_workdir(ap)
    add_range_args(ap)
    ap.add_argument("--force", action="store_true", help="已存在的檔案也重新下載")
    args = ap.parse_args()

    c = cfg()
    pbi_browser.DOWNLOAD_TIMEOUT_SECONDS = c["download_timeout_seconds"]
    keys = report_keys(args.reports)
    dates = list(daterange(parse_date_arg(args.start), parse_date_arg(args.end)))

    todo = []
    skipped = 0
    for d in dates:
        for k in keys:
            spec = c["reports"][k]
            dest = raw_dir(spec) / f"{spec['raw_prefix']}_{d.isoformat()}.xlsx"
            if not args.force and dest.exists() and dest.stat().st_size > 0:  # R-008
                skipped += 1
            else:
                todo.append((d, k))

    downloaded, failed = 0, []
    if todo:
        p, page, cdp = _connect(c["remote_debugging_port"])
        try:
            for d, k in todo:
                spec = c["reports"][k]
                try:
                    pbi_browser.export_one(page, cdp, f"{d.year}/{d.month}/{d.day}",
                                           spec["display_name"], spec["raw_prefix"], paths.RAW)
                    downloaded += 1
                except Exception as e:
                    failed.append({"date": d.isoformat(), "report": spec["display_name"], "error": str(e)})
        finally:
            p.stop()

    result = {"start_date": args.start, "end_date": args.end,
              "expected": len(dates) * len(keys), "downloaded": downloaded,
              "skipped": skipped, "failed": failed}
    write_json(args.workdir / "fetch_result.json", result)

    print(f"PBI Download: expected {result['expected']}, downloaded {downloaded}, "
          f"skipped {skipped}, failed {len(failed)}")
    for f in failed:
        print(f"  FAILED {f['date']} | {f['report']}: {f['error']}")
    return 2 if failed else 0


if __name__ == "__main__":
    run(main)
