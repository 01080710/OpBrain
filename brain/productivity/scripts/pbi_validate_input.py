#!/usr/bin/env python3
"""
ACT-02  檢查 PBI 原始檔是否齊全

職責：對每份要求的報表，確認日期區間內每一天都有原始檔、檔名格式正確。
      缺任何一天 → 不往下做（不產出看似完整但缺資料的合併檔）。

文件對應：sources.md A R-003、R-007、V-001
輸入：--start --end [--reports ...]
輸出：<workdir>/pbi_input_check.json（每份報表：expected / found / missing / filename_errors / status）
結束碼：0 全部齊全   1 參數錯誤   2 有缺檔或檔名錯誤（關卡）

用法：python pbi_validate_input.py --workdir <dir> --start 2026-09-21 --end 2026-09-30
"""
import argparse

import _bootstrap  # noqa: F401
from opbrain.common import add_workdir, parse_date_arg, run, write_json
from pbi_common import add_range_args, cfg, daterange, report_keys, scan_raw_files


def main() -> int:
    ap = argparse.ArgumentParser(description="檢查 PBI 原始檔是否齊全")
    add_workdir(ap)
    add_range_args(ap)
    args = ap.parse_args()

    keys = report_keys(args.reports)
    dates = list(daterange(parse_date_arg(args.start), parse_date_arg(args.end)))
    out, blocked = {}, False
    for k in keys:
        spec = cfg()["reports"][k]
        by_date, filename_errors = scan_raw_files(spec)
        missing = [d.isoformat() for d in dates if d not in by_date]
        status = "INCOMPLETE" if missing else ("FAILED" if filename_errors else "OK")
        blocked |= status != "OK"
        out[k] = {"report": spec["display_name"], "expected": len(dates),
                  "found": len(dates) - len(missing), "missing": missing,
                  "filename_errors": filename_errors, "status": status,
                  "files": {d.isoformat(): str(by_date[d]) for d in dates if d in by_date}}
        print(f"{spec['display_name']}: {out[k]['found']}/{len(dates)} found, status {status}")
        for m in missing:
            print(f"  missing {m}")
        for f in filename_errors:
            print(f"  bad filename {f}")

    write_json(args.workdir / "pbi_input_check.json",
               {"start_date": args.start, "end_date": args.end, "reports": out})
    return 2 if blocked else 0


if __name__ == "__main__":
    run(main)
