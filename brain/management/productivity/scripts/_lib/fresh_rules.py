"""AC / DW 模組分類規則的實作（規則的值在 config/fresh_ac.yaml、fresh_dw.yaml）。

compute（向量化）與 brute_force（逐列重算，給 ACT-15 抽查用）是兩套獨立寫法，
用來互相驗證；修改規則時兩邊都要改。
"""
import pandas as pd

from fresh_common import kind_cfg


class Rules:
    def __init__(self, kind: str):
        self.kind = kind
        c = kind_cfg(kind)
        self.cfg = c
        self.modules = list(c["module_order"])
        if kind == "ac":
            self.ac_groups = set(c["ac_groups"])
            self.group_inv = {g: m for m, gs in c["group_module_map"].items() for g in gs}
            self.other2 = set(c["other2_groups"])
            self.known = self.ac_groups | set(self.group_inv) | self.other2
            self.group_modules = ["AC"] + list(c["group_module_map"]) + ["Other", "Other 2"]
            self.keywords = dict(c["keyword_rules"])
        else:
            self.dw_groups = {m: {g.lower() for g in gs} for m, gs in c["group_modules"].items()}
            self.other_excluded = {g.lower() for g in c["other_excluded_groups"]}
            self.keywords = dict(c["keyword_modules"])

    # ---- AC：Group 完全相同（R-034、R-040～R-043） ----
    def classify_ac_group(self, group: str):
        if group == "":
            return None
        if group in self.ac_groups:
            return "AC"
        if group in self.group_inv:
            return self.group_inv[group]
        if group in self.other2:
            return "Other 2"
        return "Other"

    def add_flags(self, df: pd.DataFrame) -> pd.DataFrame:
        """在計算用資料表上加上每個模組的 0/1 標記欄 m::<模組>。"""
        tags_lower = df["tags"].str.lower()
        if self.kind == "ac":
            gm = df["group"].apply(self.classify_ac_group)
            df["group_module"] = gm
            for m in self.group_modules:
                df[f"m::{m}"] = gm == m
        else:
            group_lower = df["group"].str.lower()
            for m, groups in self.dw_groups.items():           # R-050～R-052、R-055
                df[f"m::{m}"] = group_lower.isin(groups)
            df["m::Other Fresh"] = ~group_lower.isin(self.other_excluded)  # R-053
        for m, kw in self.keywords.items():                    # R-044、R-054
            df[f"m::{m}"] = tags_lower.str.contains(kw.lower(), regex=False, na=False)
        return df

    def other_mask(self, df):
        return df["m::Other"] if self.kind == "ac" else df["m::Other Fresh"]

    # ---- 逐列重算（獨立實作，給驗證用） ----
    def brute_force_hit(self, group: str, tags: str, module: str) -> bool:
        tl = tags.lower()
        if module in self.keywords:
            return self.keywords[module].lower() in tl
        if self.kind == "ac":
            if module == "AC":
                return group in self.ac_groups
            if module == "Other":
                return group != "" and group not in self.known
            if module == "Other 2":
                return group in self.other2
            return group in self.cfg["group_module_map"].get(module, [])
        gl = group.lower()
        if module == "Other Fresh":
            return gl not in self.other_excluded
        return gl in self.dw_groups[module]
