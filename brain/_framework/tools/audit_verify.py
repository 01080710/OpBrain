#!/usr/bin/env python3
"""
（稽核）驗證 data/audit/ 的稽核紀錄沒有被改、刪、插入。

1. 每一筆的 hash 與內容重算結果一致
2. 每一筆的 prev_hash 等於前一筆的 hash（跨月份檔案連續）
3. 每個 run_id 都有 flow_end（沒有的列為警告：流程被強制中斷）

結束碼：0 通過（或尚無紀錄）   2 紀錄不一致
用法：python audit_verify.py
"""
import json
from collections import OrderedDict

from _kb import EXIT_GATE, run
from opbrain import audit


def main() -> int:
    files = audit.log_files()
    if not files:
        print("no audit log yet")
        return 0
    errors, open_runs = [], OrderedDict()
    prev, count = None, 0
    for f in files:
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            where = f"{f.name}:{n}"
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"{where} not valid JSON")
                prev = None
                continue
            count += 1
            if rec.get("hash") != audit.record_hash(rec):
                errors.append(f"{where} content does not match its hash (edited)")
            if prev is None and count == 1:
                if rec.get("prev_hash") != audit.GENESIS:
                    print(f"WARN  {where} chain starts mid-way (earlier files archived?)")
            elif rec.get("prev_hash") != prev:
                errors.append(f"{where} prev_hash does not match previous record (deleted or inserted)")
            prev = rec.get("hash")
            if rec.get("event") == "flow_start":
                open_runs[rec["run_id"]] = where
            elif rec.get("event") == "flow_end":
                open_runs.pop(rec.get("run_id"), None)
    for run_id, where in open_runs.items():
        print(f"WARN  run {run_id} started at {where} has no flow_end (interrupted)")
    for e in errors:
        print(f"ERROR {e}")
    print(f"checked {count} record(s) in {len(files)} file(s): {len(errors)} error(s)")
    return EXIT_GATE if errors else 0


if __name__ == "__main__":
    run(main)
