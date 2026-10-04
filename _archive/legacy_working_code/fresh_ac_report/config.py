"""
All adjustable settings for the AC Daily Module Report.

Nothing in generate_ac_report.py should hardcode employee names, group
lists, keywords, dates, or file paths -- everything adjustable lives
here so the report can be re-tuned without touching the calculation
code.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_FOLDER = BASE_DIR / "input"
OUTPUT_FOLDER = BASE_DIR / "output"

# ---------------------------------------------------------------------------
# Date range for the report (inclusive on both ends)
# ---------------------------------------------------------------------------
START_DATE = "2026-06-18"
END_DATE = "2026-08-31"

# ---------------------------------------------------------------------------
# Source column mapping.
#
# Keys are fixed (the program looks these up by key). Values are the
# ACTUAL column names found in the source CSV -- edit the values here
# if the source file's header changes, never edit generate_ac_report.py.
#
# The real source file (Tickets Roster Tagged Short.csv) uses
# "Created Time", not "Create Time" -- confirmed by reading the file
# directly.
# ---------------------------------------------------------------------------
COLUMN_MAPPING = {
    "create_time": "Created Time",
    "group": "Group",
    "tags": "Tags",
}

# ---------------------------------------------------------------------------
# Employee list.
#
# Only 24 confirmed names were provided when this report was built (the
# 25th line of the original request was an instruction, not a name).
# Add/remove/reorder names here directly -- row order in the final
# report follows this list's order exactly.
#
# To switch to reading the employee list from an external file instead
# (e.g. a fuller roster export), set EMPLOYEE_LIST_FILE below to that
# file's path. When EMPLOYEE_LIST_FILE is set, EMPLOYEE_NAMES is
# ignored. The external file must be .csv or .xlsx with the names in
# its first column (a header row is fine and will be skipped
# automatically if the first cell is not blank and repeats down the
# column is not the intent -- see load_employee_names() for the exact
# rule).
# ---------------------------------------------------------------------------
EMPLOYEE_NAMES = [
    "Omar Guerraoui",
    "Cisse Papa Amadou",
    "Laura Lim",
    "Joanne Loy",
    "Liyana Pertiwi",
    "Alex Lee",
    "Junquan Ko",
    "Priyatharishini Saravanan",
    "Teo Sui Kee",
    "Rina Tan",
    "Vicky Nak",
    "Aileen Chiang",
    "Ummu Sarah",
    "Sky Wong",
    "Kc Choi",
    "Calvin Lim",
    "Nurul Athirah",
    "Kaisheng Tham",
    "Elton Foo",
    "Grace Tee",
    "Ann Liao",
    "Jim Chen",
    "John Wu",
    "Lin Chen",
    "Victor Wang",
    "Alice Liao",
    "Melody Hu",
    "Adeline Chen",
    "Poya Huang",
    "Evan Chang",
    "Ken Lai",
    "Sam Lu",
    "Phoebe Sun",
    "Wilson Wen",
    "Sen Yu",
    "Xinyue Chong",
    "Chloe Chen",
    "Savrina Goh",
    "Windy Chen",
    "Wendy Wu",
    "Hailey Wu",
    "Martin Lin",
    "Thuy Duong Nguyen",
    "Nguyen Minh Quan",
    "Pham Thi Huyen Chau",
    "Thi Hong Tham Nguyen",
    "Bui Ngoc Van Anh",
    "Thuy Phuong Uyen Nguyen",
    "Chau Ngoc Thinh",
    "Tran Duc Huy",
    "Vo Duc Tan",
    "Nguyen Thi Lap",
    "Nguyen Thi Xuan Lan",
    "Vo Hoang Thuan",
    "Ngo Thi Dieu Huyen",
]

# Set to a Path to load employee names from an external file instead of
# the EMPLOYEE_NAMES list above. Example:
#   EMPLOYEE_LIST_FILE = BASE_DIR / "input" / "employee_list.xlsx"
EMPLOYEE_LIST_FILE = None

# ---------------------------------------------------------------------------
# Module classification rules
# ---------------------------------------------------------------------------

# Module display order == column order C:L(+M) in the output report.
MODULE_ORDER = [
    "AC",
    "Cpa-Ac",
    "Cpa-Payment",
    "IB",
    "IB-Adjustment",
    "FCA",
    "Other",
    "CPA-Multi plan",
    "CPA-hybrid plan",
    "CPA-non-standard plan",
    "Other 2",
]

# "AC" module: Group must be an exact match to one of these.
#
# "(OP)Acc-Account Owner Transfer" and "(OP)Acc-ID/POA" were added
# 2026-09-21 -- they showed up as large-volume unclassified groups in a
# Sept 2026 ticket export (9,178 / 1,912 rows respectively) that did not
# exist in the original spec's group list; confirmed with the user to
# count as AC.
AC_GROUPS = [
    "Ticket Admin team",
    "(OP)Account Team",
    "(OP)Acc-CES",
    "(OP)Acc-QC Ranger",
    "(OP)Acc-CS",
    "(OP)Acc-AEJ",
    "(OP)Acc-ASIC",
    "OWS Team",
    "Internal Tasks",
    "Translation - KOM",
    "(OP)Acc-Account Owner Transfer",
    "(OP)Acc-ID/POA",
]

# Single-group modules: Group must be an exact match to one of the
# given group names (a list, not a single string) -- some modules have
# been renamed in the source system over time, and older raw data
# (e.g. the original June-August export) still uses the old name, so
# both old and new names are kept here rather than replacing one with
# the other.
#
# IB: "(OP)Acc-AAK" is the original name (June-Aug data);
#     "(OP)Acc-New IB" appeared in a Sept 2026 export -- confirmed with
#     the user 2026-09-21 to be the same module under a new name.
# IB-Adjustment: "(OP)Acc-AAK (IB Adjustment)" is the original name;
#     "(OP)Acc-IB Adjustment" appeared in the same Sept 2026 export --
#     confirmed with the user 2026-09-21 to be the same module renamed.
GROUP_MODULE_MAP = {
    "Cpa-Ac": ["(OP)Cpa-AC team"],
    "Cpa-Payment": ["(OP)Cpa-Payment team"],
    "IB": ["(OP)Acc-AAK", "(OP)Acc-New IB"],
    "IB-Adjustment": ["(OP)Acc-AAK (IB Adjustment)", "(OP)Acc-IB Adjustment"],
    "FCA": ["(OP)FCA-Tickets"],
}

# "Other 2" module: Group must be an exact match to one of these.
# These are the 18 group names the "Other Groups" QC sheet surfaced as
# already-seen/expected large-volume groups (e.g. the deposit/withdraw
# processing teams) that are NOT part of any specific module above but
# should not be lumped in with genuinely new/unexpected groups either.
# A group name showing up here means "known, just not modeled as its
# own module" -- as opposed to "Other", which is reserved for groups
# that are not in this file at all (i.e. new/unexpected).
OTHER2_GROUPS = [
    "(OP)Withdrawal Team",
    "(OP)Deposit Team",
    "Settlement Team ",
    "(OP)Commission team",
    "Admin Team",
    "(OP) ASIC - Account Team",
    "BIT Team",
    "Risk Team - VIG",
    "(OP) ASIC - Deposit Team",
    "(OP) ASIC - Withdraw Team",
    "Trading Team",
    "Promotion Team",
    "(HA)Deposit Team",
    "No Group",
    "ASIC - Outlook",
    "(OP)FCA-Outlook",
    "ASIC - Trading Team",
    "FP Team",
]

# Every group name considered "known". A non-blank Group that is not in
# this list falls into "Other" (and shows up on the "Other Groups" QC
# sheet as a new/unexpected group worth reviewing).
KNOWN_GROUPS = (
    AC_GROUPS
    + [g for names in GROUP_MODULE_MAP.values() for g in names]
    + OTHER2_GROUPS
)

# Keyword-based modules: do NOT look at Group. A row counts if Tags
# contains the employee name AND contains the associated keyword
# (case-insensitive substring, no regex).
#
# NOTE: the output column is named "CPA-non-standard plan" but the
# keyword it searches for is "CPA Standard Commission Plan Update" --
# this mismatch between column name and keyword text is intentional,
# per the original spec. Do not "fix" it to search for
# "non-standard".
KEYWORD_RULES = {
    "CPA-Multi plan": "CPA Multi-Tier Commission Plan Update",
    "CPA-hybrid plan": "CPA Hybrid Commission Plan Update",
    "CPA-non-standard plan": "CPA Standard Commission Plan Update",
}

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
OUTPUT_FILENAME = "AC_Daily_Module_Report_20260618_20260831.xlsx"
MAIN_SHEET_NAME = "fresh Template Batch (AC)"

# ---------------------------------------------------------------------------
# VN5 report: same date range, same raw data, same module rules and
# output format as the main 55-employee report above -- just a
# separate, independent report scoped to these 5 employees only.
# Names are written in the exact word order confirmed to appear in the
# raw Tags data (verified against input data before use -- Vietnamese
# names in this data are family-name-first, e.g. "Nguyen Thi Xuan Lan",
# not "Thi Xuan Lan Nguyen").
# ---------------------------------------------------------------------------
VN5_EMPLOYEE_NAMES = [
    "Nguyen Thi Xuan Lan",
    "Bui Ngoc Van Anh",
    "Vo Hoang Thuan",
    "Ngo Thi Dieu Huyen",
    "Chau Ngoc Thinh",
]
VN5_OUTPUT_FILENAME = "VN5_Daily_Module_Report_20260618_20260831.xlsx"
VN5_MAIN_SHEET_NAME = "fresh Template Batch (AC)"

# ---------------------------------------------------------------------------
# Roster report: independent report using EVERY OP Name found in a given
# Roster export's first column (not the curated EMPLOYEE_NAMES list) as
# the employee list, for its own date range -- does not touch
# START_DATE/END_DATE/EMPLOYEE_NAMES above, which stay dedicated to the
# main 55-employee report.
# ---------------------------------------------------------------------------
ROSTER_REPORT_EMPLOYEE_LIST_FILE = INPUT_FOLDER / "Roster 202609.xlsx"
ROSTER_REPORT_START_DATE = "2026-09-01"
ROSTER_REPORT_END_DATE = "2026-09-30"
# Named after the date range automatically -- only edit the dates above.
ROSTER_REPORT_OUTPUT_FILENAME = f"AC Fresh Report {ROSTER_REPORT_START_DATE} - {ROSTER_REPORT_END_DATE}.xlsx"
ROSTER_REPORT_MAIN_SHEET_NAME = "fresh Template Batch (AC)"

# ---------------------------------------------------------------------------
# DW report (generate_dw_report.py): same input data, same employee-name
# matching (case-insensitive substring of Tags) and same date logic as the
# AC report, but its own 8 DW modules. Rules transcribed from the user's
# Excel formulas (2026-10-01), which reference the "AC DW Category" sheet:
#   D2 (OP)Withdrawal Team / D3:D5 (OP)Deposit Team, (HA)Deposit Team,
#   "Settlement Team " / D6 (OP)FCA-Tickets / D7 deposit bonus issue /
#   D9 Institutional Client Withdrawals / D10 Institutional Client Deposit /
#   D11 EXTRAOPWork
#
# Group comparisons are case-insensitive exact matches (Excel COUNTIF/MATCH).
# Keyword comparisons are case-insensitive substring searches in Tags (Excel
# SEARCH). Modules are not mutually exclusive, same as the AC report.
#
# NOTE: "Promo Fresh" searches only D7 ("deposit bonus issue"), not D8
# ("Promo") -- that is what the user's formula references.
# NOTE: "Other Fresh" = Group NOT in D2:D6 (blank Group included), so it
# also counts AC-side groups such as "(OP)Acc-Account Owner Transfer" --
# that is what the user's formula does.
# ---------------------------------------------------------------------------
DW_GROUP_MODULES = {
    "WD fresh": ["(OP)Withdrawal Team"],
    "DP fresh": ["(OP)Deposit Team", "(HA)Deposit Team", "Settlement Team "],
    "FCA Fresh": ["(OP)FCA-Tickets"],
}
# Groups D2:D6 -- a row whose Group is NOT one of these counts as "Other Fresh".
DW_OTHER_EXCLUDED_GROUPS = [
    "(OP)Withdrawal Team",
    "(OP)Deposit Team",
    "(HA)Deposit Team",
    "Settlement Team ",
    "(OP)FCA-Tickets",
]
DW_KEYWORD_MODULES = {
    "Promo Fresh": "deposit bonus issue",
    "Inst -WD": "Institutional Client Withdrawals",
    "Inst -DP": "Institutional Client Deposit",
    "EXTRAOPWork": "EXTRAOPWork",
}
DW_MODULE_ORDER = [
    "WD fresh",
    "DP fresh",
    "Promo Fresh",
    "Other Fresh",
    "Inst -WD",
    "Inst -DP",
    "FCA Fresh",
    "EXTRAOPWork",
]
DW_EMPLOYEE_LIST_FILE = INPUT_FOLDER / "Roster 202609.xlsx"
DW_START_DATE = "2026-09-01"
DW_END_DATE = "2026-09-30"
# Named after the date range automatically -- only edit the dates above.
DW_OUTPUT_FILENAME = f"DW Fresh Report {DW_START_DATE} - {DW_END_DATE}.xlsx"
DW_MAIN_SHEET_NAME = "fresh Template Batch (DW)"
