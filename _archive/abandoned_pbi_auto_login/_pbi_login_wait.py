"""
Internal helper for pbi_login.py -- NOT a public entry point.

Runs as a separate OS process (spawned via subprocess by
ensure_logged_in()) to poll the Power BI login page's URL via its own
fresh CDP connection, until it settles on a non-auth page or times
out.

This exists because Playwright's sync API forbids more than one
sync_playwright() instance per thread/process, so the process that
launched the browser cannot also open a second connection to poll it
-- and empirically, reading page.url from *that same launching
connection's* Page object stops reflecting reality partway through a
multi-domain OAuth/MFA redirect chain (a fresh connect_over_cdp()
connection does not have this problem).

Prints "READY:<url>" and exits 0 on success; exits 1 on timeout.
"""

import sys
import time

from playwright.sync_api import sync_playwright

REMOTE_DEBUGGING_PORT = 9333
STABLE_SECONDS = 6
POLL_INTERVAL_SECONDS = 1.0

AUTH_URL_MARKERS = (
    "login.microsoftonline.com",
    "login.live.com",
    "singleSignOn",
    "/oauth2/",
    "/authorize",
)


def _is_auth_url(url: str) -> bool:
    return any(marker in url for marker in AUTH_URL_MARKERS)


def main():
    timeout_seconds = float(sys.argv[1])
    deadline = time.monotonic() + timeout_seconds

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://localhost:{REMOTE_DEBUGGING_PORT}")

        def _url():
            # Re-fetch the page from context.pages each time rather
            # than holding a single Page reference across the whole
            # wait -- belt-and-suspenders against the same kind of
            # staleness this whole subprocess exists to avoid.
            pages = browser.contexts[0].pages
            return pages[0].url if pages else None

        last_url = _url()
        stable_since = time.monotonic()
        while time.monotonic() < deadline:
            time.sleep(POLL_INTERVAL_SECONDS)
            current = _url()
            if current is None:
                continue
            if current != last_url:
                last_url = current
                stable_since = time.monotonic()
                continue
            if not _is_auth_url(current) and (time.monotonic() - stable_since) >= STABLE_SECONDS:
                print(f"READY:{current}", flush=True)
                sys.exit(0)

    sys.exit(1)


if __name__ == "__main__":
    main()
