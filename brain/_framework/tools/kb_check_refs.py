#!/usr/bin/env python3
"""
（知識庫維護）檢查文件之間的引用是否有效（含跨 Skill 引用）

R-1 反引號內的文件路徑（`rules.md`、`flows/ac.md#R-040`）指向本 Skill 存在的文件
R-2 被引用的 ID 在本 Skill 有定義；`其他skill:R-001` 形式則必須在該 Skill 有定義
R-3 同一個 ID 在同一個 Skill 內沒有被定義兩次
「定義」：表格列的第一欄是 ID（| R-001 | …），或標題以 ID 開頭（### DEC-001：…）

結束碼：0 通過   1 有問題
用法：python kb_check_refs.py [--skill productivity]
"""
import argparse

from _kb import BRAIN, ID_RE, XREF_RE, defined_ids, docs, resolve, run, skills
import re

EXTERNAL_DOCS = {"README.md", "CLAUDE.md", "AGENTS.md", "SKILL.md"}   # 專案層級的檔名，不是本 Skill 的文件
PATH_RE = re.compile(r"`([A-Za-z0-9_\-]+(?:/[A-Za-z0-9_\-]+)*\.md)(?:#([\w\-]+))?`")


def check(skill, all_defined):
    root = BRAIN / skill
    d = docs(root)
    defined = all_defined[skill]
    errors = []
    for rel, text in d.items():
        for path, anchor in PATH_RE.findall(text):
            if path in EXTERNAL_DOCS or path.startswith(("brain/", "data/", "_core/", "_tools/")):
                continue
            if path not in d:
                errors.append(f"R-1 {rel}: path not found: {path}")
            elif anchor and ID_RE.fullmatch(anchor) and path not in defined.get(anchor, []):
                errors.append(f"R-1 {rel}: {path}#{anchor} not defined there")
        for other, ident in XREF_RE.findall(text):
            if other == "_core":
                continue
            if other not in all_defined:
                errors.append(f"R-2 {rel}: unknown skill in reference {other}:{ident}")
            elif ident not in all_defined[other]:
                errors.append(f"R-2 {rel}: {other}:{ident} not defined in {other}")
        local_text = XREF_RE.sub("", text)
        for ref in sorted(set(ID_RE.findall(local_text))):
            if ref not in defined:
                errors.append(f"R-2 {rel}: {ref} referenced but never defined")
    for ident, where in sorted(defined.items()):
        if len(where) > 1:
            errors.append(f"R-3 {ident} defined {len(where)} times: {', '.join(where)}")
    for e in errors:
        print(f"ERROR [{skill}] {e}")
    print(f"[{skill}] scanned {len(d)} docs, {len(defined)} IDs defined: {len(errors)} problem(s)")
    return not errors


def main() -> int:
    ap = argparse.ArgumentParser(description="檢查文件引用")
    ap.add_argument("--skill")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    all_defined = {s: defined_ids(BRAIN / s) for s in skills()}
    ok = all([check(s, all_defined) for s in resolve(args.skill, args.all)])
    return 0 if ok else 1


if __name__ == "__main__":
    run(main)
