#!/usr/bin/env python3
"""
ACT-01  檢查 Roster 健康狀況

職責：在其他 Skill 使用 Roster 之前，先找出會讓比對出錯的問題：
      正式姓名欄是否存在且在第一欄（R-002）、空白姓名列（R-003）、重複姓名、
      只有一個字的姓名（子字串比對時容易誤中別人，V-003）、Lark Name 重複或缺漏（R-004）。
      並列出各標籤（Team / Office / superior …）的人數分布。

文件對應：flows/check.md V-001～V-005、rules.md R-001～R-005
輸入：[--roster <檔案>]（預設 data/raw/roster/Roster.xlsx）
輸出：<workdir>/roster_check.json
結束碼：0 通過（可能有警告）   1 檔案不存在   2 有阻擋性問題（缺正式姓名欄、重複姓名）

用法：python roster_check.py --workdir <dir>
"""
import argparse
from collections import Counter
from pathlib import Path

import pandas as pd

import _bootstrap  # noqa: F401
from opbrain import config, roster
from opbrain.common import GateError, add_workdir, run, write_json


def main() -> int:
    ap = argparse.ArgumentParser(description="檢查 Roster 健康狀況")
    add_workdir(ap)
    ap.add_argument("--roster", type=Path, default=None)
    args = ap.parse_args()
    path = args.roster or roster.default_path()
    cfg = config.load("team-structure", "roster")

    df = pd.read_excel(path, dtype=str)
    op_col = next((c for c in df.columns if str(c).strip().lower() in
                   [h.lower() for h in cfg["op_name_headers"]]), None)
    blockers, warnings = [], []
    if op_col is None:
        raise GateError(f"V-001 no name column {cfg['op_name_headers']} in {path}")
    if df.columns[0] != op_col:
        warnings.append(f"V-001 name column '{op_col}' is not the first column (reports read the first column)")

    names = df[op_col].fillna("").str.strip()
    blank = df[names == ""]
    if len(blank):
        warnings.append(f"V-002 {len(blank)} row(s) with a blank name (skipped by every Skill)")
    dup = [n for n, c in Counter(names[names != ""]).items() if c > 1]
    if dup:
        blockers.append(f"V-004 duplicate names: {dup}")
    single = [n for n in names if n and len(n.split()) == 1]
    if single:
        warnings.append(f"V-003 single-word names (may match other people by substring): {single}")
    lark_col = next((c for c in df.columns if str(c).strip().lower() in
                     [h.lower() for h in cfg["lark_name_headers"]]), None)
    if lark_col:
        lark = df[lark_col].fillna("").str.strip()
        no_lark = names[(lark == "") & (names != "")].tolist()
        if no_lark:
            warnings.append(f"V-005 no Lark Name (Chatgroup cannot map them): {no_lark}")
        ldup = [n for n, c in Counter(lark[lark != ""]).items() if c > 1]
        if ldup:
            warnings.append(f"V-005 duplicate Lark Names (first one wins): {ldup}")

    tags = {c: df[c].fillna("(blank)").value_counts().to_dict()
            for c in df.columns if c not in (op_col, lark_col) and df[c].nunique() <= 30}
    result = {"roster": str(path), "name_column": op_col, "people": int((names != "").sum()),
              "blockers": blockers, "warnings": warnings, "tag_distribution": tags}
    write_json(args.workdir / "roster_check.json", result)

    print(f"Roster: {result['people']} people, name column '{op_col}'")
    for w in warnings:
        print(f"  WARN {w}")
    for b in blockers:
        print(f"  BLOCK {b}")
    for c, dist in tags.items():
        print(f"  {c}: " + ", ".join(f"{k} {v}" for k, v in dist.items()))
    if blockers:
        raise GateError("; ".join(blockers))
    return 0


if __name__ == "__main__":
    run(main)
