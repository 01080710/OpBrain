#!/usr/bin/env python3
"""
（知識庫維護）檢查 Skill 知識庫的結構是否完整

結構：必備 skill.md、context.md、decision.md、trace/{decisions,changes,issues}.md；
      選用 rules.md、sources.md；每條業務線／流程一份 flows/<名稱>.md（productivity DEC-016、DEC-017）
檢查：S-1 缺少必備文件   S-2 空檔   S-3 缺「核心問題」   S-4 不在結構內的 .md（警告；--strict 視為錯誤）
      S-5 skill.md frontmatter 缺 name / description / version / status / depends_on
      S-6 沒有任何 flows/*.md（警告）   S-7 文件超過 MAX_LINES 行，考慮拆檔（警告）
結束碼：0 通過   1 有問題

用法：python kb_check_structure.py              # 檢查所有 Skill
      python kb_check_structure.py --skill productivity --strict
"""
import argparse

from _kb import BRAIN, FLOWS_DIR, MAX_LINES, REQUIRED, docs, frontmatter, is_allowed_doc, resolve, run


def check(skill, strict):
    root = BRAIN / skill
    errors, warnings = [], []
    for rel in REQUIRED:
        if not (root / rel).is_file():
            errors.append(f"S-1 missing: {rel}")
    d = docs(root)
    for rel, text in d.items():
        if not is_allowed_doc(rel):
            (errors if strict else warnings).append(f"S-4 not in structure: {rel}")
            continue
        if not text.strip():
            errors.append(f"S-2 empty: {rel}")
        elif "核心問題" not in text:
            errors.append(f"S-3 no 核心問題: {rel}")
        elif len(text.splitlines()) > MAX_LINES:
            warnings.append(f"S-7 {rel} has {len(text.splitlines())} lines (> {MAX_LINES}); consider splitting")
    if not any(rel.startswith(FLOWS_DIR) for rel in d):
        warnings.append(f"S-6 no {FLOWS_DIR}*.md")
    if (root / "skill.md").is_file():
        fm = frontmatter((root / "skill.md").read_text(encoding="utf-8"))
        for key in ("name", "description", "version", "status", "depends_on"):
            if key not in fm:
                errors.append(f"S-5 skill.md frontmatter missing '{key}'")
    for w in warnings:
        print(f"WARN  [{skill}] {w}")
    for e in errors:
        print(f"ERROR [{skill}] {e}")
    print(f"[{skill}] checked {len(d)} docs: {len(errors)} error(s), {len(warnings)} warning(s)")
    return not errors


def main() -> int:
    ap = argparse.ArgumentParser(description="檢查知識庫結構")
    ap.add_argument("--skill")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    ok = all([check(s, args.strict) for s in resolve(args.skill, args.all)])
    return 0 if ok else 1


if __name__ == "__main__":
    run(main)
