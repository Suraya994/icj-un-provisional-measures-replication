# Replication package: UN practice concerning ICJ provisional measures (2002–2025)

Data, code, screening resources and audit documentation accompanying:

> Bazarova, S. (2026). *Temporal Proximity Does Not Establish Institutional Follow Up: UN Practice Concerning ICJ Provisional Measures (2002–2025).* In *International Conference on Globalization & International Relations-VIII, Proceedings Book*, pp. 87–107. Liberty Publishing House. ISBN 979-8-89695-539-9. Published 13 September 2026.

Author: **Suraya Bazarova**. ORCID 0000-0002-9061-6364.

## Status

**Version 1.3.0 — public-release package.** The quantitative replication chain passes the included validators. One published wording error (the P5/Russian Federation sentence) remains documented as a post-publication erratum rather than silently rewritten.

This package was rebuilt after a critical post-publication audit. It does **not** silently repair the published paper. It separates four things: (1) results that reproduce, (2) source-selection machinery that can be reconstructed, (3) post-publication diagnostics, and (4) published statements that require an erratum or remain archivally unverifiable.

### What now reproduces exactly

- 41 ICJ decisions in 27 contentious cases.
- 13,692 structured UN events; 561,372 theoretical combinations.
- 17,413 ±180-day pairs, rebuilt from dates.
- **Original case-dictionary screen restored:** 8,557 nonnegative-lag pairs -> preliminary 0/1/2/9 counts of 8,246/25/53/233 -> the exact same 233 pair keys as the manual-review layer. Run `python3 code/reconstruct_dictionary_screen.py`.
- 233 human-coded pairs with final codes 73/31/126/3. All substantive coding is attributed only to Suraya Bazarova (`HUMAN_MANUAL`).
- 24 primary and 27 sensitivity orders; broad 30/90/180 = 6/7/10; order-specific = 2/2/2.
- Four positive documentary records -> three institutional processes -> two positive orders, all within Case No. 192.

### Critical interpretation boundary

The 233 rows are **not** an exhaustive reading of all 17,413 temporally eligible pairs. Among 24 primary orders there are 4,868 post-order pairs (0–180 days); 209 are in the original 233 review layer. The reconstructed 120-candidate recall set adds review evidence for 33 additional primary post-order pairs, for a union of 242/4,868. See `data/07_postpublication_diagnostics/ORDER_REVIEW_COVERAGE_24.csv`. Therefore an order-level zero means **no order-specific engagement was found among screened/reviewed candidate evidence**, not that every eligible UN record was read. Pair-level records with no preserved manual-review evidence are now explicitly labelled `NO_PRESERVED_MANUAL_REVIEW_EVIDENCE`.

### Human-coding provenance

The published analysis had one substantive coder: **Suraya Bazarova**. Automated procedures performed candidate generation, date-window construction, text diagnostics, hashing, aggregation and figure generation. No person is named in this public package as a pending second coder. No independent second-coder dataset is represented as completed.

### Recall audit

The exact 120 E1–E4 candidate IDs are reconstructed from the later V8 evidence screen and are preserved in `RECALL_AUDIT_120_CANDIDATE_IDS_RECONSTRUCTED.csv`. The system also preserves a 120-row binary human-review ledger, now released as `RECALL_REVIEW_120_HUMAN_BINARY_RECONSTRUCTED.csv`: the published manuscript states that Suraya Bazarova read all 120 in full and that none met the order-specific-engagement definition. The original four-way row-to-subcategory mapping underlying the published 113/5/1/1 descriptive breakdown is still not preserved, so those four labels are **not** retroactively assigned to individual rows. The aggregate statement remains in `RECALL_REVIEW_PUBLISHED_SUMMARY.csv`.

### Published wording issue

The paper twice says that six primary orders name the **Russian Federation** as respondent. The data support six orders involving **any Security Council permanent-member respondent**: Russian Federation 3, United States 2, France 1. The 0/6 versus 2/18 descriptive split remains numerically unchanged, but the noun phrase in the paper requires correction. See `docs/POSTPUBLICATION_ERRATA_NOTE.md`.

### S/PV.9638

The earlier concern that the paper over-described S/PV.9638 is resolved. The official record, p. 2, explicitly reports the ICJ order of 24 May 2024 to the Security Council and the meeting contains additional order-specific interventions. The classification as **deliberative engagement**, not adopted collective action, is supported.


### Post-publication diagnostics

The package now includes case-level uncertainty, review-coverage diagnostics, the pre/same/post composition of the symmetric screen, a reporting-requirement sensitivity diagnostic, a partial Article 41(2) transmission registry, and a machine-screen pre/post proxy. These files are **diagnostics**, not retroactive additions to the published estimand. See `data/07_postpublication_diagnostics/` and `docs/CRITICAL_AUDIT_RESPONSE.md`.

## Quick start

```bash
python3 -m pip install -r requirements.txt
python3 code/reconstruct_dictionary_screen.py
python3 code/reproduce_published_results.py
python3 code/reproduce_additional_results.py
python3 code/check_paper_concordance.py
python3 code/validate_release.py
python3 -m unittest discover -s tests -v
```

Optional R source: `code/reproduce_descriptives.R`. The historical R script recovered from the master archive is in `code/historical_method/`; it is provenance material and uses the older research-archive layout.

## Repository layout

`data/01_legal_corpus` legal coding; `02_universe` structured event universe; `03_screening` temporal pairs plus restored dictionary; `04_human_coding` manual coding and recall audit; `05_results` published-result layers; `06_sources` registries/hashes; `07_postpublication_diagnostics` coverage, case-level uncertainty and Article 41(2) transmission enrichment; `code/` portable reproduction; `docs/` discrepancies, errata and quality gates.

## Licensing

This public release is multi-licensed. Code is MIT licensed. Original author-created coding/data, derived outputs and documentation are CC BY-NC 4.0. Third-party UN/ICJ materials are not relicensed. See `LICENSE`, `LICENSE-CODE`, `LICENSE-DATA-DOCS`, and `LICENSE_NOTICE.md`.
