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
