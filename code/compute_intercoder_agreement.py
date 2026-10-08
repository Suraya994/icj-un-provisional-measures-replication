#!/usr/bin/env python3
"""Inter-coder agreement between the first coding and a second, independent coding.

Usage:
  python code/compute_intercoder_agreement.py --second PATH_TO_SECOND_CODER_CSV [--out outputs/agreement]

The second-coder file must contain the columns 'stage6_pair_key' and 'link_code' (see
docs/templates/SECOND_CODER_BLIND_TEMPLATE_233.csv). Only rows present in both files are compared.
No second-coder data ship with this package. Second coding is a post-publication revalidation and
must not be described as part of the published analysis.
"""
import argparse
import collections
import json
from pathlib import Path
from replication_utils import ROOT, DATA, read_csv, write_csv


def observed_agreement(a, b):
    return sum(x == y for x, y in zip(a, b)) / len(a)


def cohen_kappa(a, b):
    n = len(a)
    po = observed_agreement(a, b)
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum((ca[k] / n) * (cb[k] / n) for k in set(a) | set(b))
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def gwet_ac1(a, b):
    """Gwet's AC1 for two raters and nominal categories. More stable than kappa under skewed prevalence."""
    n = len(a)
    cats = sorted(set(a) | set(b))
    q = len(cats)
    if q < 2:
        return float("nan")
    po = observed_agreement(a, b)
    ca, cb = collections.Counter(a), collections.Counter(b)
    pi = {k: (ca[k] + cb[k]) / (2 * n) for k in cats}
    pe = sum(p * (1 - p) for p in pi.values()) / (q - 1)
    return (po - pe) / (1 - pe)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--first", default=str(DATA / "04_human_coding/MANUAL_REVIEW_233_HUMAN.csv"))
    parser.add_argument("--second", required=True)
    parser.add_argument("--out", default=str(ROOT / "outputs/agreement"))
    args = parser.parse_args()
    first = {r["stage6_pair_key"]: r["final_link_code"] for r in read_csv(args.first)}
    second = {r["stage6_pair_key"]: r["link_code"].strip() for r in read_csv(args.second) if r.get("link_code", "").strip()}
    keys = sorted(set(first) & set(second))
    if not keys:
        raise SystemExit("No overlapping, completed rows between the two files.")
    a, b = [first[k] for k in keys], [second[k] for k in keys]
    confusion = collections.Counter(zip(a, b))
    summary = {
        "pairs_compared": len(keys),
        "observed_agreement": round(observed_agreement(a, b), 4),
        "cohen_kappa": round(cohen_kappa(a, b), 4),
        "gwet_ac1": round(gwet_ac1(a, b), 4),
        "first_coder_code3": a.count("3"),
        "second_coder_code3": b.count("3"),
        "both_code3": sum(1 for x, y in zip(a, b) if x == y == "3"),
        "note": "Code 3 is rare in the first coding. Report agreement on code 3 separately and do not rely on kappa alone.",
    }
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "agreement_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_csv(out / "confusion_first_vs_second.csv",
              [{"first_code": f, "second_code": s, "n": n} for (f, s), n in sorted(confusion.items())])
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
