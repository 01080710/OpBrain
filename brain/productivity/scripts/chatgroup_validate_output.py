#!/usr/bin/env python3
"""
ACT-24  驗證 Chatgroup Volumn 檔

職責：重新開啟寫出的檔案，檢查（V-031～V-034）：表頭正確、列數與處理結果一致、
      日期都在區間內、OP Name 不空白、Roster Status 只有空白或「Inactive from Roster」。

文件對應：sources.md C V-031～V-034
輸入：<workdir>/chatgroup_outputs.json（ACT-23）、chatgroup_final_<target>.pkl
輸出：<workdir>/chatgroup_validation.json
結束碼：0 全部通過   1 前一步輸出不存在   2 驗證未通過（關卡）

用法：python chatgroup_validate_output.py --workdir <dir>
"""
import argparse
from datetime import date as _date, datetime

import openpyxl

import _bootstrap  # noqa: F401
from chatgroup_common import cfg
from opbrain.common import add_workdir, load_obj, read_json, require, run, write_json


def main() -> int:
    ap = argparse.ArgumentParser(description="驗證 Chatgroup Volumn 檔")
    add_workdir(ap)
    args = ap.parse_args()

    check = read_json(require(args.workdir / "chatgroup_input_check.json", "先執行 ACT-20"))
    outputs = read_json(require(args.workdir / "chatgroup_outputs.json", "先執行 ACT-23"))
    start, end = _date.fromisoformat(check["start_date"]), _date.fromisoformat(check["end_date"])
    c = cfg()
    results, failed = {}, False
    for k, o in outputs.items():
        wb = openpyxl.load_workbook(o["output_path"], read_only=True)
        rows = list(wb.active.iter_rows(values_only=True))
        wb.close()
        expected = load_obj(args.workdir / f"chatgroup_final_{k}.pkl")
        problems = []
        if list(rows[0]) != c["output_columns"]:
            problems.append("V-031 header mismatch")
        if len(rows) - 1 != len(expected):
            problems.append(f"V-032 row count {len(rows) - 1} != {len(expected)}")
        for r in rows[1:]:
            d = r[0].date() if isinstance(r[0], datetime) else r[0]
            if not isinstance(d, _date) or not (start <= d <= end):
                problems.append("V-033 a date is outside the range")
                break
        if any(r[1] is None or str(r[1]).strip() == "" for r in rows[1:]):
            problems.append("V-033 blank OP Name")
        if any(r[4] not in (None, c["inactive_flag"]) for r in rows[1:]):
            problems.append("V-034 unexpected Roster Status value")
        results[k] = {"ok": not problems, "problems": problems}
        failed |= bool(problems)
        print(f"{k}: {'OK' if not problems else 'FAILED ' + '; '.join(problems)}")
    write_json(args.workdir / "chatgroup_validation.json", results)
    return 2 if failed else 0


if __name__ == "__main__":
    run(main)
