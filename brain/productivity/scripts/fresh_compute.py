#!/usr/bin/env python3
"""
ACT-13  計算 Fresh「日期 × 員工 × 模組」件數

職責：讀 Tickets 精簡版（ACT-12 的輸出），依 --kind（ac / dw）的模組規則計算每人每天的件數。
      員工比對 = Tags 含該姓名（不分大小寫子字串，R-030）；日期 = Created Time 的日期（R-031）；
      區間內每一天 × 每位員工都有一列，沒有就填 0；模組彼此不互斥（R-032）。
      員工名單預設 = Roster 全員（R-033），或固定名單 main55 / vn5（R-047）。
      同時整理：無效資料列（日期無法解析 / Tags 空白 / Group 空白）、被歸到 Other 的 Group 清單。

文件對應：sources.md B（計算）R-030～R-033、flows/ac.md R-034～R-045、flows/dw.md R-050～R-056
輸入：--kind ac|dw --start --end [--employees roster|main55|vn5]
輸出：<workdir>/fresh_<kind>.pkl（主表、Other 清單、無效資料、摘要）
結束碼：0 成功   1 參數錯誤 / 精簡版不存在

用法：python fresh_compute.py --workdir <dir> --kind dw --start 2026-09-01 --end 2026-09-30
"""
import argparse
from datetime import timedelta

import pandas as pd

import _bootstrap  # noqa: F401
from fresh_common import employee_names, load_short_data
from fresh_rules import Rules
from opbrain.common import add_workdir, parse_date_arg, run, save_obj


def invalid_rows(raw: pd.DataFrame) -> pd.DataFrame:
    cols = ["Row Number", "Created Time", "Group", "Tags", "Reason"]
    records = []
    checks = [
        (pd.to_datetime(raw["create_time"], errors="coerce").isna(), "Date could not be parsed"),
        (raw["tags"].str.strip() == "", "Tags is blank"),
        (raw["group"].str.strip() == "", "Group is blank"),
    ]
    for mask, reason in checks:
        for _, r in raw[mask].iterrows():
            records.append([r["row_number"], r["create_time"], r["group"], r["tags"], reason])
    if not records:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(records, columns=cols).sort_values("Row Number").reset_index(drop=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="計算 Fresh 模組件數")
    add_workdir(ap)
    ap.add_argument("--kind", required=True, choices=["ac", "dw"])
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--employees", default="roster", help="roster（預設）/ main55 / vn5")
    args = ap.parse_args()

    start, end = parse_date_arg(args.start), parse_date_arg(args.end)
    date_range = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    names = employee_names(args.employees, args.kind)
    rules = Rules(args.kind)

    raw = load_short_data()
    df = raw.copy()
    df["parsed_date"] = pd.to_datetime(df["create_time"], errors="coerce").dt.date
    df = df[df["parsed_date"].notna()]
    df = df[(df["parsed_date"] >= start) & (df["parsed_date"] <= end)]
    df = rules.add_flags(df)

    flag_cols = [f"m::{m}" for m in rules.modules]
    rows = []
    for name in names:
        sub = df[df["tags"].str.contains(name, case=False, regex=False, na=False)]
        counts = sub.groupby("parsed_date")[flag_cols].sum()
        counts = counts.reindex(index=date_range, fill_value=0).fillna(0).astype(int)
        counts.columns = rules.modules
        for d, r in counts.iterrows():
            rows.append({"Date": d, "OP Name": name, **{m: int(r[m]) for m in rules.modules}})
    order = {n: i for i, n in enumerate(names)}
    main_table = (pd.DataFrame(rows)
                  .assign(_o=lambda t: t["OP Name"].map(order))
                  .sort_values(["Date", "_o"], kind="stable").drop(columns="_o").reset_index(drop=True))
    for m in rules.modules:
        main_table[m] = main_table[m].astype(int)

    other = df[rules.other_mask(df)]
    groups = other["group"] if args.kind == "ac" else other["group"].replace("", "(blank)")
    other_groups = groups.value_counts().reset_index()
    other_groups.columns = ["Group", "Count"]

    save_obj(args.workdir / f"fresh_{args.kind}.pkl", {
        "kind": args.kind, "employees_preset": args.employees, "start": args.start, "end": args.end,
        "employees": names, "date_range": date_range, "main_table": main_table,
        "other_groups": other_groups, "invalid": invalid_rows(raw),
        "raw_row_count": len(raw), "rows_in_range": len(df),
    })
    totals = {m: int(main_table[m].sum()) for m in rules.modules}
    print(f"{args.kind.upper()}: {len(names)} employees x {len(date_range)} days; "
          f"{len(df)} ticket rows in range")
    print("  " + ", ".join(f"{m} {v}" for m, v in totals.items()))
    return 0


if __name__ == "__main__":
    run(main)
