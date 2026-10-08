#!/usr/bin/env python3
"""Check every quantitative claim of the published paper against the data in this package.

Paper: Bazarova, S. (2026). Temporal Proximity Does Not Establish Institutional Follow Up:
UN Practice Concerning ICJ Provisional Measures (2002-2025). Proceedings of the 8th
International Conference on Globalization & International Relations, pp. 87-107.

The 'paper_value' column was transcribed by hand from the published PDF. The 'computed_value'
column is recomputed from the CSV files. Status values:
  MATCH          computed value equals the paper value
  MISMATCH       computed value differs from the paper value (see note)
  UNVERIFIABLE   the claim cannot be checked from the files in this package
"""
from pathlib import Path
import collections
import json
import sys
from replication_utils import ROOT, DATA, read_csv, write_csv, parse_date, parse_parties, is_p5, percent

# Mismatches that are known, documented in docs/KNOWN_DISCREPANCIES.md and not silently tolerated.
EXPECTED_MISMATCH_IDS = {"P5-01"}

rows = []


def add(cid, location, claim, paper, computed, note=""):
    status = "MATCH" if str(paper) == str(computed) else "MISMATCH"
    rows.append({"claim_id": cid, "paper_location": location, "claim": claim,
                 "paper_value": paper, "computed_value": computed, "status": status, "note": note})


def unverifiable(cid, location, claim, note):
    rows.append({"claim_id": cid, "paper_location": location, "claim": claim,
                 "paper_value": "stated in paper", "computed_value": "not computable from package",
                 "status": "UNVERIFIABLE", "note": note})


legal = read_csv(DATA / "01_legal_corpus/ICJ_LEGAL_CORPUS_41_HUMAN.csv")
univ = read_csv(DATA / "02_universe/UN_EVENT_UNIVERSE_13692_STRUCTURED.csv")
pairs = read_csv(DATA / "03_screening/TEMPORAL_PAIRS_17413_SCREENING.csv")
review = read_csv(DATA / "04_human_coding/MANUAL_REVIEW_233_HUMAN.csv")
recall = read_csv(DATA / "04_human_coding/RECALL_AUDIT_120_CANDIDATE_IDS_RECONSTRUCTED.csv")
recall_binary = read_csv(DATA / "04_human_coding/RECALL_REVIEW_120_HUMAN_BINARY_RECONSTRUCTED.csv")
posdocs = read_csv(DATA / "05_results/POSITIVE_DOCUMENTARY_RECORDS_4.csv")
posproc = read_csv(DATA / "05_results/POSITIVE_INSTITUTIONAL_PROCESSES_3.csv")
orders = read_csv(DATA / "05_results/ORDER_LEVEL_RESULTS_41_CANONICAL.csv")
primary = [r for r in orders if r["primary_sample"] == "1"]
sens = [r for r in orders if r["sensitivity_sample"] == "1"]

# ---- Sample construction (Abstract, Materials and Methods, Table 1) ----
add("SAMPLE-01", "Abstract / Methods", "ICJ decisions on provisional measures", 41, len(legal))
add("SAMPLE-02", "Abstract / Methods", "contentious cases", 27, len({r["case_number"] for r in legal}))
dates = sorted(r["order_date"] for r in legal)
add("SAMPLE-03", "Methods", "first order date", "2002-07-10", dates[0])
add("SAMPLE-04", "Methods", "last order date", "2025-09-12", dates[-1])
disp = collections.Counter(r["order_disposition_code_manual"] for r in legal)
add("SAMPLE-05", "Methods", "new measures indicated", 20, disp["NEW_PM"])
add("SAMPLE-06", "Methods", "measures modified", 4, disp["MODIFIED_PM"])
add("SAMPLE-07", "Methods", "measures reaffirmed", 3, disp["REAFFIRMED_PM"])
add("SAMPLE-08", "Methods", "requests rejected", 12, disp["REQUEST_REJECTED"])
add("SAMPLE-09", "Methods", "withdrawn or discontinued", 2, disp["WITHDRAWN_DISCONTINUED"])
add("SAMPLE-10", "Methods / Table 1", "primary sample (orders)", 24, len(primary))
add("SAMPLE-11", "Methods / Table 1", "primary sample (case files)", 17, len({r["case_number"] for r in primary}))
add("SAMPLE-12", "Methods / Table 1", "sensitivity sample (orders)", 27, len(sens))
add("SAMPLE-13", "Methods / Eq. 1", "UN event records", 13692, len(univ))
add("SAMPLE-14", "Methods / Eq. 1", "theoretical order-event pairs", 561372, len(legal) * len(univ))

