#!/usr/bin/env python3
"""Re-verify the archived UN PDFs against the digests recorded in the release.

Usage: python code/verify_source_hashes.py --pdf-dir /path/to/folder/with/PDFs

The PDFs are not redistributed here. This script lets anyone who has downloaded the official files
re-check them. It writes outputs/source_hash_verification.csv and prints a summary.
"""
import argparse
import hashlib
from pathlib import Path
from replication_utils import ROOT, DATA, read_csv, write_csv


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument("--pdf-dir", required=True)
args = parser.parse_args()
folder = Path(args.pdf_dir)
rows = []
for r in read_csv(DATA / "06_sources/SOURCE_INTEGRITY_VERIFICATION_137.csv"):
    f = folder / r["archive_pdf_filename"]
    if not f.exists():
        status, digest = "MISSING", ""
    else:
        digest = sha256(f)
        status = "MATCH" if digest == r["expected_sha256"] else "MISMATCH"
    rows.append({"archive_pdf_filename": r["archive_pdf_filename"], "expected_sha256": r["expected_sha256"],
                 "observed_sha256": digest, "status": status})
write_csv(ROOT / "outputs/source_hash_verification.csv", rows)
counts = {s: sum(1 for x in rows if x["status"] == s) for s in ("MATCH", "MISMATCH", "MISSING")}
print(counts)
