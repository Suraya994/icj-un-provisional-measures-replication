#!/usr/bin/env python3
"""Regenerate RELEASE_MANIFEST.json and SHA256SUMS.txt. Run after any edit and before committing."""
import hashlib
import json
import os
from replication_utils import ROOT

SKIP_DIRS = {".git", "__pycache__", "_tmp", ".venv"}
SKIP_FILES = {"SHA256SUMS.txt", "RELEASE_MANIFEST.json", ".DS_Store"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


files = []
for base, dirs, names in os.walk(ROOT):
    dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
    for name in sorted(names):
        if name in SKIP_FILES or name.endswith(".pyc"):
            continue
        p = os.path.join(base, name)
        files.append(os.path.relpath(p, ROOT).replace(os.sep, "/"))
files.sort()
manifest = {"package_version": "1.1.0", "created": "2026-10-08",
            "status": "RELEASE_CANDIDATE_WITH_OPEN_AUTHOR_ITEMS (see docs/OPEN_ITEMS.md)",
            "files": [{"path": f, "bytes": os.path.getsize(ROOT / f), "sha256": sha256(ROOT / f)} for f in files]}
(ROOT / "RELEASE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
lines = [f"{sha256(ROOT / f)}  {f}" for f in files + ["RELEASE_MANIFEST.json"]]
lines.sort(key=lambda s: s.split("  ", 1)[1])
(ROOT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(len(lines), "files hashed")
