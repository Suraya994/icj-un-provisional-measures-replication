#!/usr/bin/env python3
"""Numbers that appear in the paper's text but were not produced by reproduce_published_results.py.

Writes (all derived, none overwrite coded data):
  outputs/tables/table_5_sensitivity_sample_rates.csv   engagement rate, primary (N=24) and sensitivity (N=27)
  outputs/tables/table_6_permanent_member_respondents.csv  descriptive P5-respondent cross-tabulation
  outputs/derived/ORDER_PARTIES_DERIVED_FROM_CASE_TITLES.csv  applicant / respondent parsed from case_title

The respondent variable is DERIVED by string-parsing the trailing '(A v. B)' of each case title.
It is not a human-coded field and should be checked by the author before being cited.
"""
from replication_utils import ROOT, DATA, read_csv, write_csv, parse_parties, is_p5, percent

orders = read_csv(DATA / "05_results/ORDER_LEVEL_RESULTS_41_CANONICAL.csv")
primary = [r for r in orders if r["primary_sample"] == "1"]
sens = [r for r in orders if r["sensitivity_sample"] == "1"]

# Table 5: order-specific engagement rate in the two analytical samples.
def eng(sample):
    return sum(int(r["order_specific_engagement_final"]) for r in sample)

write_csv(ROOT / "outputs/tables/table_5_sensitivity_sample_rates.csv", [
    {"sample": "primary", "orders": len(primary), "engaged": eng(primary), "rate_percent": percent(eng(primary), len(primary))},
    {"sample": "sensitivity", "orders": len(sens), "engaged": eng(sens), "rate_percent": percent(eng(sens), len(sens))},
])

# Derived parties for all 41 orders.
derived = []
for r in orders:
    applicant, respondent = parse_parties(r["case_title"])
    derived.append({
        "order_id": r["order_id"], "case_number": r["case_number"], "primary_sample": r["primary_sample"],
        "applicant_parsed": applicant or "", "respondent_parsed": respondent or "",
        "respondent_is_p5": "" if respondent is None else int(is_p5(respondent)),
        "derivation": "parsed from case_title, not human-coded",
    })
write_csv(ROOT / "outputs/derived/ORDER_PARTIES_DERIVED_FROM_CASE_TITLES.csv", derived)
unparsed = [d["order_id"] for d in derived if d["primary_sample"] == "1" and d["respondent_parsed"] == ""]
assert not unparsed, f"unparsed primary titles: {unparsed}"

# Table 6: permanent-member respondents among the 24 primary orders.
engaged = {r["order_id"]: int(r["order_specific_engagement_final"]) for r in primary}
prim_derived = [d for d in derived if d["primary_sample"] == "1"]
def summarise(label, group):
    return {"respondent_group": label, "orders": len(group), "engaged": sum(engaged[d["order_id"]] for d in group)}
p5 = [d for d in prim_derived if d["respondent_is_p5"] == 1]
rows = [summarise("any permanent member (US, UK, France, Russia, China)", p5),
        summarise("  of which Russian Federation", [d for d in p5 if d["respondent_parsed"].startswith("Russian")]),
        summarise("  of which United States", [d for d in p5 if d["respondent_parsed"].startswith("United States")]),
        summarise("  of which France", [d for d in p5 if d["respondent_parsed"].startswith("France")]),
        summarise("non-permanent member", [d for d in prim_derived if d["respondent_is_p5"] == 0])]
write_csv(ROOT / "outputs/tables/table_6_permanent_member_respondents.csv", rows)
for row in rows:
    print(row)
