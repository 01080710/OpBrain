#!/usr/bin/env python3
"""
ACT-05  寫出 PBI 合併檔

職責：每份報表寫一個 Excel 到 data/COMBINE/，檔名依 R-002 的範本與日期區間；
      工作表名 "Export"，表頭一列，A 欄日期格式 mm-dd-yy（與使用者參考檔一致）。

文件對應：sources.md A（輸出）R-002
輸入：<workdir>/pbi_input_check.json、pbi_processed_<報表>.pkl（ACT-04）
輸出：data/COMBINE/COMBINE-<報表>_<start> to <end>.xlsx；<workdir>/pbi_outputs.json
結束碼：0 成功   1 前一步輸出不存在 / 檔案被 Excel 開著

用法：python pbi_build_output.py --workdir <dir>
"""
import argparse

import openpyxl

import _bootstrap  # noqa: F401
from opbrain import paths
from opbrain.common import add_workdir, load_obj, read_json, require, run, write_json
from pbi_common import cfg


def main() -> int:
    ap = argparse.ArgumentParser(description="寫出 PBI 合併檔")
    add_workdir(ap)
    args = ap.parse_args()

    check = read_json(require(args.workdir / "pbi_input_check.json", "先執行 ACT-02"))
    start, end = check["start_date"], check["end_date"]
    outputs = {}
    for k in check["reports"]:
        spec = cfg()["reports"][k]
        data = load_obj(args.workdir / f"pbi_processed_{k}.pkl")
        out = paths.COMBINE / spec["output_name_template"].format(start=start, end=end)
        out.parent.mkdir(parents=True, exist_ok=True)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Export"
        ws.append(data["header"])
        for row in data["rows"]:
            ws.append(row)
        for r in range(2, len(data["rows"]) + 2):
            ws.cell(row=r, column=1).number_format = "mm-dd-yy"
        wb.save(out)
        wb.close()

        outputs[k] = {"report": spec["display_name"], "output_path": str(out), "rows": len(data["rows"])}
        print(f"{spec['display_name']}: {out}")

    write_json(args.workdir / "pbi_outputs.json", outputs)
    return 0


if __name__ == "__main__":
    run(main)