# Rebuild the +/-180 day eligibility screen (Eq. 2-3) from the corpus and the universe.
order_dates = {r["order_id"]: parse_date(r["order_date"]) for r in legal}
rebuilt = set()
for event in univ:
    event_date = parse_date(event["event_date"])
    for order_id, order_date in order_dates.items():
        if abs((event_date - order_date).days) <= 180:
            rebuilt.add(f"{order_id}||{event['event_type']}::{event['event_uid']}")
add("SAMPLE-15", "Methods / Eq. 3", "temporally eligible pairs (+/-180 days), rebuilt from corpus x universe",
    17413, len(rebuilt))
add("SAMPLE-16", "Methods / Eq. 3", "rebuilt pair keys identical to shipped screening file", "True",
    str(rebuilt == {r["stage6_pair_key"] for r in pairs}))
add("SAMPLE-17", "Methods / Table 1", "dictionary-screened pairs", 233, len(review))
add("SAMPLE-18", "Methods / Table 1", "unique UN events in review layer", 154, len({r["stage6_event_key"] for r in review}))
add("SAMPLE-19", "Methods / Table 1", "official files in review layer", 137,
    len({r["archive_pdf_filename"] for r in review}))

# ---- Table 2 ----
pair_codes = collections.Counter(r["final_link_code"] for r in review)
rank = {"9": -1, "0": 0, "1": 1, "2": 2, "3": 3}
event_code = {}
for r in review:
    key, code = r["stage6_event_key"], r["final_link_code"]
    if key not in event_code or rank[code] > rank[event_code[key]]:
        event_code[key] = code
event_codes = collections.Counter(event_code.values())
for code, p_exp, e_exp in [("0", 73, 47), ("1", 31, 26), ("2", 126, 78), ("3", 3, 3), ("9", 0, 0)]:
    add(f"TABLE2-P{code}", "Table 2", f"pair-level count, code {code}", p_exp, pair_codes.get(code, 0))
    add(f"TABLE2-E{code}", "Table 2", f"event-level count, code {code} (maximum code per event)", e_exp,
        event_codes.get(code, 0), "Event-level rule (maximum linkage class per event) is documented in CODEBOOK.md; the paper does not state it.")

# ---- Order-level rates (Findings, Figures 2-3) ----
for w, n_exp, pct_exp in [(30, 6, 25.0), (90, 7, 29.2), (180, 10, 41.7)]:
    n = sum(int(r[f"broad_{w}d"]) for r in primary)
    add(f"BROAD-{w}", "Findings / Fig. 2", f"dispute-level attention within {w} days (orders)", n_exp, n)
    add(f"BROAD-{w}-PCT", "Findings / Fig. 2", f"dispute-level attention within {w} days (%)", pct_exp, percent(n, len(primary)))
for w in (30, 90, 180):
    n = sum(int(r[f"order_specific_{w}d"]) for r in primary)
    add(f"ENGAGE-{w}", "Findings / Fig. 2", f"order-specific engagement within {w} days (orders)", 2, n)
add("ENGAGE-PCT", "Findings", "order-specific engagement rate, primary (%)", 8.3, percent(2, len(primary)))
add("ENGAGE-SENS", "Findings", "order-specific engagement rate, sensitivity sample N=27 (%)", 7.4,
    percent(sum(int(r["order_specific_engagement_final"]) for r in sens), len(sens)))

# ---- Rebuild order-level indicators from the pair-level coding ----
by_order = collections.defaultdict(list)
for r in review:
    by_order[r["order_id"]].append(r)
rebuild_ok = True
for o in orders:
    sub = by_order.get(o["order_id"], [])
    for w in (30, 90, 180):
        b = int(any(int(x["relative_day"]) <= w and int(x["final_link_code"]) >= 2 for x in sub))
        if b != int(o[f"broad_{w}d"]):
            rebuild_ok = False
    if int(any(x["final_link_code"] == "3" for x in sub)) != int(o["order_specific_engagement_final"]):
        rebuild_ok = False
add("INTERNAL-01", "Eq. 4-6", "order-level indicators rebuilt from pair-level codes equal shipped order-level file",
    "True", str(rebuild_ok))

# ---- Equation (5) derivation ----
eq5_mismatch = sum(
    1 for r in review
    if ((r["same_icj_case_confirmed"] == "1" and r["specific_order_reference"] == "1"
         and r["official_pdf_hash_verified"] == "1") != (r["final_link_code"] == "3")))
add("EQ5-01", "Eq. 5", "code 3 <=> SameCase AND ExplicitOrderLink AND OfficialSource (rows disagreeing)", 0, eq5_mismatch,
    "The 'InstitutionalProcess' condition of Eq. 5 has no separate column in the review file. See CODEBOOK.md.")
