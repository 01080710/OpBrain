#!/usr/bin/env python3
"""
ACT-10  匯入新的 Tickets 匯出檔與 Roster（選擇性）

職責：使用者手動從 Freshdesk 匯出的 Tickets_*.csv 資料夾、以及新的 Roster 檔，
      先檢查再替換：新資料夾欄位必須一致且含必要欄位（R-020）、Roster 必須有正式姓名欄（team-structure:R-002）。
      檢查全部通過才刪除 data/raw/tickets_export/ 的舊檔再複製新檔（舊檔若留著，會被一起合併而污染結果）。
      兩個參數都不給 = 沿用現有資料，不做任何事。

文件對應：sources.md B S-02、S-04、R-020、H-002
輸入：[--source-folder <資料夾>] [--roster <檔案>]
輸出：<workdir>/intake.json
結束碼：0 成功（含不需匯入）   1 新資料不合格（舊資料未被動到）

用法：python tickets_intake.py --workdir <dir> --source-folder "C:/Users/.../Fresh Sept" --roster ".../Roster 202609.xlsx"
"""
import argparse
import shutil
from pathlib import Path

import _bootstrap  # noqa: F401
from fresh_common import TICKETS_DIR, check_ticket_columns, ticket_files
from opbrain import paths, roster
from opbrain.common import InputError, add_workdir, run, write_json


def main() -> int:
    ap = argparse.ArgumentParser(description="匯入新的 Tickets 匯出檔與 Roster")
    add_workdir(ap)
    ap.add_argument("--source-folder", type=Path)
    ap.add_argument("--roster", type=Path)
    args = ap.parse_args()

    new_files = None
    if args.source_folder:
        new_files = ticket_files(args.source_folder)
        _, err = check_ticket_columns(new_files)
        if err:
            raise InputError(f"new export rejected: {err}")
    if args.roster:
        roster.op_name_set(args.roster)  # 沒有正式姓名欄會丟 InputError
        if not roster.first_column_is_name_column(args.roster):
            raise InputError("new Roster rejected: first column must be 'OP Name' or 'CRM OP Name'")

    result = {"tickets_replaced": 0, "roster_replaced": False}
    if new_files:
        TICKETS_DIR.mkdir(parents=True, exist_ok=True)
        for old in ticket_files(TICKETS_DIR):
            old.unlink()
        for f in new_files:
            shutil.copy2(f, TICKETS_DIR / f.name)
        result["tickets_replaced"] = len(new_files)
        print(f"Replaced tickets export with {len(new_files)} file(s) from {args.source_folder}")
    if args.roster:
        paths.ROSTER_FILE.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.roster, paths.ROSTER_FILE)
        result["roster_replaced"] = True
        print(f"Replaced Roster with {args.roster}")
    if not new_files and not args.roster:
        print("No new data given -- reusing existing tickets export and Roster")

    write_json(args.workdir / "intake.json", result)
    return 0


if __name__ == "__main__":
    run(main)
