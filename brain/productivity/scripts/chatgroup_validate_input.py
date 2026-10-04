#!/usr/bin/env python3
"""
ACT-20  檢查 Lark Chatgroup 來源檔與 Roster

職責：確認 Group Management.xlsx 存在；每個要求的 target（ac / dw）需要的工作表都在，
      且每張表都找得到 Date 與 OP 姓名欄（R-061、R-062）；Roster 有 Lark Name 與正式姓名欄
      （team-structure:R-002、R-004）。任一不合格 → 全部不產出。

文件對應：flows/chatgroup.md（輸入）V-030
輸入：--start --end [--targets ac dw]
輸出：<workdir>/chatgroup_input_check.json
結束碼：0 通過   1 參數錯誤   2 不合格（關卡）

用法：python chatgroup_validate_input.py --workdir <dir> --start 2026-09-01 --end 2026-09-30
"""
import argparse

import _bootstrap  # noqa: F401
from chatgroup_common import cfg, header_columns, open_source, sheet_rows, sheets_for, source_path, target_keys
from opbrain import roster
from opbrain.common import GateError, InputError, add_workdir, parse_date_arg, run, write_json


def main() -> int:
    ap = argparse.ArgumentParser(description="檢查 Lark Chatgroup 來源檔")
    add_workdir(ap)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--targets", nargs="*", default=None)
    args = ap.parse_args()
    parse_date_arg(args.start), parse_date_arg(args.end)
    keys = target_keys(args.targets)

    try:
        wb = open_source()
    except InputError as e:
        raise GateError(f"V-030 {e}")
    errors, plan = [], {}
    for k in keys:
        spec = cfg()["targets"][k]
        sheets = sheets_for(spec, wb.sheetnames)
        plan[k] = sheets
        for s in sheets:
            if s not in wb.sheetnames:
                errors.append(f"{k}: sheet '{s}' not found")
                continue
            header = next(sheet_rows(wb[s]), None)
            date_col, _, op_col = header_columns(header or (), spec)
            if date_col is None or op_col is None:
                errors.append(f"{k}: sheet '{s}' has no Date/OP-name column")
    wb.close()
    try:
        lark_map = roster.lark_to_op_map()
    except InputError as e:
        errors.append(f"roster: {e}")
        lark_map = {}

    write_json(args.workdir / "chatgroup_input_check.json",
               {"start_date": args.start, "end_date": args.end, "source": str(source_path()),
                "targets": plan, "roster_lark_names": len(lark_map), "errors": errors})
    for k, sheets in plan.items():
        print(f"{k}: {len(sheets)} sheet(s)")
    if errors:
        raise GateError("V-030 " + "; ".join(errors))
    return 0


if __name__ == "__main__":
    run(main)
