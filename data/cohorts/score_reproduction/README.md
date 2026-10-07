# SCORE: computational reproducibility

SCORE collaboration

Reproduction of published results using original data and code

The inventory preserves 600 paper records and 551 assessment rows concerning 143 papers.

## Files

- `papers.csv`: one row per source paper ID, including unassessed roster entries.
- `assessments.csv`: source-level outcomes; multiple rows may belong to one paper.
- `source_records/`: selected original columns or an exact source-table extraction.
- `sources.csv`: exact download URLs, original-file checksums and local source paths.
- `study.json`: study-specific definitions, timing evidence and remaining work.

Original downloads are preserved in `private-data/cohorts/score_reproduction/source/`.
The [shared dictionary](../dictionary.md) defines the normalized columns.

## Construction and outcomes

Preserve all 600 non-COVID sampled papers from pr_outcomes. For assessed outcomes keep !is_covid, repro_version_of_record and repro_outcome_overall != none: 551 claims from 143 papers. Unassessed papers remain in the roster with zero assessment rows; they are not failures.

Native categories are push button (253), precise (91), approximate (102), not (100), and not attemptable (5). The last category remains distinct. An inability to reproduce due to unavailable inputs does not establish a substantive error. All source DOI identities are retained.

## Disclosure timing

The summary article appeared on 1 April 2026; individual reports may have earlier public dates. No citation-effect estimate is eligible at the 2025 cutoff solely on that summary date.

## Sources and next step

[Study](https://doi.org/10.1038/s41586-026-10203-5); [archive](https://osf.io/kmvst/).

Recover individual disclosure dates, distinguish discrepancies from unavailable materials, and specify how multiple claim outcomes become one paper assessment. Check overlap with other SCORE components.

## Rebuild

From the repository root, run `make cohorts-import` using saved originals, or
`make cohorts-fetch` to download the recorded source URLs and verify their hashes.
Run `make cohorts` for offline consistency checks and regeneration of this index.
