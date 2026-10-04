#!/usr/bin/env python3
"""
（知識庫維護）建立新的業務主題 Skill

從 brain/_tools/template/ 複製文件骨架（必備檔 + flows/flow.md）到 brain/<name>/，填好 frontmatter 的 name、
建立 config/ 與 scripts/（含 _bootstrap.py、run_workflow.py 範本），
最後重新產生 .claude/skills/ 的入口。

用法：python new_skill.py --name scheduling --title "排班" --depends-on team-structure
"""
import argparse
import re
import shutil
import subprocess
import sys

from _kb import BRAIN, TOOLS, InputError, run

RUN_WORKFLOW = '''#!/usr/bin/env python3
"""
（流程總控）{name} 的具名流程。新增步驟腳本後，在 FLOWS 登記。

用法：python run_workflow.py --flow <名稱>
結束碼：0 成功   1 輸入錯誤   2 關卡擋下   3 緊急停止
"""
import argparse
from pathlib import Path

import _bootstrap  # noqa: F401
from opbrain.common import InputError, new_workdir, run
from opbrain.workflow import Step, run_steps

SCRIPT_DIR = Path(__file__).resolve().parent
FLOWS = {{}}  # 例："check": [Step("ACT-xx", "xxx.py")]，ACT 編號登記在 flows/<流程>.md


def main() -> int:
    ap = argparse.ArgumentParser(description="{name} 流程總控")
    ap.add_argument("--flow", required=True)
    a = ap.parse_args()
    if a.flow not in FLOWS:
        raise InputError(f"unknown flow {{a.flow!r}}; valid: {{list(FLOWS)}}")
    wd = new_workdir("{name}", a.flow)
    return run_steps(SCRIPT_DIR, FLOWS[a.flow], wd, a.flow)


if __name__ == "__main__":
    run(main)
'''


def main() -> int:
    ap = argparse.ArgumentParser(description="建立新 Skill")
    ap.add_argument("--name", required=True, help="英文小寫加連字號，例如 scheduling")
    ap.add_argument("--title", required=True, help="中文名稱，例如 排班")
    ap.add_argument("--depends-on", default="team-structure", help="逗號分隔")
    args = ap.parse_args()
    if not re.fullmatch(r"[a-z][a-z0-9\-]*", args.name):
        raise InputError("name must be lowercase letters, digits and hyphens")
    dest = BRAIN / args.name
    if dest.exists():
        raise InputError(f"{dest} already exists")

    shutil.copytree(TOOLS / "template", dest)
    skill_md = dest / "skill.md"
    text = skill_md.read_text(encoding="utf-8")
    deps = ", ".join(d.strip() for d in args.depends_on.split(",") if d.strip())
    text = text.replace('name: "[待填：skill-name]"', f"name: {args.name}", 1)
    text = text.replace("status: skeleton\n", f"status: skeleton\ndepends_on: [{deps}]\nprovides: []\n", 1)
    text = text.replace("# [待填：Skill 名稱]", f"# {args.title}（{args.name}）", 1)
    skill_md.write_text(text, encoding="utf-8")

    (dest / "config").mkdir()
    scripts = dest / "scripts"
    scripts.mkdir()
    shutil.copy2(BRAIN / "productivity" / "scripts" / "_bootstrap.py", scripts / "_bootstrap.py")
    (scripts / "_lib").mkdir()
    (scripts / "run_workflow.py").write_text(RUN_WORKFLOW.format(name=args.name), encoding="utf-8")

    print(f"created {dest}")
    subprocess.run([sys.executable, str(TOOLS / "sync_claude_skills.py")])
    print("下一步：填寫 skill.md 的 description（使用者會怎麼說）、context.md，再把 flows/flow.md 改名為流程名稱並填寫。")
    return 0


if __name__ == "__main__":
    run(main)
