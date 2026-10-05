#!/usr/bin/env python3
"""
ACT-04  合併 PBI 每日資料（依欄名對齊）

職責：以日期遞增順序把每天的資料列接在一起；A 欄填入該檔的 source_date（R-005）。
      欄位依「名稱」對齊（R-006）：標準欄位 = 最長的表頭；某天少欄位時補空值；
      有多出或順序不同的欄位 = 結構錯誤，整份報表不產出。

文件對應：sources.md A（清理與合併）R-005、R-006、R-007
輸入：<workdir>/pbi_clean_<報表>.pkl（ACT-03）
輸出：<workdir>/pbi_processed_<報表>.pkl  {"header": [...], "rows": [...]}；
      <workdir>/pbi_process.json（各報表 rows / schema_errors）
結束碼：0 成功   1 前一步輸出不存在   2 有結構錯誤（關卡）

用法：python pbi_process.py --workdir <dir>
"""
import argparse

import _bootstrap  # noqa: F401
from opbrain.common import add_workdir, load_obj, read_json, require, run, save_obj, write_json
from pbi_common import cfg


def build_column_mapping(file_header, canonical_header):
    """file_header 必須是 canonical_header 的同順序子集；否則 ValueError。"""
    mapping, file_idx = [], 0
    for canon_col in canonical_header:
        if file_idx < len(file_header) and file_header[file_idx] == canon_col:
            mapping.append(file_idx)
            file_idx += 1
        else:
            mapping.append(None)
    if file_idx != len(file_header):
        raise ValueError("file_header is not a same-order subset of canonical_header")
    return mapping


def main() -> int:
    ap = argparse.ArgumentParser(description="合併 PBI 每日資料")
    add_workdir(ap)
    args = ap.parse_args()

    check = read_json(require(args.workdir / "pbi_input_check.json", "先執行 ACT-02"))
    summary, blocked = {}, False
    for k in check["reports"]:
        cleaned = load_obj(args.workdir / f"pbi_clean_{k}.pkl")
        dates = sorted(cleaned)
        headers = {d: cleaned[d][0] for d in dates}

        max_len = max(len(h) for h in headers.values())
        canonical = next(headers[d] for d in dates if len(headers[d]) == max_len)

        rows, schema_errors = [], []
        for d in dates:
            header, data = cleaned[d]
            if header == canonical:
                mapping = list(range(len(canonical)))
            else:
                try:
                    mapping = build_column_mapping(header, canonical)
                except ValueError:
                    schema_errors.append({"date": d.isoformat(), "expected_columns": canonical,
                                          "found_columns": header})
                    continue
            for row in data:
                row_wo_a = row[1:]
                rows.append([d] + [row_wo_a[i] if i is not None else None for i in mapping])

        name = cfg()["reports"][k]["display_name"]
        summary[k] = {"report": name, "rows": len(rows), "schema_errors": schema_errors}
        if schema_errors:
            blocked = True
            print(f"{name}: SCHEMA ERRORS")
            for e in schema_errors:
                print(f"  {e['date']}: expected {e['expected_columns']}, found {e['found_columns']}")
        else:
            save_obj(args.workdir / f"pbi_processed_{k}.pkl", {"header": [None] + list(canonical), "rows": rows})
            print(f"{name}: {len(rows)} row(s)")

    write_json(args.workdir / "pbi_process.json", summary)
    return 2 if blocked else 0


if __name__ == "__main__":
    run(main)
