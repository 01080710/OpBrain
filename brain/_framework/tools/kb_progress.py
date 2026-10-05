#!/usr/bin/env python3
"""
（知識庫維護）完成度儀表板

逐份文件統計 [待填]、[待確認]、未勾選的核對項，以及文件頭部狀態
（skeleton < draft < reviewed < active）。
--write 會回寫各 skill.md 的「完成度總覽」表（| `文件` | 狀態 |）。

用法：python kb_progress.py [--skill productivity] [--write]
"""
import argparse
import re

from _kb import BRAIN, skill_root, docs, resolve, run

LEVELS = ["skeleton", "draft", "reviewed", "active"]
STATUS_RE = re.compile(r"\*\*狀態\*\*：`(\w+)`")
TODO_RE = re.compile(r"\[待填[^\]]*\]")
UNCONFIRMED_RE = re.compile(r"\[待確認\]")
UNCHECKED_RE = re.compile(r"^\s*- \[ \]", re.MULTILINE)


def file_stats(text: str) -> dict:
    m = STATUS_RE.search(text)
    return {"level": m.group(1) if m and m.group(1) in LEVELS else "skeleton",
            "todo": len(TODO_RE.findall(text)), "unconfirmed": len(UNCONFIRMED_RE.findall(text)),
            "unchecked": len(UNCHECKED_RE.findall(text))}


def report(skill, write):
    root = skill_root(skill)
    summary = {rel: file_stats(text) for rel, text in docs(root).items() if rel != "skill.md"}
    print(f"\n[{skill}]")
    print(f"{'doc':<24}{'status':<10}{'[待填]':>8}{'[待確認]':>9}{'未勾選':>8}")
    for rel, s in summary.items():
        print(f"{rel:<24}{s['level']:<10}{s['todo']:>8}{s['unconfirmed']:>9}{s['unchecked']:>8}")
    if write:
        skill_md = root / "skill.md"
        text = skill_md.read_text(encoding="utf-8")
        for rel, s in summary.items():
            text = re.sub(rf"(\| `{re.escape(rel)}` \| )(?:{'|'.join(LEVELS)})( \|)", rf"\g<1>{s['level']}\g<2>", text)
        skill_md.write_text(text, encoding="utf-8")
        print("skill.md 完成度總覽已更新")


def main() -> int:
    ap = argparse.ArgumentParser(description="完成度儀表板")
    ap.add_argument("--skill")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    for s in resolve(args.skill, args.all):
        report(s, args.write)
    return 0


if __name__ == "__main__":
    run(main)
