#!/usr/bin/env python3
"""
ACT-06  驗證 PBI 合併檔

職責：重新開啟寫出的檔案，確認：表頭與處理結果一致（V-002）、列數一致（V-003）、
      A 欄每列都是區間內的日期且依日期遞增（V-004）、每天都有資料（V-005）。

文件對應：sources.md A V-002～V-005
輸入：<workdir>/pbi_outputs.json（ACT-05）、pbi_processed_<報表>.pkl
輸出：<workdir>/pbi_validation.json
結束碼：0 全部通過   1 前一步輸出不存在   2 驗證未通過（關卡）

用法：python pbi_validate_output.py --workdir <dir>
"""
import argparse
from datetime import date as _date, datetime

import openpyxl

import _bootstrap  # noqa: F401
from opbrain.common import add_workdir, load_obj, read_json, require, run, write_json


def _as_date(v):
    return v.date() if isinstance(v, datetime) else v


def main() -> int:
    ap = argparse.ArgumentParser(description="驗證 PBI 合併檔")
    add_workdir(ap)
    args = ap.parse_args()

    check = read_json(require(args.workdir / "pbi_input_check.json", "先執行 ACT-02"))
    outputs = read_json(require(args.workdir / "pbi_outputs.json", "先執行 ACT-05"))
    start, end = _date.fromisoformat(check["start_date"]), _date.fromisoformat(check["end_date"])
    expected_days = (end - start).days + 1

    results, failed = {}, False
    for k, o in outputs.items():
        data = load_obj(args.workdir / f"pbi_processed_{k}.pkl")
        wb = openpyxl.load_workbook(o["output_path"], read_only=True)
        rows = list(wb.active.iter_rows(values_only=True))
        wb.close()
        problems = []
        if list(rows[0]) != list(data["header"]):
            problems.append("V-002 header differs from processed header")
        if len(rows) - 1 != len(data["rows"]):
            problems.append(f"V-003 row count {len(rows) - 1} != {len(data['rows'])}")
        dates = [_as_date(r[0]) for r in rows[1:]]
        if any(not isinstance(d, _date) or not (start <= d <= end) for d in dates):
            problems.append("V-004 column A has a value outside the date range")
        elif dates != sorted(dates):
            problems.append("V-004 rows are not in ascending date order")
        if len(set(dates)) != expected_days:
            problems.append(f"V-005 {len(set(dates))} distinct day(s), expected {expected_days}")
        results[k] = {"report": o["report"], "ok": not problems, "problems": problems}
        failed |= bool(problems)
        print(f"{o['report']}: {'OK' if not problems else 'FAILED'}")
        for p in problems:
            print(f"  {p}")

    write_json(args.workdir / "pbi_validation.json", results)
    return 2 if failed else 0


if __name__ == "__main__":
    run(main)
