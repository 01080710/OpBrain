#!/usr/bin/env python3
"""
（知識庫維護）一次跑完所有檢查——改完大腦（文件、設定、腳本）後必跑。

1. kb_check_structure.py   每個 Skill 的必備文件、flows/ 與 frontmatter
2. kb_check_refs.py        文件之間的引用（含跨 Skill）
3. check_code_refs.py      設定／腳本的 ID 與文件一致
4. sync_claude_skills.py --check   .claude/skills 入口是否與 brain 同步
5. scan_secrets.py         專案內沒有夾帶金鑰

結束碼：0 全部通過   1 有任何一項沒過
用法：python check_all.py
"""
import subprocess
import sys

from _kb import BRAIN, TOOLS

CHECKS = [
    ["kb_check_structure.py"],
    ["kb_check_refs.py"],
    ["check_code_refs.py"],
    ["sync_claude_skills.py", "--check"],
    ["scan_secrets.py", "--paths", str(BRAIN.parent)],
]


def main() -> int:
    failed = []
    for cmd in CHECKS:
        print(f"\n### {' '.join(cmd)}")
        if subprocess.run([sys.executable, str(TOOLS / cmd[0]), *cmd[1:]]).returncode != 0:
            failed.append(cmd[0])
    print(f"\n{'ALL CHECKS PASSED' if not failed else 'FAILED: ' + ', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
