# md2m3u

Convert the [free-and-creative-commons-music](https://github.com/semareit/free-and-creative-commons-music)
tracklist into a ready-to-play **M3U playlist**.

The script downloads the `index.md` file from the source repository, parses the
tracklist table, and writes an `.m3u` file with one entry per track — including
artist, title, year, label, and the direct audio URL.

## Features

- Parses the markdown table (`[Artist - Title](URL) @ Year, Label`)
- Emits `#EXTINF` / `# @ Year, Label` / URL entries for every track
- Adds a comment header with source URL, creation timestamp, track count,
  and a short "about" block (hardcoded, easy to edit via `ABOUT_LINES`)
- Only uses the Python standard library — no dependencies

## Requirements

- Python **3.8+**

## Usage

```bash
# print playlist to stdout
python md2m3u.py

# write playlist to a file
python md2m3u.py playlist.m3u
```

# check link

A Python script that automatically checks every music link on
[**semareit.github.io/free-and-creative-commons-music**](https://semareit.github.io/free-and-creative-commons-music/)
for availability and reports dead or broken URLs.

The page lists a large collection of freely licensed music tracks
(Internet Archive, Broque, and others). Since direct links tend to rot over
time, this script helps keep the catalog clean.

## Features

- **Automatic link discovery** — parses the page and collects all unique URLs.
- **Efficient checks** via HTTP `HEAD` requests (no audio files are downloaded).
- **`GET` fallback** if a server doesn't support `HEAD` (`405 Method Not Allowed`).
- **Timeout and error handling** (timeouts, connection errors, DNS issues, …).
- **Polite crawling** — proper User-Agent and a 0.5 s delay between requests.
- **Optional logfile** — full report written to a file (`--log`).
- **Quiet mode** — log to file only (`--quiet`), perfect for cron jobs / CI.
- **Exit codes** for automation: `0` = all good, `2` = dead links found.

## Requirements

- Python **3.9+** (tested with 3.10 / 3.11 / 3.12)
- Internet connection


## Installation

```bash
# Clone the repository
git clone https://github.com/<YOUR-USER>/<YOUR-REPO>.git
cd <YOUR-REPO>

# (Optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requests>=2.31 beautifulsoup4>=4.12
```

## Usage

### 1. Standard run

```bash
python check_links.py
```

Prints progress and, at the end, a summary of all dead or broken links to the
console.

### 2. Also write the output to a logfile

```bash
python check_links.py --log report.log
```

or with the short flag:

```bash
python check_links.py -l report.log
```

Every log line includes a timestamp and a log level:

```
2026-11-22 14:03:11 [INFO] Fetching page: https://semareit.github.io/...
2026-11-22 14:03:12 [INFO] Found 412 unique links to check.
2026-11-22 14:03:15 [WARNING] - https://example.com/broken.mp3  [HTTP 404]
```

### 3. Write only to the logfile (keep the terminal clean)

```bash
python check_links.py --log report.log --quiet
```

### 4. Show all options

```bash
python check_links.py --help
```

| Option | Short | Description |
|---|---|---|
| `--log FILE` | `-l` | Also write the full report to `FILE`. |
| `--quiet` | `-q` | Suppress console output. |
| `--help` | `-h` | Show help. |


## Project structure

```
.
├── check_links.py       # The checker script
├── md2m3u.py            # Dependencies
├── playlist.m3u         # Dependencies
└── README.md            # This file
```

## Notes

- **Rate limits & fairness:** The script deliberately waits 0.5 s between
  requests. Please don't drastically reduce `DELAY` — it's there to avoid
  hammering third-party servers.
- **False negatives:** Some servers block automated requests or return
  different status codes for `HEAD` vs. `GET`. If in doubt, open the link
  manually in a browser.
- **`HEAD`-only checks:** **No audio files are downloaded** — only their HTTP
  status is inspected.