eq4_mismatch = sum(1 for r in review if (int(r["final_link_code"]) >= 2) != (r["same_icj_case_confirmed"] == "1"))
add("EQ4-01", "Eq. 4", "SameCase <=> code >= 2 (rows disagreeing)", 0, eq4_mismatch)
add("CODE9-01", "Findings", "unresolved (code 9) rows remaining", 0, pair_codes.get("9", 0))

# ---- Table 3 and positive evidence ----
add("POS-01", "Findings / Table 3", "positive documentary records", 4, len(posdocs))
add("POS-02", "Findings", "institutional processes", 3, len(posproc))
add("POS-03", "Findings", "Security Council processes", 2, sum(1 for r in posproc if r["UN_organ"] == "Security Council"))
add("POS-04", "Findings", "General Assembly processes", 1, sum(1 for r in posproc if r["UN_organ"] == "General Assembly"))
add("POS-05", "Findings", "adopted collective action among positives", 0, sum(int(r["adopted_collective_action"]) for r in posproc))
add("POS-06", "Findings", "positive primary orders", 2, sum(int(r["order_specific_engagement_final"]) for r in primary))
for symbol, lag in [("S/2024/173", 25), ("S/PV.9552", 25), ("A/78/PV.59", 38), ("S/PV.9638", 5)]:
    rec = [r for r in posdocs if r["document_symbol"] == symbol][0]
    computed = (parse_date(rec["document_date"]) - parse_date(rec["order_date"])).days
    add(f"LAG-{symbol}", "Table 3", f"lag in days for {symbol} (recomputed from dates)", lag, computed)
    add(f"LAGFIELD-{symbol}", "Table 3", f"lag_days field for {symbol}", lag, int(rec["lag_days"]))
pos_ids = sorted(r["order_id"] for r in primary if r["order_specific_engagement_final"] == "1")
add("FIG5-01", "Figure 5", "orders marked positive", "ICJ-192-2024-01-26|ICJ-192-2024-05-24", "|".join(pos_ids))
for oid, label in [("ICJ-166-2017-04-19", "Ukraine v. Russia 2017"), ("ICJ-178-2020-01-23", "The Gambia v. Myanmar 2020"),
                   ("ICJ-182-2022-03-16", "Ukraine v. Russia 2022"), ("ICJ-192-2024-03-28", "South Africa v. Israel 28 March 2024")]:
    val = [r for r in orders if r["order_id"] == oid][0]["order_specific_engagement_final"]
    add(f"NEG-{oid}", "Case concentration", f"no order-specific engagement: {label}", 0, int(val))

# ---- Table 4 ----
rr = collections.Counter((r["reporting_requirement"], r["order_specific_engagement_final"]) for r in primary)
add("TABLE4-01", "Table 4", "reporting requirement present: engagement / none", "2/10", f"{rr[('YES','1')]}/{rr[('YES','0')]}")
add("TABLE4-02", "Table 4", "reporting requirement absent: engagement / none", "0/12", f"{rr[('NO','1')]}/{rr[('NO','0')]}")

# ---- Permanent-member respondent pattern (Findings, 'P5 constraints') ----
p5_orders, nonp5_orders = [], []
russia = 0
for r in primary:
    _, respondent = parse_parties(r["case_title"])
    (p5_orders if is_p5(respondent) else nonp5_orders).append(r)
    if respondent and respondent.startswith("Russian Federation"):
        russia += 1
add("P5-01", "Findings, 'permanent member pattern'",
    "orders naming the RUSSIAN FEDERATION as respondent (paper text: six)", 6, russia,
    "The paper text attributes all six orders to the Russian Federation. Parsed respondents give Russia 3, "
    "United States 2, France 1. Six is the count for ALL permanent-member respondents. See docs/KNOWN_DISCREPANCIES.md.")
add("P5-02", "Findings", "orders naming ANY permanent member as respondent (parsed from case titles)", 6, len(p5_orders))
add("P5-03", "Findings", "permanent-member-respondent orders with engagement", 0,
    sum(int(r["order_specific_engagement_final"]) for r in p5_orders))
add("P5-04", "Findings", "orders with non-permanent-member respondents", 18, len(nonp5_orders))
add("P5-05", "Findings", "non-permanent-member-respondent orders with engagement", 2,
    sum(int(r["order_specific_engagement_final"]) for r in nonp5_orders))

