"""稽核紀錄（audit log）。規範見 brain/_core/framework.md「二、稽核紀錄」。

- 位置：data/audit/audit-YYYY-MM.jsonl（UTC 月份），一行一筆 JSON，只能附加
- 每筆含 prev_hash 與 hash（SHA-256）形成雜湊鏈；改、刪、插入任何一行，
  brain/_tools/audit_verify.py 都會發現
- 只記「誰、何時、用哪版程式與設定、產生了哪些檔（雜湊值）、結果」，不記資料內容
"""
import getpass
import hashlib
import json
import os
import platform
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from . import paths

SCHEMA_VERSION = 1
GENESIS = "0" * 64
_SKIP_ARTIFACTS = {"run_log.json", "STOP"}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def canonical(record: dict) -> str:
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def record_hash(record: dict) -> str:
    body = {k: v for k, v in record.items() if k != "hash"}
    return hashlib.sha256(canonical(body).encode("utf-8")).hexdigest()


def file_digest(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def log_files():
    return sorted(paths.AUDIT.glob("audit-*.jsonl"))


def _last_hash() -> str:
    for f in reversed(log_files()):
        for line in reversed(f.read_text(encoding="utf-8").splitlines()):
            if line.strip():
                return json.loads(line)["hash"]
    return GENESIS


def append(event: str, **fields) -> dict:
    """寫入一筆稽核紀錄。寫不進去就丟出例外：稽核紀錄失敗時流程不得繼續。"""
    record = {"schema": SCHEMA_VERSION, "ts": now_utc(), "event": event, **fields,
              "prev_hash": _last_hash()}
    record["hash"] = record_hash(record)
    paths.AUDIT.mkdir(parents=True, exist_ok=True)
    target = paths.AUDIT / f"audit-{record['ts'][:7]}.jsonl"
    with target.open("a", encoding="utf-8") as fh:
        fh.write(canonical(record) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    return record


def _git(*args):
    try:
        r = subprocess.run(["git", *args], cwd=paths.PROJECT_ROOT, capture_output=True,
                           text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def environment() -> dict:
    """執行者、主機、程式版本、所有 Skill 設定檔的雜湊值。"""
    status = _git("status", "--porcelain", "--untracked-files=no")
    return {
        "actor": {"os_user": getpass.getuser(), "git_email": _git("config", "user.email")},
        "host": socket.gethostname(),
        "python": platform.python_version(),
        "code": {"git_commit": _git("rev-parse", "HEAD"),
                 "dirty": None if status is None else bool(status)},
        "config_digest": {p.relative_to(paths.PROJECT_ROOT).as_posix(): file_digest(p)
                          for p in sorted(paths.BRAIN.glob("*/config/*.yaml"))},
    }


def snapshot(workdir: Path) -> dict:
    workdir = Path(workdir)
    return {p.relative_to(workdir).as_posix(): (p.stat().st_mtime_ns, p.stat().st_size)
            for p in workdir.rglob("*") if p.is_file()}


def changed_files(workdir: Path, before: dict) -> dict:
    """與 before 相比新增或變更的檔案 → {相對路徑: sha256}。"""
    workdir = Path(workdir)
    return {rel: file_digest(workdir / rel) for rel, sig in sorted(snapshot(workdir).items())
            if before.get(rel) != sig and rel not in _SKIP_ARTIFACTS}
