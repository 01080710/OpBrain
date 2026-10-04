"""_tools 共用：列出 Skill、ID 樣式。"""
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
BRAIN = TOOLS.parent
sys.path.insert(0, str(BRAIN / "_core" / "lib"))

from opbrain.common import EXIT_GATE, InputError, run  # noqa: E402,F401

# 每個 Skill 的文件結構（2026-10-04 起，productivity DEC-016、DEC-017）：
# 必備檔 + 選用 rules.md（跨業務線共用規則）、sources.md（共用資料來源與取得流程）+ 每條業務線／流程一份 flows/<名稱>.md
REQUIRED = ["skill.md", "context.md", "decision.md",
            "trace/decisions.md", "trace/changes.md", "trace/issues.md"]
OPTIONAL = ["rules.md", "sources.md"]
FLOWS_DIR = "flows/"
MAX_LINES = 300   # 超過就提醒拆檔
NON_DOC_DIRS = ("scripts/", "config/", "work/", "dist/")

ID =r"(?:ACT|INV|DEC|SEC|TC|[ARDBTLHFEVICPS])-\d{2,3}"
ID_RE = re.compile(rf"\b{ID}\b")
XREF_RE = re.compile(rf"\b([a-z][a-z0-9\-]*|_core):({ID})\b")   # 跨 Skill 引用：skill:R-001
DEF_RE = re.compile(rf"^\|\s*({ID})\s*\||^#{{1,6}}\s*({ID})\b")


def skills():
    """brain/ 底下的 Skill（有 skill.md、名稱不以 _ 開頭）。"""
    return sorted(p.name for p in BRAIN.iterdir()
                  if p.is_dir() and not p.name.startswith("_") and (p / "skill.md").is_file())


def is_allowed_doc(rel: str) -> bool:
    """rel 是否屬於規定的文件結構（必備、選用或 flows/ 底下一層的 .md）。"""
    return (rel in REQUIRED or rel in OPTIONAL
            or (rel.startswith(FLOWS_DIR) and rel.count("/") == 1 and rel.endswith(".md")))


def resolve(args_skill, args_all):
    if args_all or not args_skill:
        return skills()
    if args_skill not in skills():
        raise InputError(f"unknown skill {args_skill!r}; known: {skills()}")
    return [args_skill]


def docs(root: Path):
    return {p.relative_to(root).as_posix(): p.read_text(encoding="utf-8")
            for p in sorted(root.rglob("*.md"))
            if not p.relative_to(root).as_posix().startswith(NON_DOC_DIRS)}


def defined_ids(root: Path):
    out = {}
    for rel, text in docs(root).items():
        for line in text.splitlines():
            m = DEF_RE.match(line)
            if m:
                out.setdefault(m.group(1) or m.group(2), []).append(rel)
    return out


def frontmatter(text: str) -> dict:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm
