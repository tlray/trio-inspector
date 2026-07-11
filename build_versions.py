#!/usr/bin/env python3
"""Generate versioned snapshots of index.html + a versions.json manifest for GitHub Pages.

Each commit on the current branch that touched index.html becomes a "version". The newest
is the site root (index.html), so visiting the base URL always serves the latest build.
Older versions are written to versions/<epoch>-<shortsha>.html with a small fixed
"go to latest" banner injected, and listed (newest first) in versions.json — which the app
reads to populate its version selector.

Run from the repo root AFTER a full-history checkout (actions/checkout fetch-depth: 0):

    python3 build_versions.py _site
"""
import datetime
import json
import os
import subprocess
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "_site"
LIMIT = int(os.environ.get("VERSIONS_LIMIT", "20"))
VDIR = os.path.join(OUT, "versions")


def git(*args):
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    ).stdout


def banner(date):
    # position:fixed so it renders regardless of where in the (head-less) document it lands.
    return (
        '<div style="position:fixed;z-index:99999;right:12px;bottom:12px;'
        "background:#1b1b1b;color:#fff;font:600 12px system-ui,sans-serif;"
        "padding:8px 12px;border-radius:8px;box-shadow:0 2px 12px rgba(0,0,0,.35);"
        'max-width:calc(100vw - 24px)">\U0001f4cc Older version (' + date + " UTC) "
        '&middot; <a href="../" style="color:#7bb8ff;text-decoration:none">Go to latest '
        "&rarr;</a></div>"
    )


def main():
    os.makedirs(VDIR, exist_ok=True)
    # commits that changed index.html, newest first: <sha>\x1f<short>\x1f<epoch>\x1f<subject>
    log = git("log", f"-{LIMIT}", "--format=%H%x1f%h%x1f%ct%x1f%s", "--", "index.html")
    rows = [l.split("\x1f") for l in log.splitlines() if l.strip()]

    manifest = []
    for i, parts in enumerate(rows):
        if len(parts) != 4:
            continue
        sha, short, ts, subject = parts
        ts = int(ts)
        date = datetime.datetime.fromtimestamp(
            ts, datetime.timezone.utc
        ).strftime("%Y-%m-%d %H:%M")
        is_current = i == 0
        entry = {"ts": ts, "date": date, "short": short, "subject": subject, "file": None}
        if not is_current:
            try:
                content = git("show", f"{sha}:index.html")
            except subprocess.CalledProcessError:
                continue  # index.html absent at this commit; skip
            fname = f"{ts}-{short}.html"
            with open(os.path.join(VDIR, fname), "w", encoding="utf-8") as f:
                f.write(content + "\n" + banner(date) + "\n")
            entry["file"] = f"versions/{fname}"
        manifest.append(entry)

    with open(os.path.join(OUT, "versions.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=0)
    print(f"wrote {len(manifest)} versions to {OUT}/versions.json")


if __name__ == "__main__":
    main()