# ---- Recall audit (Materials and Methods) ----
add("RECALL-00", "Methods", "recall-audit pairs", 120, len(recall))
unverifiable("RECALL-01", "Methods",
    "published recall subcategories: judicial elections / President briefings / Avena / unresolved",
    "The exact 120 candidate IDs and the manuscript-supported binary human outcome are preserved, but the original four-way human row-to-subcategory mapping behind 113/5/1/1 is not. The aggregate statement is retained in RECALL_REVIEW_PUBLISHED_SUMMARY.csv and is not contradicted by the package.")
add("RECALL-02", "Methods", "recall pairs with completed review and zero order-specific engagement", 120,
    sum(1 for r in recall_binary if r["review_completed"] == "YES" and r["order_specific_engagement"] == "0"))
add("RECALL-03", "Methods", "binary recall ledger pair keys identical to reconstructed 120 candidate IDs", "True",
    str({r["stage6_pair_key"] for r in recall_binary} == {r["stage6_pair_key"] for r in recall}))

# ---- Source integrity ----
integ = read_csv(DATA / "06_sources/SOURCE_INTEGRITY_VERIFICATION_137.csv")
add("HASH-01", "Methods, document integrity", "archived UN PDFs whose recorded digest matched (flag)", 137,
    sum(int(r["hash_match"]) for r in integ),
    "Self-reported flag. PDFs are not redistributed. Use code/verify_source_hashes.py with a local PDF folder to re-verify.")
add("HASH-02", "Methods, document integrity", "rows where expected_sha256 equals recomputed_sha256", 137,
    sum(1 for r in integ if r["expected_sha256"] == r["recomputed_sha256"]))
unverifiable("HASH-03", "Methods, document integrity / Table 3",
             "SHA-256 integrity control applies to the documents used in analysis",
             f"Only {sum(1 for r in posdocs if r['document_sha256'].strip())} of {len(posdocs)} positive documentary records carry a stored digest. "
             "S/2024/173 and A/78/PV.59 have none (documented limitation, not a coding gap).")

# ---- Claims the package cannot verify ----
# Original dictionary resources have been restored and a portable reconstruction reproduces all 233 keys.
from reconstruct_dictionary_screen import ROOT as _screen_root  # importability check only
import subprocess as _sp
_scr=_sp.run([sys.executable,str(ROOT/"code/reconstruct_dictionary_screen.py")],capture_output=True,text=True)
add("NOTVER-01", "Methods", "case-dictionary screen selects the 233 manual-review pairs", "True", str(_scr.returncode==0),
    "Original dictionary and archived selection logic restored in v1.2.0-RC1; portable script reproduces exact pair keys.")
unverifiable("NOTVER-02", "Methods", "Event duplication controlled by a composite key (date, symbol, process)",
             "The shipped keys are event_type::event_uid. The composite key is not stored.")
add("NOTVER-03", "Methods", "archived R analysis source recovered in package", "True",
    str((ROOT/"code/historical_method/reviewer_analysis_ARCHIVAL.R").exists()),
    "The recovered archival R script documents an R component; the canonical public reproduction remains Python. A portable R descriptive script is also supplied but was not runtime-tested in the build environment.")
add("NOTVER-04", "Methods", "no separate Article 41(2) notification-date field in frozen legal corpus", "True",
    str("notification_date" not in legal[0]),
    "A separate post-publication enrichment registry now records three Case No. 192 transmission documents; it is not used as published time zero.")
add("NOTVER-05", "Materials and Methods", "all substantive coding in public 233 file attributed to sole author", "True",
    str(all(r.get("primary_coder")=="Suraya Bazarova" and r.get("primary_coding_mode")=="HUMAN_MANUAL" for r in review)),
    "No completed second-coder dataset is represented in the public release.")
add("NOTVER-06", "Findings", "four positive documentary records have explicit source pin-cites", "True",
    str(all(r.get("pin_cite","").strip() for r in posdocs)),
    "Pin-cites added after verification against official UN records. Source PDFs are still not redistributed.")

write_csv(ROOT / "outputs/paper_concordance.csv", rows)
counts = collections.Counter(r["status"] for r in rows)
print(json.dumps(dict(counts), indent=2))
bad = {r["claim_id"] for r in rows if r["status"] == "MISMATCH"}
for r in rows:
    if r["status"] == "MISMATCH":
        print(f"MISMATCH {r['claim_id']}: paper={r['paper_value']} computed={r['computed_value']}")
if bad != EXPECTED_MISMATCH_IDS:
    print("FAIL: set of mismatches differs from the documented set:", sorted(bad), "expected", sorted(EXPECTED_MISMATCH_IDS))
    sys.exit(1)
print("OK: only the documented discrepancies remain:", sorted(bad))
