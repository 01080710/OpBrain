#!/usr/bin/env python3
"""
（安全）機密掃描

職責：交付或提交前，掃描目錄中是否夾帶金鑰、token、私鑰、密碼。
      輸出只列「檔案:行號 規則名稱」，絕不印出命中的內容（避免二次洩漏）。

文件對應：brain/_org/conventions.md §9（機密不入庫）
規則：private-key、aws-access-key、api-key-like、slack-token、jwt、assignment（key/secret/token/password = "..."）
略過：.git、node_modules、__pycache__、dist、二進位檔、大於 1MB 的檔；
      行內含 `nosecret` 標記者視為已人工確認的誤報
結束碼：0 無發現   1 路徑不存在   2 有發現（阻擋）

用法：python scan_secrets.py --paths ../.. （整個專案；data/、.venv/、_archive/ 會略過）
"""
import argparse
import re
from pathlib import Path

from _kb import EXIT_GATE, InputError, run

PATTERNS = {
    "private-key": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    "aws-access-key": r"\bAKIA[0-9A-Z]{16}\b",
    "api-key-like": r"\bsk-[A-Za-z0-9_-]{20,}\b",
    "slack-token": r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b",
    "jwt": r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b",
    "assignment": r"(?i)\b(?:api[_-]?key|secret|token|passw(?:or)?d)\b\s*[:=]\s*['\"][^'\"\s]{8,}['\"]",
}
COMPILED = {name: re.compile(p) for name, p in PATTERNS.items()}
SKIP_DIRS = {".git", "node_modules", "__pycache__", "dist", ".venv", "data", "_archive", ".env", ".secrets"}  # .env/.secrets 本來就不入庫
MAX_BYTES = 1024 * 1024


def iter_files(root: Path):
    if root.is_file():
        yield root
        return
    for p in root.rglob("*"):
        if p.is_file() and not (SKIP_DIRS & set(p.parts)):
            yield p


def scan_file(path: Path):
    if path.stat().st_size > MAX_BYTES:
        return
    data = path.read_bytes()
    if b"\0" in data:
        return                                  # 二進位檔
    for no, line in enumerate(data.decode("utf-8", errors="ignore").splitlines(), start=1):
        if "nosecret" in line:
            continue
        for name, rx in COMPILED.items():
            if rx.search(line):
                yield no, name


def main() -> int:
    ap = argparse.ArgumentParser(description="機密掃描")
    ap.add_argument("--paths", nargs="+", type=Path, default=[Path(".")])
    args = ap.parse_args()
    missing = [str(p) for p in args.paths if not p.exists()]
    if missing:
        raise InputError(f"path not found: {missing}")

    findings = 0
    for root in args.paths:
        for f in iter_files(root):
            for no, rule in scan_file(f):
                print(f"{f}:{no}  {rule}")
                findings += 1
    print(f"scan complete: {findings} finding(s)")
    return EXIT_GATE if findings else 0


if __name__ == "__main__":
    run(main)
