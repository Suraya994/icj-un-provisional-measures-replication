# Codebook and data dictionary

## Units

- **ICJ decision/order:** one Court decision on a provisional-measures request (`order_id`).
- **UN event:** one record in the predefined heterogeneous UN event universe.
- **Order-event pair:** one ICJ order matched to one UN event within ±180 calendar days.
- **Reviewed pair:** one candidate advanced to human full-text review.
- **Documentary record:** an official UN document used as direct positive evidence.
- **Institutional process:** a substantively distinct Security Council or General Assembly process; several documents can belong to one process.
- **Case file:** one contentious ICJ case (`case_number`).

## Samples and time

Primary sample = `NEW_PM` + `MODIFIED_PM` = 24 orders. Sensitivity sample adds `REAFFIRMED_PM` = 27. Time zero in the published quantitative windows is the **order date**, not a separately measured Article 41(2) transmission date. Windows 30/90/180 are nested. The ±180 eligibility screen is symmetric and therefore contains pre-order pairs; follow-up outcomes use nonnegative/post-order time only.

## Original dictionary screen

`data/03_screening/dictionary/ICJ_CASE_FILE_DICTIONARY_V1.csv` and `ICJ_CASE_PARTY_ISSUE_LEXICON_V4.csv` are restored historical screening resources. `code/reconstruct_dictionary_screen.py` applies the archived logic portably to the 17,413 file and reproduces exactly 8,557 nonnegative-lag pairs, preliminary codes 0=8,246, 1=25, 2=53, 9=233, and the exact 233 pair keys in the manual-review layer. Preliminary code 9 means **requires full-document review**, not substantive positive engagement.

## Final manual linkage codes

`MANUAL_REVIEW_233_HUMAN.csv` contains the published human-coded review layer. `final_link_code`: 0 unrelated/different case; 1 general thematic overlap; 2 same dispute without all order-specific conditions; 3 order-specific institutional engagement; 9 unresolved (none remain). The published construct requires same case, explicit connection to the matched order, identifiable SC/GA institutional process, and official source. Code 3 is not synonymous with implementation, compliance, or adopted collective action.

The old field `collective_organ_output` was removed from the public canonical CSV because its name could be misread as adopted output. Institutional form is instead documented in `POSITIVE_DOCUMENTARY_RECORDS_4.csv` and `POSITIVE_INSTITUTIONAL_PROCESSES_3.csv`.

`page_or_paragraph` is now populated for the three code-3 pair rows: S/PV.9552 pp. 2, 8 and S/PV.9638 p. 2. Nonpositive rows do not have retrospectively invented page cites. A separate `MANUAL_REVIEW_233_MACHINE_CONTEXT_AUDIT.csv` preserves machine-extracted context from the research archive, explicitly labelled as non-human evidence.

## Recall audit

`RECALL_AUDIT_120_CANDIDATE_IDS_RECONSTRUCTED.csv` preserves the reconstructable candidate IDs. `RECALL_REVIEW_120_HUMAN_BINARY_RECONSTRUCTED.csv` adds the preserved binary human-review result supported by the manuscript: Suraya Bazarova reviewed all 120 in full and none met the order-specific-engagement definition. This is not represented as the contemporaneous original row-level worksheet. The original four-way human row-to-subcategory mapping behind 113/5/1/1 remains unavailable, and no such labels are retroactively invented.

## Coverage diagnostics

`ORDER_REVIEW_COVERAGE_24.csv` and `PRIMARY_POSTORDER_4868_REVIEW_COVERAGE.csv` distinguish candidate records with preserved review evidence from eligible records with no preserved manual-review evidence. These are post-publication audit diagnostics and do not alter published outcomes.

## Source integrity

137 archived UN PDFs have preserved expected/recomputed SHA-256 equality in `SOURCE_INTEGRITY_VERIFICATION_137.csv`. Source PDFs are not redistributed in this compact repository. S/2024/173 and A/78/PV.59 were added/verified after the original archive and do not have a preserved local hash in the master package; this is disclosed rather than fabricated.

## Zero semantics and unreviewed records

`ORDER_LEVEL_RESULTS_41_CANONICAL.csv` preserves the published 0/1 indicators for exact replication. For interpretation, use `data/07_postpublication_diagnostics/ORDER_LEVEL_INTERPRETATION_24.csv`. A zero is **not** a claim that all temporally eligible records were manually reviewed. `PRIMARY_POSTORDER_4868_REVIEW_COVERAGE.csv` supplies `review_evidence_status` so unreviewed pairs are not silently converted into coded negatives.

## Structured metadata is not full text

`event_text_metadata` and related universe fields are screening metadata, not a 13,692-document full-text corpus. They must not be used as if they were full documentary text in a new NLP analysis.
