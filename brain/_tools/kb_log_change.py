#!/usr/bin/env python3
"""
（知識庫維護）寫入變更紀錄

每次修改某個 Skill 的文件、設定或腳本後，一行指令在該 Skill 的 trace/changes.md
新增一筆，版本號自動遞增（patch +1），並同步 skill.md frontmatter 的 version。

規則：--skill、--files、--summary、--reason 必填（原因最好連到 DEC-xxx 或 I-xxx）
用法：python kb_log_change.py --skill productivity --files "config/fresh_dw.yaml" \
          --summary "Promo Fresh 加入 Promo 關鍵字" --reason "DEC-013" --author howard
"""
import argparse
import os
import re
from datetime import date

from _kb import BRAIN, InputError, run, skills

SEMVER_ROW = re.compile(r"^\|\s*(\d+)\.(\d+)\.(\d+)\s*\|")


def cell(text):
    return text.replace("|", "\\|").replace("\n", " ").strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="寫入變更紀錄")
    ap.add_argument("--skill", required=True, choices=skills())
    ap.add_argument("--files", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--reason", required=True)
    ap.add_argument("--author", default=os.environ.get("USERNAME") or os.environ.get("USER") or "[待填]")
    ap.add_argument("--version")
    args = ap.parse_args()
    root = BRAIN / args.skill

    changes = root / "trace" / "changes.md"
    lines = changes.read_text(encoding="utf-8").splitlines()
    table = [i for i, line in enumerate(lines) if line.startswith("|")]
    if len(table) < 3:
        raise InputError("changes table not found (need header + separator + rows)")
    m = SEMVER_ROW.match(lines[table[-1]])
    if args.version:
        if not re.fullmatch(r"\d+\.\d+\.\d+", args.version):
            raise InputError("version must look like 1.2.3")
        version = args.version
    elif m:
        major, minor, patch = map(int, m.groups())
        version = f"{major}.{minor}.{patch + 1}"
    else:
        raise InputError("cannot infer next version from the last row; pass --version")

    for f in [x.strip() for x in args.files.split(",") if x.strip()]:
        if not (root / f).exists():
            print(f"WARN  file not found in {args.skill}: {f}")
    row = (f"| {version} | {date.today().isoformat()} | {cell(args.files)} | {cell(args.summary)} | "
           f"{cell(args.reason)} | {cell(args.author)} |")
    lines.insert(table[-1] + 1, row)
    changes.write_text("\n".join(lines) + "\n", encoding="utf-8")

    skill_md = root / "skill.md"
    text = skill_md.read_text(encoding="utf-8")
    skill_md.write_text(re.sub(r"^version: .*$", f"version: {version}", text, count=1, flags=re.MULTILINE),
                        encoding="utf-8")
    print(f"[{args.skill}] logged {version}: {args.summary}")
    return 0


if __name__ == "__main__":
    run(main)
