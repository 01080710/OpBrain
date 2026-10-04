"""
Power BI login / session bootstrap.

MFA cannot be automated -- this module only launches Microsoft Edge
with a remote debugging port (or reuses one already running and
already logged in) and waits for a human to finish logging in.

Detecting "login is done" is delegated to a separate subprocess
(_pbi_login_wait.py) rather than done in-process. Two things forced
that design, both found the hard way:
  1. Playwright's sync API forbids opening a second sync_playwright()
     instance in the same thread/process, so this process (which
     launched the browser) cannot also open a second connection to
     poll it.
  2. Reading page.url from *the launching connection's own* Page
     object was observed to stop reflecting reality partway through a
     multi-domain OAuth/MFA redirect chain -- it can sit there
     unchanged for the entire timeout even though the browser has long
     since finished redirecting. A fresh connect_over_cdp() connection
     (which is what the subprocess uses) does not have this problem.

IMPORTANT: the (playwright, browser) pair returned by ensure_logged_in()
must be kept referenced by the caller for as long as the browser
should stay open -- on Windows, the launched browser's lifetime is
tied to its launching process, so letting that process/connection go
away closes the browser.
"""

import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from config.settings import PBI_REPORT_URL

REMOTE_DEBUGGING_PORT = 9333
LOGIN_TIMEOUT_SECONDS = 10 * 60

AUTH_URL_MARKERS = (
    "login.microsoftonline.com",
    "login.live.com",
    "singleSignOn",
    "/oauth2/",
    "/authorize",
)

_WAIT_SCRIPT = str(Path(__file__).parent / "_pbi_login_wait.py")


def _is_auth_url(url: str) -> bool:
    return any(marker in url for marker in AUTH_URL_MARKERS)


def _try_reuse_existing_session():
    """
    Try attaching to an already-running, already-logged-in session.
    Returns (playwright, browser) if usable, else (None, None). Never
    raises -- any failure just means "not usable, launch a fresh one".
    """
    try:
        p = sync_playwright().start()
    except Exception:
        return None, None
    try:
        browser = p.chromium.connect_over_cdp(
            f"http://localhost:{REMOTE_DEBUGGING_PORT}", timeout=5000
        )
        if not browser.contexts or not browser.contexts[0].pages:
            p.stop()
            return None, None
        page = browser.contexts[0].pages[0]
        if _is_auth_url(page.url):
            p.stop()
            return None, None
        return p, browser
    except Exception:
        p.stop()
        return None, None


def ensure_logged_in():
    """
    Returns (playwright, browser) for an authenticated Power BI Edge
    session on REMOTE_DEBUGGING_PORT.

    Reuses an existing valid session if one is already open and not
    sitting on a login page; otherwise launches a new Edge window and
    blocks (up to LOGIN_TIMEOUT_SECONDS) waiting for the user to
    complete login + MFA by hand.
    """
    p, browser = _try_reuse_existing_session()
    if browser is not None:
        print("[login] Reusing existing logged-in session.", flush=True)
        return p, browser

    if not PBI_REPORT_URL:
        raise SystemExit("PBI_REPORT_URL is not set in .env")

    print("[login] Launching Edge for manual login...", flush=True)
    p = sync_playwright().start()
    browser = p.chromium.launch(
        channel="msedge",
        headless=False,
        args=[f"--remote-debugging-port={REMOTE_DEBUGGING_PORT}"],
    )
    context = browser.new_context()
    page = context.new_page()
    page.goto(PBI_REPORT_URL, timeout=60000)

    print(
        f"[login] Please complete login + MFA in the Edge window "
        f"(waiting up to {LOGIN_TIMEOUT_SECONDS // 60} minutes)...",
        flush=True,
    )

    result = subprocess.run(
        [sys.executable, _WAIT_SCRIPT, str(LOGIN_TIMEOUT_SECONDS)],
        capture_output=True,
        text=True,
        timeout=LOGIN_TIMEOUT_SECONDS + 30,
    )

    if result.returncode == 0 and result.stdout.strip().startswith("READY:"):
        landed_on = result.stdout.strip().split("READY:", 1)[1]
        print(f"[login] Logged in. Landed on: {landed_on}", flush=True)
        return p, browser

    p.stop()
    raise TimeoutError(
        "Timed out waiting for manual login to complete. "
        f"wait-process stdout={result.stdout!r} stderr={result.stderr!r}"
    )


if __name__ == "__main__":
    ensure_logged_in()
    print("[login] Session ready. Leave this window open.", flush=True)
