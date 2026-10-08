# Critical audit response

This release was rebuilt after a post-publication methodological audit. The purpose is not to conceal or retroactively rewrite the conference paper. It is to separate reproducible published results, genuine published wording errors, recoverable screening machinery, and limitations that cannot be repaired without new human review.

| Audit issue | Status in v1.2.0 | Resolution |
|---|---|---|
| Unreviewed pairs could look like coded zero | **Resolved in public data semantics** | Pair-level coverage explicitly distinguishes preserved review evidence from `NO_PRESERVED_MANUAL_REVIEW_EVIDENCE`; order-level zeros are labelled non-exhaustive. |
| Original 233 dictionary screen unavailable | **Resolved** | Historical dictionary resources and screening logic were recovered. `reconstruct_dictionary_screen.py` reproduces the exact 233 pair keys from 8,557 nonnegative-lag pairs. |
| 120 recall audit row categories not reproducible | **Not fully recoverable** | Exact 120 candidate IDs are reconstructable, but the original human 113/5/1/1 row mapping was not preserved. The package does not fabricate it. |
| Engagement could be confused with adopted collective action | **Resolved** | Misleading `collective_organ_output` field removed. Positive records are classified separately as deliberative, proposed/vetoed, or adopted action. No adopted collective action is claimed. |
| Article 41(2) notification/exposure not observed for all orders | **Clarified** | Published timing uses order date, not notification date. A partial transmission registry is post-publication enrichment only; unknown does not mean no transmission. |
| 24 orders are clustered in 17 cases | **Resolved diagnostically** | Case-level rate, Wilson intervals and duplicate-case concentration are reported in post-publication diagnostics. No causal inference is made. |
| Reporting-requirement pattern may be Case 192-driven | **Resolved diagnostically** | Fisher exact p and Case-192-excluded cross-tab are reported; the relationship remains descriptive only. |
| Symmetric ±180 screen includes pre-order observations | **Clarified** | Pre/same/post decomposition is reported; the symmetric layer is eligibility architecture only, not a follow-up numerator. |
| P5 statement says six Russian Federation orders | **Genuine published wording error** | Correct count is Russia 3, United States 2, France 1 = six permanent-member-respondent orders. Erratum note included. Headline results unchanged. |
| Pin-cites absent for nonpositive rows | **Not retroactively fabricated** | Positive rows have verified pin-cites. Machine context is separated from human evidence. A full negative-row pin-cite ledger would require a new human re-audit. |
| Second coder provenance | **Resolved** | No pending second coder is named in canonical row-level data. Published substantive coding is attributed only to Suraya Bazarova. |
