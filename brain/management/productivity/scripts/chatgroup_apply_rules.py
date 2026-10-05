#!/usr/bin/env python3
"""
ACT-22  Lark 顯示名 → Roster 正式姓名

職責：OP 姓名（去前後空白、區分大小寫）若等於 Roster 的某個 Lark Name，
      換成該人的正式姓名、Roster Status 留空；對不到（通常是已離職）則保留原名、
      Roster Status 標「Inactive from Roster」，絕不刪除該列（R-064、DEC-003）。

文件對應：sources.md C R-064、team-structure:R-004
輸入：<workdir>/chatgroup_rows_<target>.pkl（ACT-21）
輸出：<workdir>/chatgroup_final_<target>.pkl；<workdir>/chatgroup_rules.json（matched / unmatched / 對不到的名字）
結束碼：0 成功   1 前一步輸出不存在 / Roster 不合格

用法：python chatgroup_apply_rules.py --workdir <dir>
"""
import argparse
from collections import Counter

import _bootstrap  # noqa: F401
from chatgroup_common import cfg
from opbrain import roster
from opbrain.common import add_workdir, load_obj, read_json, require, run, save_obj, write_json


def main() -> int:
    ap = argparse.ArgumentParser(description="Lark 顯示名轉 Roster 正式姓名")
    add_workdir(ap)
    args = ap.parse_args()

    check = read_json(require(args.workdir / "chatgroup_input_check.json", "先執行 ACT-20"))
    lark_map = roster.lark_to_op_map()
    flag = cfg()["inactive_flag"]
    summary = {}
    for k in check["targets"]:
        out, unmatched = [], Counter()
        for d, op_name, group, source in load_obj(args.workdir / f"chatgroup_rows_{k}.pkl"):
            key = str(op_name).strip() if op_name is not None else ""
            if key in lark_map:
                out.append((d, lark_map[key], group, source, None))
            else:
                out.append((d, op_name, group, source, flag))
                unmatched[str(op_name)] += 1
        save_obj(args.workdir / f"chatgroup_final_{k}.pkl", out)
        summary[k] = {"rows": len(out), "matched": len(out) - sum(unmatched.values()),
                      "unmatched": sum(unmatched.values()), "unmatched_names": dict(unmatched)}
        print(f"{k}: matched {summary[k]['matched']}, unmatched {summary[k]['unmatched']}"
              + (f" {dict(unmatched)}" if unmatched else ""))
    write_json(args.workdir / "chatgroup_rules.json", summary)
    return 0


if __name__ == "__main__":
    run(main)
