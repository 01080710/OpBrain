"""fresh 流程（Tickets 彙總 → AC / DW 報表）各步驟共用的函式。"""
import re
from pathlib import Path

import pandas as pd

from opbrain import config, paths
from opbrain.common import InputError

TICKETS_DIR = paths.RAW / "tickets_export"


def tickets_cfg():
    return config.load("productivity", "tickets")


def kind_cfg(kind: str):
    if kind not in ("ac", "dw"):
        raise InputError(f"--kind must be ac or dw, got {kind!r}")
    return config.load("productivity", f"fresh_{kind}")


def natural_sort_key(path: Path):
    m = re.search(r"(\d+)", path.stem)
    return (int(m.group(1)) if m else 0, path.stem)


def ticket_files(folder: Path):
    """R-020：符合樣式的來源檔，依檔名數字排序。"""
    return sorted(Path(folder).glob(tickets_cfg()["source_glob"]), key=natural_sort_key)


def check_ticket_columns(files):
    """R-020：所有來源檔欄位必須完全相同，且包含必要欄位。回傳 (欄位, 錯誤訊息或 None)。"""
    if not files:
        return None, "no Tickets_*.csv files found"
    ref = None
    for f in files:
        cols = pd.read_csv(f, dtype=str, nrows=0).columns.tolist()
        missing = [c for c in tickets_cfg()["required_columns"] if c not in cols]
        if missing:
            return None, f"{f.name} is missing column(s) {missing}"
        if ref is None:
            ref = cols
        elif cols != ref:
            return None, f"{f.name} has different columns than {files[0].name}: {cols} vs {ref}"
    return ref, None


def short_csv_path():
    return paths.COMBINE / tickets_cfg()["short_output_name"]


def load_short_data():
    """讀 Tickets 精簡版（ACT-12 的輸出），欄位改名為 create_time / group / tags，並加列號。"""
    path = short_csv_path()
    if not path.exists():
        raise InputError(f"{path} not found -- run ACT-12 (tickets_clean.py) first")
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    required = tickets_cfg()["short_columns"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise InputError(f"{path.name} is missing column(s) {missing}")
    df = df[required].copy()
    df.columns = ["create_time", "group", "tags"]
    df.insert(0, "row_number", range(1, len(df) + 1))
    return df


def employee_names(preset: str, kind: str):
    """R-033 / R-047：預設 Roster 全員（第一欄）；main55 / vn5 為固定名單（只限 AC 設定檔）。"""
    from opbrain import roster
    if preset in (None, "", "roster"):
        return roster.employee_list()
    presets = config.load("productivity", "fresh_ac").get("employee_presets", {})
    if preset not in presets:
        raise InputError(f"unknown employee preset {preset!r}; valid: roster, {', '.join(presets)}")
    return list(dict.fromkeys(presets[preset]["names"]))


def output_name(kind: str, preset: str, start: str, end: str):
    if preset in (None, "", "roster"):
        tpl = kind_cfg(kind)["output_name_template"]
    else:
        tpl = config.load("productivity", "fresh_ac")["employee_presets"][preset]["output_name_template"]
        if kind == "dw":
            tpl = tpl.replace("AC Fresh", "DW Fresh")
    return tpl.format(start=start, end=end)
