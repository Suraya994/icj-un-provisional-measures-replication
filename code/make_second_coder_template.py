#!/usr/bin/env python3
"""Write a BLIND coding sheet for a second coder. First-coder codes and evidence fields are not included."""
from replication_utils import ROOT, DATA, read_csv, write_csv

review = read_csv(DATA / "04_human_coding/MANUAL_REVIEW_233_HUMAN.csv")
rows = []
for r in sorted(review, key=lambda x: x["stage6_pair_key"]):
    rows.append({
        "stage6_pair_key": r["stage6_pair_key"], "order_id": r["order_id"], "order_date": r["order_date"],
        "event_date": r["event_date"], "document_symbol": r["document_symbol"], "event_type": r["event_type"],
        "event_text_metadata": r["event_text_metadata"], "official_source_url": r["fulltext_source"],
        "coder_id": "", "coding_date": "",
        "same_case_0_1": "", "explicit_order_link_0_1": "", "institutional_process_0_1": "", "official_source_0_1": "",
        "link_code": "", "page_or_paragraph": "", "coder_note": "",
    })
write_csv(ROOT / "docs/templates/SECOND_CODER_BLIND_TEMPLATE_233.csv", rows)
print(len(rows), "rows written")
