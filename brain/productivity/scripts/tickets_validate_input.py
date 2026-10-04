#!/usr/bin/env python3
"""
ACT-11  檢查 Tickets 來源檔與 Roster

職責：確認 data/raw/tickets_export/ 有來源檔、所有檔案欄位完全一致且含必要欄位（R-020），
      Roster 可讀且有正式姓名欄（team-structure:R-002）。任何一項不合格就不往下做。

文件對應：sources.md B（輸入）V-010
輸出：<workdir>/tickets_input_check.json（files / columns / roster_names）
結束碼：0 通過   2 不合格（關卡）

用法：python tickets_validate_input.py --workdir <dir>
"""
import argparse

import _bootstrap  # noqa: F401
from fresh_common import TICKETS_DIR, check_ticket_columns, ticket_files
from opbrain import roster
from opbrain.common import GateError, InputError, add_workdir, run, write_json


def main() -> int:
    ap = argparse.ArgumentParser(description="檢查 Tickets 來源檔與 Roster")
    add_workdir(ap)
    args = ap.parse_args()

    files = ticket_files(TICKETS_DIR)
    cols, err = check_ticket_columns(files)
    if err:
        raise GateError(f"V-010 tickets export: {err} (folder: {TICKETS_DIR})")
    try:
        names = roster.op_name_set()
    except InputError as e:
        raise GateError(f"V-010 roster: {e}")

    write_json(args.workdir / "tickets_input_check.json",
               {"files": [str(f) for f in files], "columns": cols, "roster_names": len(names)})
    print(f"{len(files)} ticket file(s), identical columns; Roster has {len(names)} name(s)")
    return 0


if __name__ == "__main__":
    run(main)
