"""pbi 流程各步驟共用的小函式（報表清單、日期範圍、原始檔掃描）。"""
import re
from datetime import date as _date, timedelta

from opbrain import config, paths
from opbrain.common import InputError


def cfg():
    return config.load("productivity", "pbi")


def report_keys(arg_list):
    """--reports 參數 → 報表 key 清單（None/空 = 全部 3 份）。R-002"""
    specs = cfg()["reports"]
    keys = arg_list or list(specs)
    for k in keys:
        if k not in specs:
            raise InputError(f"Unknown report '{k}'. Valid: {list(specs)}")
    return keys


def daterange(start: _date, end: _date):
    if start > end:
        raise InputError("start date is after end date")
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def raw_dir(spec):
    return paths.RAW / spec["display_name"]


def scan_raw_files(spec):
    """掃描原始資料夾；source_date 只從檔名取得（R-003）。
    回傳 (by_date: {date: Path}, filename_errors: [檔名])。"""
    folder = raw_dir(spec)
    by_date, filename_errors = {}, []
    if not folder.exists():
        return by_date, filename_errors
    pattern = re.compile(rf"^{re.escape(spec['raw_prefix'])}_(\d{{4}}-\d{{2}}-\d{{2}})\.xlsx$")
    for f in folder.glob(f"{spec['raw_prefix']}_*.xlsx"):
        if f.name.startswith("~$"):
            continue
        m = pattern.match(f.name)
        if not m:
            filename_errors.append(f.name)
            continue
        try:
            d = _date.fromisoformat(m.group(1))
        except ValueError:
            filename_errors.append(f.name)
            continue
        by_date[d] = f
    return by_date, filename_errors


def add_range_args(ap):
    ap.add_argument("--start", required=True, help="YYYY-MM-DD（含）")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD（含）")
    ap.add_argument("--reports", nargs="*", default=None,
                    help="op_workload_p1 op_workload_p2 wd_wl_by_group；不填 = 全部")
