#!/usr/bin/env python3
"""
（知識庫維護）檢查程式／設定與文件的 ID 是否一致

C-1 config/*.yaml 裡標註的規則 ID（R-xxx）必須定義在 rules.md、sources.md 或 flows/*.md
C-2 scripts/*.py 開頭 docstring 的動作 ID（ACT-xx）必須登記在 sources.md 或 flows/*.md 的動作表
C-3 scripts 與 config 引用的其他 ID（V-、DEC-、F-、TC-…；含 skill:ID）必須在對應 Skill 有定義
C-4 sources.md、flows/*.md 登記的每個動作 ID，都要有一支腳本的 docstring 宣告它

結束碼：0 通過   1 有問題
用法：python check_code_refs.py [--skill productivity]
"""
import argparse
import re

from _kb import BRAIN, skill_root, FLOWS_DIR, ID_RE, OPTIONAL, XREF_RE, defined_ids, resolve, run, skills

ACT_HEAD = re.compile(r'^"""\s*\n(ACT-\d{2})\b', re.MULTILINE)


def check(skill, all_defined):
    root = skill_root(skill)
    defined = all_defined[skill]
    def in_spec(where):   # 定義在 rules.md、sources.md 或 flows/*.md
        return any(w in OPTIONAL or w.startswith(FLOWS_DIR) for w in where)

    rules_defs = {i for i, where in defined.items() if in_spec(where)}
    act_defs = {i for i, where in defined.items() if i.startswith("ACT-") and in_spec(where)}
    errors, declared_acts = [], set()

    sources = [(p, p.read_text(encoding="utf-8")) for p in sorted((root / "config").glob("*.yaml"))]
    sources += [(p, p.read_text(encoding="utf-8")) for p in sorted((root / "scripts").rglob("*.py"))]
    for p, text in sources:
        rel = p.relative_to(root).as_posix()
        for other, ident in XREF_RE.findall(text):
            if other not in ("_core",) and (other not in all_defined or ident not in all_defined[other]):
                errors.append(f"C-3 {rel}: {other}:{ident} not defined")
        local = XREF_RE.sub("", text)
        m = ACT_HEAD.search(text)
        if m:
            declared_acts.add(m.group(1))
            if m.group(1) not in act_defs:
                errors.append(f"C-2 {rel}: {m.group(1)} not registered in sources.md or flows/*.md")
        for ref in sorted(set(ID_RE.findall(local))):
            if p.suffix == ".yaml" and ref.startswith("R-") and ref not in rules_defs:
                errors.append(f"C-1 {rel}: {ref} not defined in rules.md, sources.md or flows/*.md")
            elif ref not in defined:
                errors.append(f"C-3 {rel}: {ref} not defined in {skill} docs")
    for a in sorted(act_defs - declared_acts):
        errors.append(f"C-4 {a}: registered in docs but no script declares it")
    for e in errors:
        print(f"ERROR [{skill}] {e}")
    print(f"[{skill}] code/config refs: {len(errors)} problem(s)")
    return not errors


def main() -> int:
    ap = argparse.ArgumentParser(description="檢查程式與文件的 ID 一致性")
    ap.add_argument("--skill")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    all_defined = {s: defined_ids(skill_root(s)) for s in skills()}
    ok = all([check(s, all_defined) for s in resolve(args.skill, args.all)])
    return 0 if ok else 1


if __name__ == "__main__":
    run(main)
