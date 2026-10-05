# Independent coding protocol

Do not infer error propagation from a citation's presence or from the absence of a criticism in one sentence. Read the original claim record and the citing paper. Preserve uncertainty.

## Establish the original claim first

Use `data/pilot/claims.csv`. Two independent readers must record their identities and assess the exact passage, figure/table, source criticism, relevant author response or correction, and any alternative evidence within the original paper. Resolve disagreements before estimating continued reliance. Allowed final statuses are `verified_inferential_error`, `assumption_sensitive`, `not_sustained`, and `unresolved`. A significance change alone cannot establish a false substantive claim. The supplied assessments and the assistant's first-pass checks are evidence for this review, not completed independent judgments.

## One record per reader and citation pair

Use `reader_1` and `reader_2` as placeholders until actual identities are assigned. Do not consult the other reader's judgments before recording your own. Empty cells mean uncompleted work, not no.

| Field | Values and rule |
| --- | --- |
| `pair_id` | Fixed identifier from the sample. Never renumber. |
| `reader_id` | Actual reader identifier; same identifier throughout the study. |
| `valid_link` | `yes`, `no`, or `unclear`. Check reference identity, including corrections and different versions. |
| `fulltext_read` | `yes` only after reading all relevant sections, mentions, and qualifications; `no` for an unavailable full text; `unclear` for incomplete material. |
| `claim_identified` | `yes`, `no`, or `unclear`: can the specific challenged inference be identified in the original and compared to the citing passage? |
| `relies_on_claim` | `yes`, `no`, or `unclear`. Yes means the citing paper uses the challenged finding as evidence, not merely describes the controversy or cites a different contribution. |
| `qualification` | `yes`, `no`, or `unclear`: does the paper acknowledge or accommodate a limitation relevant to that claim? An unrelated generic caveat is insufficient. No requires full-text review. |
| `use_role` | Semicolon-separated entries from `hypothesis`, `design`, `effect_size`, `meta_analysis`, `substantive_evidence`, `unaffected_finding`, `method_background`, `critical_discussion`, `unclear`. |
| `evidence_locator` | Page, section, paragraph, table, and/or stable anchor for every passage necessary to justify the code. |
| `evidence_excerpt` | Short passage establishing use/qualification; store longer annotated material privately when needed. |
| `notes` | Ambiguity, author response, correction, version mismatch, pre-warning submission, possible duplicate, or additional supporting evidence. |

“Unqualified reliance” requires a verified link, full-text review, an identified challenged claim, `relies_on_claim=yes`, and `qualification=no`. A critical discussion can mention the claim accurately while having `relies_on_claim=no` and `use_role=critical_discussion`. A broad method/background citation is not reliance merely because its source contains a mistake. A claim can be used with a qualification; these are two separate dimensions.

For papers citing an original and its critique, record what the text actually does. Co-citation establishes an opportunity for acknowledgment; it does not establish what an author knew. Papers with publication dates after a warning may have been submitted before it. Record submission/version information when available, and retain the one-year publication lag for the main pilot.

## Disagreements and completeness

Compare the two original ratings only after both are locked. Calculate exact agreement and confusion tables separately for reliance and qualification, reporting complete-pair denominators and unresolved responses. Report positive and negative agreement alongside overall agreement when possible. Do not use adjudicated ratings to claim initial reliability. Record adjudication in a separate file keyed by `pair_id`, including adjudicator, final codes, and reason.

Unavailable texts and unmapped claims remain unresolved. Do not replace them with more convenient papers. If retrieval differs sharply between cohorts or periods, resolve access before interpreting any observed difference in reliance. Expansion requires the availability and agreement criteria in the protocol; the sign of the eventual finding is not a criterion.
