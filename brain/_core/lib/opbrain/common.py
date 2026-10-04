"""共用小工具。不是流程步驟，沒有 ACT 編號。

統一的結束碼（所有 Skill 的所有腳本一致；run_workflow.py 以此判斷）：
    0  成功
    1  輸入錯誤（檔案缺漏、欄位缺漏、參數不合法）
    2  被品質關卡擋下（資料不完整、驗證未通過）—「安全停止」，不是程式錯誤
    3  被緊急停止（工作目錄內有 STOP 檔）
"""
import json
import pickle
import sys
from datetime import datetime
from pathlib import Path

from . import paths

EXIT_OK, EXIT_INPUT, EXIT_GATE, EXIT_STOPPED = 0, 1, 2, 3


class InputError(Exception):
    """輸入缺漏或不合法 → 結束碼 1。"""


class GateError(Exception):
    """被品質關卡擋下 → 結束碼 2。訊息說明哪個檢查沒過。"""


def run(main):
    """腳本進入點：把 InputError / GateError 統一轉成結束碼。"""
    try:
        code = main()
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        code = EXIT_INPUT
    except GateError as exc:
        print(f"GATE: {exc}", file=sys.stderr)
        code = EXIT_GATE
    except PermissionError as exc:
        print(f"ERROR: cannot write {exc.filename} -- close it in Excel and run again", file=sys.stderr)
        code = EXIT_INPUT
    except BrokenPipeError:
        sys.stderr.close()
        code = EXIT_OK
    sys.exit(code or EXIT_OK)


def add_workdir(ap):
    ap.add_argument("--workdir", type=Path, required=True,
                    help="本次執行的工作目錄（由 run_workflow.py 建立，位於 data/work/ 底下）")


def new_workdir(skill: str, flow: str) -> Path:
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    wd = paths.WORK / skill / flow / run_id
    wd.mkdir(parents=True, exist_ok=True)
    return wd


def require(path, hint=""):
    path = Path(path)
    if not path.is_file():
        raise InputError(f"missing file: {path}" + (f"（{hint}）" if hint else ""))
    return path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def save_obj(path, obj):
    """步驟之間傳遞中間結果（保留原始型別，避免轉檔造成數值差異）。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fh:
        pickle.dump(obj, fh)


def load_obj(path):
    with require(path, "前一個步驟的輸出不存在，請先執行前一步").open("rb") as fh:
        return pickle.load(fh)


def parse_date_arg(value: str):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise InputError(f"date must be YYYY-MM-DD, got {value!r}")
