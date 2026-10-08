# Validation and limitations note

Inherited from version 1.0.0 and still accurate. For the 1.1.0 checks see `RELEASE_VALIDATION_REPORT.md`. Items 1 to 6 of `docs/KNOWN_DISCREPANCIES.md` are additional to the notes below.

## Confirmed release checks

- 41 unique ICJ decision IDs
- 27 unique contentious cases
- disposition distribution 20 NEW_PM, 4 MODIFIED_PM, 3 REAFFIRMED_PM, 12 REQUEST_REJECTED, 2 WITHDRAWN_OR_DISCONTINUED
- 13,692 unique UN event IDs
- event-type composition 6,415 SC meetings, 5,694 GA formal votes, 1,578 SC formal votes, 5 SC special-veto records
- 561,372 theoretical combinations
- 17,413 ±180-day eligible pairs
- 233 unique manually reviewed pair IDs
- 154 event rows and 137 archived UN PDFs in the original manual-review layer
- 137/137 archived UN PDF SHA-256 checks matched
- 120 exact E1–E4 strong-candidate pair IDs outside the original 233 layer
- four final positive documentary records
- three final institutional processes
- two positive primary orders
- broad order-level counts 6 / 7 / 10 at 30 / 90 / 180 days
- reporting-requirement cross-tab 2+10 vs 0+12

## Deliberately not reconstructed

The release now also includes `RECALL_REVIEW_120_HUMAN_BINARY_RECONSTRUCTED.csv`, a 120-row binary human-review ledger supported by the manuscript statement that all 120 were reviewed in full by the sole author and none yielded an additional order-specific positive. The published 113 / 5 / 1 / 1 **subcategory** breakdown still cannot be mapped to individual pair IDs without inference. The aggregate summary and binary ledger are therefore kept separate.

## Not a full-text UN corpus

The 13,692-event universe is heterogeneous and incomplete for General Assembly plenary discourse. A/78/PV.59 was absent upstream. This dataset is suitable for reproducing the published study as scoped, but it must not be presented as a comprehensive UN full-text corpus for a new NLP article.

## Positive-document source verification

The official UN URLs for S/2024/173 and A/78/PV.59 were independently re-verified on 8 October 2026. Their raw PDF bytes were not preserved inside the uploaded master archive, so this release does not invent SHA-256 values for them. S/PV.9552 and S/PV.9638 retain verified master-archive hashes. This is an explicit provenance limitation, not a missing substantive classification.
