#!/usr/bin/env python3
"""
ACT-23  寫出 Chatgroup Volumn 檔

職責：每個 target 寫一個 Excel 到 data/COMBINE/，工作表名 = 顯示名稱，
      欄位 Date / OP Name / Group Name / Source / Roster Status，日期格式 yyyy/mm/dd（R-065）。

文件對應：sources.md C、flows/ac.md、flows/dw.md（輸出）R-065
輸入：<workdir>/chatgroup_final_<target>.pkl（ACT-22）
輸出：data/COMBINE/<AC|DW> Chatgroup Volumn <start> to <end>.xlsx；<workdir>/chatgroup_outputs.json
結束碼：0 成功   1 前一步輸出不存在 / 檔案被 Excel 開著

用法：python chatgroup_build_output.py --workdir <dir>
"""
import argparse

import openpyxl

import _bootstrap  # noqa: F401
from chatgroup_common import cfg
from opbrain import paths
from opbrain.common import add_workdir, load_obj, read_json, require, run, write_json


def main() -> int:
    ap = argparse.ArgumentParser(description="寫出 Chatgroup Volumn 檔")
    add_workdir(ap)
    args = ap.parse_args()

    check = read_json(require(args.workdir / "chatgroup_input_check.json", "先執行 ACT-20"))
    c = cfg()
    outputs = {}
    for k in check["targets"]:
        spec = c["targets"][k]
        rows = load_obj(args.workdir / f"chatgroup_final_{k}.pkl")
        out = paths.COMBINE / spec["output_name_template"].format(start=check["start_date"], end=check["end_date"])
        out.parent.mkdir(parents=True, exist_ok=True)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = spec["display_name"]
        ws.append(c["output_columns"])
        for r in rows:
            ws.append(list(r))
        for i in range(2, len(rows) + 2):
            ws.cell(row=i, column=1).number_format = c["output_date_format"]
        wb.save(out)
        wb.close()
        outputs[k] = {"output_path": str(out), "rows": len(rows)}
        print(f"{spec['display_name']}: {out}")
    write_json(args.workdir / "chatgroup_outputs.json", outputs)
    return 0


if __name__ == "__main__":
    run(main)
