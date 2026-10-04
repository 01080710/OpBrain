"""具名流程的共用執行器。各 Skill 的 scripts/run_workflow.py 定義流程（步驟清單），
由這裡依序執行。

- 每個步驟是一支獨立腳本（子程序），以結束碼回報：0 成功｜1 輸入錯誤｜2 關卡擋下｜3 緊急停止
- 任何步驟非 0 → 立即停止，後續步驟一律不執行（回到安全狀態）
- 每個步驟開始前檢查 <workdir>/STOP；存在就停止（結束碼 3）
- 紀錄寫在 <workdir>/run_log.json（每步：狀態、結束碼、秒數；沒執行的標為 skipped）
"""
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from .common import EXIT_OK, EXIT_STOPPED, write_json

STATUS = {0: "ok", 1: "error", 2: "gate_blocked", 3: "stopped"}


@dataclass
class Step:
    act: str                 # 動作 ID，例如 "ACT-02"
    script: str              # scripts/ 底下的檔名
    args: list = field(default_factory=list)
    retries: int = 1         # 結束碼 2 時最多執行幾次（用於會暫時失敗的下載）


def run_steps(script_dir: Path, steps, workdir: Path, flow: str) -> int:
    workdir = Path(workdir)
    stop_file = workdir / "STOP"
    log = {"flow": flow, "workdir": str(workdir), "steps": [
        {"step": s.act, "script": s.script, "status": "skipped", "exit_code": None,
         "seconds": None, "attempts": 0} for s in steps]}
    exit_code = EXIT_OK

    for entry, step in zip(log["steps"], steps):
        if stop_file.exists():
            print(f"STOP file found: halting before {step.act}")
            exit_code = EXIT_STOPPED
            break
        cmd = [sys.executable, str(script_dir / step.script), "--workdir", str(workdir), *step.args]
        t0 = time.monotonic()
        code = None
        for attempt in range(1, step.retries + 1):
            label = f" (attempt {attempt}/{step.retries})" if step.retries > 1 else ""
            print(f"\n=== {step.act} {step.script}{label} ===", flush=True)
            code = subprocess.run(cmd).returncode
            entry["attempts"] = attempt
            if code != 2 or stop_file.exists():
                break
        entry.update(status=STATUS.get(code, "error"), exit_code=code,
                     seconds=round(time.monotonic() - t0, 1))
        write_json(workdir / "run_log.json", log)
        if code != EXIT_OK:
            exit_code = code
            break

    write_json(workdir / "run_log.json", log)
    return exit_code
