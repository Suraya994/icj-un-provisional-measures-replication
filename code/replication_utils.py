"""Shared helpers for the replication package (standard library only)."""
from pathlib import Path
import csv
import datetime as dt
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

P5_PREFIXES = ("United States", "United Kingdom", "France", "Russian Federation", "China")
TITLE_PATTERN = re.compile(r"\(([^()]*?)\s+v\.\s+([^()]*)\)\s*$")


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_date(text):
    return dt.date.fromisoformat(text.strip()[:10])


def parse_parties(case_title):
    """Return (applicant, respondent) parsed from the trailing '(A v. B)' of a case title.

    This is a *derived* helper. It reads only the case title string and does not use
    any human-coded field. Returns (None, None) when the title has no 'v.' pattern.
    """
    match = TITLE_PATTERN.search(case_title.strip())
    if not match:
        return None, None
    return match.group(1).strip(), match.group(2).strip()


def is_p5(state_name):
    return bool(state_name) and state_name.startswith(P5_PREFIXES)


def percent(numerator, denominator, digits=1):
    return round(100.0 * numerator / denominator, digits)
