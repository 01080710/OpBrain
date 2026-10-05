"""讀取 Skill 設定檔 brain/<領域>/<skill>/config/<name>.yaml。

設定檔放規則的「值」，每一段都標註對應的規則 ID（R-xxx）；
規則的意義與理由寫在該 Skill 的 rules.md 或 flows/<流程>.md。兩邊的 ID 由
brain/_framework/tools/check_config_ids.py 檢查是否一致。
"""
from functools import lru_cache

import yaml

from . import paths
from .common import InputError


@lru_cache(maxsize=None)
def load(skill: str, name: str) -> dict:
    path = paths.skill_dir(skill) / "config" / f"{name}.yaml"
    if not path.is_file():
        raise InputError(f"config not found: {path}")
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}
