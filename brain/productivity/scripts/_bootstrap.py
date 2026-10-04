"""把共用程式庫 brain/_core/lib 與本 Skill 的 scripts/_lib 加入 import 路徑。"""
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
for p in (_here.parents[1] / "_core" / "lib", _here / "_lib"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
