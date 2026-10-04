#!/usr/bin/env python3
"""
（回歸測試）逐格比對兩個輸出檔是否完全相同。

xlsx：工作表名稱、順序、每張表的尺寸、每一格的值都要相同（日期與 datetime 視為同一天即相同）。
csv ：逐位元組比對；不同時再逐列找出第一個差異。
--ignore-order-block <工作表>:<區塊標題>：該區塊內的列只比內容不比順序（用於刻意調整過排序的區塊）。

用法：python compare_outputs.py <標準答案檔> <新產出檔> [--ignore-order-block "Summary:Employee Totals (all modules combined)"]
結束碼：0 完全相同   2 有差異   1 檔案不存在
"""
import argparse
import sys
from datetime import date, datetime
from pathlib import Path

import openpyxl


def norm(v):
    if isinstance(v, datetime) and v.hour == v.minute == v.second == 0:
        return v.date()
    return v


def sheet_values(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = {ws.title: [tuple(norm(v) for v in r) for r in ws.iter_rows(values_only=True)] for ws in wb.worksheets}
    wb.close()
    return out


def unorder_block(rows, title):
    titles = [r[0] if r else None for r in rows]
    if title not in titles:
        return rows
    i = titles.index(title) + 2           # 區塊標題 + 欄位列之後
    j = i
    while j < len(rows) and any(v is not None for v in rows[j]):
        j += 1
    return rows[:i] + sorted(rows[i:j], key=repr) + rows[j:]


def compare_xlsx(a, b, ignore):
    A, B = sheet_values(a), sheet_values(b)
    diffs = []
    if list(A) != list(B):
        diffs.append(f"sheet names differ: {list(A)} vs {list(B)}")
    for name in A:
        if name not in B:
            continue
        ra, rb = A[name], B[name]
        for sheet, block in ignore:
            if sheet == name:
                ra, rb = unorder_block(ra, block), unorder_block(rb, block)
        if len(ra) != len(rb):
            diffs.append(f"[{name}] row count {len(ra)} vs {len(rb)}")
        for i, (x, y) in enumerate(zip(ra, rb), start=1):
            if x != y:
                diffs.append(f"[{name}] row {i}: {x} != {y}")
                if len(diffs) > 10:
                    return diffs
    return diffs


def compare_csv(a, b):
    if Path(a).read_bytes() == Path(b).read_bytes():
        return []
    la = Path(a).read_text(encoding="utf-8-sig").splitlines()
    lb = Path(b).read_text(encoding="utf-8-sig").splitlines()
    for i, (x, y) in enumerate(zip(la, lb), start=1):
        if x != y:
            return [f"line {i} differs"]
    return [f"line count {len(la)} vs {len(lb)}"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("baseline")
    ap.add_argument("candidate")
    ap.add_argument("--ignore-order-block", action="append", default=[])
    args = ap.parse_args()
    for p in (args.baseline, args.candidate):
        if not Path(p).is_file():
            print(f"missing: {p}")
            return 1
    ignore = [tuple(s.split(":", 1)) for s in args.ignore_order_block]
    diffs = compare_csv(args.baseline, args.candidate) if args.baseline.lower().endswith(".csv") \
        else compare_xlsx(args.baseline, args.candidate, ignore)
    name = Path(args.candidate).name
    if diffs:
        print(f"DIFF  {name}")
        for d in diffs:
            print(f"   {d}")
        return 2
    print(f"SAME  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
