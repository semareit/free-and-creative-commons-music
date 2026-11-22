import argparse
import logging
import sys
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# --- Configuration ---
PAGE_URL = "https://semareit.github.io/free-and-creative-commons-music/"
TIMEOUT = 10
DELAY = 0.5
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

log = logging.getLogger("linkchecker")


def setup_logging(logfile: str | None, quiet: bool) -> None:
    """Configure logging to console (and optionally a file)."""
    log.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

    # Console handler (unless --quiet)
    if not quiet:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(fmt)
        log.addHandler(ch)

    # Optional file handler
    if logfile:
        fh = logging.FileHandler(logfile, mode="w", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        log.addHandler(fh)


def get_all_links(page_url: str) -> list[str]:
    log.info("Fetching page: %s", page_url)
    try:
        response = requests.get(page_url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        log.error("Error fetching the main page: %s", e)
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = {urljoin(page_url, a["href"]) for a in soup.find_all("a", href=True)}
    log.info("Found %d unique links to check.", len(links))
    return sorted(links)


def check_link(url: str):
    try:
        response = requests.head(url, headers=HEADERS, timeout=TIMEOUT,
                                 allow_redirects=True)
        if response.status_code == 405:  # server refuses HEAD -> try GET
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT,
                                    allow_redirects=True, stream=True)
            response.close()

        code = response.status_code
        if 200 <= code < 300:
            return "OK", code, None
        return "DEAD", code, None
    except requests.exceptions.Timeout:
        return "ERROR", None, "Timeout"
    except requests.exceptions.ConnectionError:
        return "ERROR", None, "Connection Error"
    except requests.RequestException as e:
        return "ERROR", None, str(e)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check all links on the free CC music page."
    )
    parser.add_argument(
        "-l", "--log", metavar="FILE",
        help="Write the full report to FILE (in addition to stdout).",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help="Suppress console output (useful with --log).",
    )
    args = parser.parse_args()

    setup_logging(args.log, args.quiet)

    all_links = get_all_links(PAGE_URL)
    if not all_links:
        return 1

    dead: list[tuple[str, object]] = []
    log.info("Checking links...")

    for i, link in enumerate(all_links, 1):
        log.debug("[%d/%d] Checking: %s", i, len(all_links), link)
        status, code, err = check_link(link)

        if status == "DEAD":
            log.warning("  -> DEAD (HTTP %s)", code)
            dead.append((link, f"HTTP {code}"))
        elif status == "ERROR":
            log.warning("  -> ERROR: %s", err)
            dead.append((link, f"ERROR: {err}"))
        else:
            log.debug("  -> OK (HTTP %s)", code)

        time.sleep(DELAY)

    log.info("=" * 50)
    log.info("SUMMARY OF DEAD OR BROKEN LINKS")
    log.info("=" * 50)
    if dead:
        for link, reason in dead:
            log.info("- %s  [%s]", link, reason)
    else:
        log.info("All links appear to be alive!")

    if args.log:
        log.info("Full report written to: %s", args.log)

    return 0 if not dead else 2


if __name__ == "__main__":
    sys.exit(main())