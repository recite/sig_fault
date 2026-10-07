# SCORE: replicability of social and behavioural science

SCORE collaboration

Replication outcomes under the project's stated success criterion

The inventory preserves 164 paper records and 274 assessment rows concerning 164 papers.

## Files

- `papers.csv`: one row per source paper ID, including unassessed roster entries.
- `assessments.csv`: source-level outcomes; multiple rows may belong to one paper.
- `source_records/`: selected original columns or an exact source-table extraction.
- `sources.csv`: exact download URLs, original-file checksums and local source paths.
- `study.json`: study-specific definitions, timing evidence and remaining work.

Original downloads are preserved in `private-data/cohorts/score_replication/source/`.
The [shared dictionary](../dictionary.md) defines the normalized columns.

## Construction and outcomes

Load the primary analysis RData. Join repli_binary to repli_outcomes on report_id, then paper_metadata on paper_id: 274 claims from 164 original papers, all with DOIs. Keep the published subset, not all 427 candidate outcome records. Project metadata also contain earlier individual project dates, which are not automatically public disclosure dates.

The primary native variable is repli_score_criteria_met: 151 met and 123 not met. repli_binary_analyst is a different definition and is retained separately; it cannot substitute for the primary criterion. Several claims can belong to one paper. Neither outcome proves an error in the original paper.

## Disclosure timing

The summary article appeared on 1 April 2026, after the current citation cutoff of 31 December 2025. Earlier public replication reports may support earlier events; these require date verification.

## Sources and next step

[Study](https://doi.org/10.1038/s41586-025-10078-y); [archive](https://osf.io/bzfgy/).

Recover first public report dates and aggregate claim outcomes to a justified paper-level assessment. Resolve overlap with computational reproduction, Multi100 and the existing FReD/FLoRA inventories before matching.

## Rebuild

From the repository root, run `make cohorts-import` using saved originals, or
`make cohorts-fetch` to download the recorded source URLs and verify their hashes.
Run `make cohorts` for offline consistency checks and regeneration of this index.
