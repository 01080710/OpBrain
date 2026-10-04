#!/usr/bin/env python3
"""
ACT-12  彙總並依 Roster 篩選 Tickets

職責：把所有來源檔依序接在一起，只保留 Tags 有任一段（逗號切開、去空白、去零寬字元、
      不分大小寫）完全等於某個 Roster 正式姓名的列（R-021，不用子字串比對，避免類別代碼誤中人名）。
      不去重、不篩日期（R-022）。輸出全欄版與精簡版兩個 CSV（R-023）。

文件對應：sources.md B（清理）R-021～R-023
輸入：<workdir>/tickets_input_check.json（ACT-11）
輸出：data/COMBINE/Tickets Roster Tagged.csv、Tickets Roster Tagged Short.csv；<workdir>/tickets_clean.json
結束碼：0 成功   1 前一步輸出不存在 / 檔案被 Excel 開著

用法：python tickets_clean.py --workdir <dir>
"""
import argparse
from pathlib import Path

import pandas as pd

import _bootstrap  # noqa: F401
from fresh_common import tickets_cfg
from opbrain import paths, roster
from opbrain.common import add_workdir, read_json, require, run, write_json


def main() -> int:
    ap = argparse.ArgumentParser(description="彙總並依 Roster 篩選 Tickets")
    add_workdir(ap)
    args = ap.parse_args()

    check = read_json(require(args.workdir / "tickets_input_check.json", "先執行 ACT-11"))
    c = tickets_cfg()
    combined = pd.concat([pd.read_csv(f, dtype=str, keep_default_na=False) for f in check["files"]],
                         ignore_index=True)

    names_lower = {n.lower() for n in roster.op_name_set()}
    zw = c["zero_width_chars"]

    def has_roster_name(tags):
        if not tags:
            return False
        parts = []
        for p in str(tags).split(","):
            for ch in zw:
                p = p.replace(ch, "")
            parts.append(p.strip().lower())
        return any(p in names_lower for p in parts)

    kept = combined[combined[c["tags_column"]].apply(has_roster_name)]

    paths.COMBINE.mkdir(parents=True, exist_ok=True)
    full_path = paths.COMBINE / c["full_output_name"]
    kept.to_csv(full_path, index=False, encoding="utf-8-sig")

    short = kept[c["short_columns"]].copy()
    short["Created Time"] = pd.to_datetime(short["Created Time"]).dt.strftime(c["short_date_format"])
    short_path = paths.COMBINE / c["short_output_name"]
    short.to_csv(short_path, index=False, encoding="utf-8-sig")

    result = {"source_files_found": len(check["files"]), "rows_scanned": len(combined),
              "rows_kept": len(kept), "full_output": str(Path(full_path)), "short_output": str(short_path)}
    write_json(args.workdir / "tickets_clean.json", result)
    print(f"Rows scanned {len(combined)}, kept {len(kept)} "
          f"({len(kept) / max(len(combined), 1):.1%}) -> {full_path.name}, {short_path.name}")
    return 0


if __name__ == "__main__":
    run(main)
