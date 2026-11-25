#!/usr/bin/env python3
"""
Convert the markdown tracklist from
https://github.com/semareit/free-and-creative-commons-music/blob/main/index.md
into an M3U playlist.

The header of the playlist contains a hardcoded comment block
together with the source URL and the creation date.

Usage:
    python md2m3u.py [output_file]
    If no output file is given, the playlist is printed to stdout.
"""

import re
import sys
import urllib.request
from datetime import datetime, timezone

SOURCE_URL = (
    "https://raw.githubusercontent.com/semareit/"
    "free-and-creative-commons-music/main/index.md"
)
SOURCE_REPO = (
    "https://github.com/semareit/free-and-creative-commons-music"
)

# ---- hardcoded "about" text (written as comment lines) -------------------- #
ABOUT_LINES = [
    "Free and Creative Commons Music",
    "",
    "A curated collection of freely licensed music, gathered from the",
    "semareit/free-and-creative-commons-music repository on GitHub.",
    "",
    "All tracks are published under free or Creative Commons licenses.",
    "Please respect the terms of each individual license.",
]

ROW_PATTERN = re.compile(
    r"\[(?P<link_text>.*?)\]\((?P<url>.*?)\)"          # [Artist - Title](URL)
    r"(?:\s*@\s*(?P<year>\d{4}),\s*(?P<label>.+))?"    # optional @ Year, Label
)


# --------------------------------------------------------------------------- #
# Fetch
# --------------------------------------------------------------------------- #
def fetch_markdown(url: str) -> str:
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode("utf-8")


# --------------------------------------------------------------------------- #
# Parse the tracklist table
# --------------------------------------------------------------------------- #
def parse_tracks(md_text: str):
    for line in md_text.splitlines():
        if not line.startswith("|") or "](" not in line:
            continue
        if re.match(r"^\|\s*:?-{3,}", line):        # header separator row
            continue

        first_cell = line.split("|")[1].strip()
        match = ROW_PATTERN.search(first_cell)
        if not match:
            continue

        link_text = match.group("link_text").strip()
        url       = match.group("url").strip()
        year      = match.group("year")
        label     = match.group("label")

        if " - " in link_text:
            artist, title = link_text.split(" - ", 1)
        else:
            artist, title = link_text, ""

        yield {
            "artist": artist.strip(),
            "title":  title.strip(),
            "url":    url,
            "year":   year.strip()  if year  else None,
            "label":  label.strip() if label else None,
        }


# --------------------------------------------------------------------------- #
# Write the playlist
# --------------------------------------------------------------------------- #
def generate_m3u(tracks, output_file=None):
    out = open(output_file, "w", encoding="utf-8") if output_file else sys.stdout
    now = datetime.now(timezone.utc).astimezone()

    try:
        # ---- header ------------------------------------------------------ #
        out.write("#EXTM3U\n")
        out.write(f"# Playlist generated from: {SOURCE_REPO}\n")
        out.write(f"# Source file: {SOURCE_URL}\n")
        out.write(f"# Created: {now.isoformat(timespec='seconds')}\n")
        out.write(f"# Tracks:  {len(tracks)}\n")
        out.write("#\n# About:\n")
        for ln in ABOUT_LINES:
            out.write(f"# {ln}\n" if ln else "#\n")
        out.write("#\n")

        # ---- entries ----------------------------------------------------- #
        for tr in tracks:
            display = f"{tr['artist']} - {tr['title']} ({tr['year']}, {tr['label']})".strip()
            out.write(f"#EXTINF:-1,{display}\n")

            #comment_parts = []
            #if tr["year"]:
            #    comment_parts.append(tr["year"])
            #if tr["label"]:
            #    comment_parts.append(tr["label"])
            #if comment_parts:
            #    out.write(f"# @ {', '.join(comment_parts)}\n")

            out.write(tr["url"] + "\n")
    finally:
        if out is not sys.stdout:
            out.close()


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    md_text     = fetch_markdown(SOURCE_URL)
    tracks      = list(parse_tracks(md_text))

    generate_m3u(tracks, output_file)

    if output_file:
        print(f"Playlist written to {output_file} ({len(tracks)} tracks)",
              file=sys.stderr)


if __name__ == "__main__":
    main()
