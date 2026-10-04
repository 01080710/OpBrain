#!/usr/bin/env python3
"""
ACT-07  開啟 Power BI 登入用的 Edge 視窗

職責：用獨立設定檔開一個帶除錯 port 的 Edge（不影響使用者原本的 Edge），
      直接打開 .env 的 PBI_REPORT_URL，並把視窗最大化。登入與 MFA 仍由使用者手動完成。
      若該 port 已有 Edge 在跑，只做最大化。

文件對應：sources.md A（步驟）R-001、R-011（視窗必須最大化）、
          trace/issues.md INV-001（視窗太小導致找不到「更多選項」按鈕）
輸出：<workdir>/browser.json
結束碼：0 成功   1 找不到 Edge / 未設定 PBI_REPORT_URL / port 未啟動

用法：python pbi_open_browser.py --workdir <dir>
"""
import argparse
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

import _bootstrap  # noqa: F401
from opbrain import env
from opbrain.common import InputError, add_workdir, run, write_json
from pbi_common import cfg

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def _port_up(port):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def _maximize(port):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(f"http://localhost:{port}")
        pages = [pg for c in b.contexts for pg in c.pages]
        if not pages:
            return None
        s = pages[0].context.new_cdp_session(pages[0])
        w = s.send("Browser.getWindowForTarget")
        s.send("Browser.setWindowBounds", {"windowId": w["windowId"], "bounds": {"windowState": "maximized"}})
        return s.send("Browser.getWindowForTarget")["bounds"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    add_workdir(ap)
    args = ap.parse_args()
    port = cfg()["remote_debugging_port"]

    launched = False
    if not _port_up(port):
        url = env.get("PBI_REPORT_URL")
        if not url:
            raise InputError("PBI_REPORT_URL is not set in .env")
        edge = next((p for p in EDGE_PATHS if Path(p).exists()), None)
        if edge is None:
            raise InputError("Microsoft Edge not found")
        profile = os.path.expandvars(cfg()["edge_profile_dir"])
        subprocess.Popen([edge, f"--remote-debugging-port={port}", f"--user-data-dir={profile}",
                          "--no-first-run", url])
        launched = True
        for _ in range(30):
            if _port_up(port):
                break
            time.sleep(1)
        else:
            raise InputError(f"Edge did not open debug port {port}")

    bounds = _maximize(port)
    write_json(args.workdir / "browser.json", {"port": port, "launched": launched, "bounds": bounds})
    print(json.dumps({"launched": launched, "maximized": bounds}, ensure_ascii=False))
    print("請在 Edge 視窗手動登入 Power BI（含 MFA），看到報表後再執行下載。")
    return 0


if __name__ == "__main__":
    run(main)
