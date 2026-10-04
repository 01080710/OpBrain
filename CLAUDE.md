# CLAUDE.md

Entry point for Claude Code in this repository. Everything — business rules,
procedures, scripts — lives in `brain/` (OpBrain format). This file only says
where to start and the rules that always apply.

## Read first, every session
1. `brain/README.md` — what the product is, which Skills exist
2. `brain/_core/conventions.md` — cross-Skill rules and working principles (must read)
3. The `skill.md` of the Skill the request belongs to — it maps what the user says to the exact command

Skills are also registered in `.claude/skills/` as thin auto-generated entries
(`brain/_tools/sync_claude_skills.py`); they only point back to `brain/<skill>/skill.md`.

## Running things
- Python: `.venv\Scripts\python.exe`, from the project root.
- Each Skill runs through `brain/<skill>/scripts/run_workflow.py --flow <name> ...`.
  Do not write new scripts for something a flow already does.
- Exit codes: 0 ok · 1 input error · 2 stopped by a quality gate (report what is missing, don't work around it) · 3 STOP file.

## Hard rules
- **Business rules are the user's call** (module mapping, Group renames, name mapping, scoring). Ask; don't guess.
- **Never produce a result that looks complete but isn't.** Gates stop the flow; report and stop.
- **Do not redesign validated logic** without explicit instruction, a baseline, and a passing
  `brain/productivity/scripts/regression_check.py`. The Power BI browser logic
  (`brain/productivity/scripts/_lib/pbi_browser.py`) is frozen (productivity DEC-001).
- **PBI login is manual** (MFA). Use `--flow open-browser` (opens Edge on port 9333, maximized); the user logs in.
- **Roster is owned by team-structure.** Read it only via `opbrain.roster`.
- **Real business data never goes into version control** (`data/`, `_archive` holds code only).
- After changing anything in `brain/`: run `brain/_tools/check_all.py`, log it with
  `brain/_tools/kb_log_change.py`, and record trade-offs in that Skill's `trace/decisions.md`.
