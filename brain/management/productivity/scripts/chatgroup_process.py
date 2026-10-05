#!/usr/bin/env python3
"""
ACT-21  擷取區間內的 Chatgroup 紀錄

職責：依工作表順序、由上而下讀取每張表，只保留 Date 是日期且落在區間內、
      OP 姓名欄非空白的列（R-063）。Source = 工作表名稱。不做姓名轉換（見 ACT-22）。

文件對應：sources.md C R-061～R-063
輸入：<workdir>/chatgroup_input_check.json（ACT-20）
輸出：<workdir>/chatgroup_rows_<target>.pkl  [(date, op_name, group_name, source), ...]
結束碼：0 成功   1 前一步輸出不存在

用法：python chatgroup_process.py --workdir <dir>
"""
import argparse
from datetime import date as _date, datetime

import _bootstrap  # noqa: F401
from chatgroup_common import cfg, header_columns, open_source, sheet_rows
from opbrain.common import add_workdir, read_json, require, run, save_obj


def main() -> int:
    ap = argparse.ArgumentParser(description="擷取區間內的 Chatgroup 紀錄")
    add_workdir(ap)
    args = ap.parse_args()

    check = read_json(require(args.workdir / "chatgroup_input_check.json", "先執行 ACT-20"))
    start, end = _date.fromisoformat(check["start_date"]), _date.fromisoformat(check["end_date"])
    wb = open_source()
    for k, sheets in check["targets"].items():
        spec = cfg()["targets"][k]
        collected = []
        for s in sheets:
            rows = sheet_rows(wb[s])
            header = next(rows, None)
            date_col, group_col, op_col = header_columns(header, spec)
            for row in rows:
                raw_date = row[date_col] if date_col < len(row) else None
                if not isinstance(raw_date, (datetime, _date)):
                    continue
                d = raw_date.date() if isinstance(raw_date, datetime) else raw_date
                if not (start <= d <= end):
                    continue
                op_name = row[op_col] if op_col < len(row) else None
                if op_name is None or str(op_name).strip() == "":
                    continue
                group = row[group_col] if group_col is not None and group_col < len(row) else None
                collected.append((d, op_name, group, s))
        save_obj(args.workdir / f"chatgroup_rows_{k}.pkl", collected)
        print(f"{spec['display_name']}: {len(collected)} row(s) in range")
    wb.close()
    return 0


if __name__ == "__main__":
    run(main)
