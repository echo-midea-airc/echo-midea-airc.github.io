"""
Download missing files from MaverickRen/VideoWorld2.github.io (static/ only).
Skips blobs that already exist with expected size (from GitHub tree API).
Run from repo root: python fetch_static.py
"""
from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.error
import urllib.request

REPO = "MaverickRen/VideoWorld2.github.io"
BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/"
TREE_API = f"https://api.github.com/repos/{REPO}/git/trees/{BRANCH}?recursive=1"


def main() -> int:
    root = os.path.dirname(os.path.abspath(__file__))
    ctx = ssl.create_default_context()
    req = urllib.request.Request(TREE_API, headers={"User-Agent": "fetch_static.py"})
    with urllib.request.urlopen(req, context=ctx, timeout=120) as r:
        tree = json.load(r)["tree"]

    blobs = [
        t
        for t in tree
        if t["type"] == "blob"
        and str(t["path"]).startswith("static/")
        and not str(t["path"]).endswith(".DS_Store")
    ]

    for i, t in enumerate(blobs, 1):
        path = t["path"]
        expected = int(t["size"])
        dest = os.path.join(root, *path.split("/"))
        if os.path.isfile(dest) and os.path.getsize(dest) == expected:
            print(f"[{i}/{len(blobs)}] skip {path}")
            continue

        url = RAW_BASE + path.replace("\\", "/")
        print(f"[{i}/{len(blobs)}] fetch {path} ({expected} bytes) ...")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        tmp = dest + ".part"
        try:
            rreq = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(rreq, context=ctx, timeout=900) as resp:
                data = resp.read()
            if len(data) != expected:
                print(f"  WARN size mismatch got {len(data)} expected {expected}")
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, dest)
            print(f"  ok {len(data)} bytes")
        except (urllib.error.URLError, OSError) as e:
            print(f"  FAIL {e}", file=sys.stderr)
            if os.path.isfile(tmp):
                os.remove(tmp)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
