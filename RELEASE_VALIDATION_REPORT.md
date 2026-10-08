# Release validation report, version 1.3.0 (8 October 2026)

Scope: package integrity, numerical reproduction, screening reconstruction and paper-versus-data concordance. This report **does not independently validate the author's substantive legal coding**.

## Executed checks

- `code/reconstruct_dictionary_screen.py`: PASS. Exact 233 pair-key reconstruction.
- `code/reproduce_published_results.py`: PASS.
- `code/reproduce_additional_results.py`: PASS.
- `code/check_paper_concordance.py`: 82 claims checked: **78 MATCH, 2 MISMATCH, 2 UNVERIFIABLE**.
- `code/validate_release.py`: PASS.
- `python3 -m unittest discover -s tests -v`: 4 tests PASS.
- Source-integrity table: 137/137 stored expected SHA-256 values equal stored recomputed SHA-256 values.

## Reproduced published architecture

41 decisions / 27 cases; 13,692 structured UN events; 561,372 theoretical combinations; 17,413 ±180-day pairs; exact 233 candidate keys; final 233 code distribution 73/31/126/3; 24 primary and 27 sensitivity orders; broad attention 6/7/10; order-specific indicator 2/2/2; four documentary records; three processes; two positive orders.

## Documented published discrepancies

1. P5 country-label wording: the paper says six Russian Federation respondent orders. Data support Russia 3, United States 2 and France 1, i.e. six **permanent-member-respondent** orders. The 0/6 versus 2/18 descriptive split is unchanged.
2. Recall subcategory breakdown 113/5/1/1: the exact 120 candidate IDs and a 120-row binary human-review ledger are preserved/reconstructed, confirming all 120 reviewed and zero additional positives. The original four-way per-row subcategory mapping is not preserved, so the aggregate 113/5/1/1 statement remains archivally unverifiable rather than contradicted.

## Archivally unverifiable from the compact package

- Stored hashes are unavailable for post-hoc positive records S/2024/173 and A/78/PV.59. Official source URLs and pin-cites are verified; no digest is fabricated.
- The paper's historical duplicate-control statement based on a date/symbol/process composite key cannot be reconstructed exactly from preserved public keys.

## Interpretation boundary

The package now distinguishes **unreviewed** pairs from human-reviewed candidate pairs. A published order-level zero must be read as *no positive identified among screened/reviewed candidate evidence*, not as an exhaustive negative finding across every eligible UN record.

## v1.3.0 final public-release checks

- Paper concordance checks: 83 total; 79 MATCH; 1 MISMATCH; 3 UNVERIFIABLE.
- Sole paper-data mismatch: P5/Russian Federation wording, documented in `docs/POSTPUBLICATION_ERRATA_NOTE.md`.
- 120-row binary human recall ledger: present, exact candidate-key concordance, 120/120 reviewed, 0/120 order-specific positives.
- Repository licensing: applied.
- Public-release blockers: none in `QUALITY_GATE.json`.
