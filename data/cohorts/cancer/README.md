# Reproducibility Project: Cancer Biology

Reproducibility Project: Cancer Biology collaboration

Experimental replication of cancer-biology findings

The inventory preserves 53 paper records and 188 assessment rows concerning 23 papers.

## Files

- `papers.csv`: one row per source paper ID, including unassessed roster entries.
- `assessments.csv`: source-level outcomes; multiple rows may belong to one paper.
- `source_records/`: selected original columns or an exact source-table extraction.
- `sources.csv`: exact download URLs, original-file checksums and local source paths.
- `study.json`: study-specific definitions, timing evidence and remaining work.

Original downloads are preserved in `private-data/cohorts/cancer/source/`.
The [shared dictionary](../dictionary.md) defines the normalized columns.

## Construction and outcomes

Preserve the complete 53-paper source roster and 188 result rows from 23 papers. Rows include internal replications; paper, experiment, effect and internal-replication identifiers form the assessment key. Preserve uncompleted projects in the roster. Original titles and replication-report links are present; original DOI linkage remains.

Expected and observed differences, effect sizes, standard errors and p values remain in the source projection. Native observed-difference labels distinguish direction and statistical evidence. Internal repeats are not independent papers. No automatic binary label converts an unsuccessful replication into an original statistical error.

## Disclosure timing

Individual replication reports began before the 7 December 2021 aggregate article, including reports from 2017. Use the first public report for each original; submission and acceptance dates in the roster are not publication dates.

## Sources and next step

[Study](https://pmc.ncbi.nlm.nih.gov/articles/PMC8651293/); [archive](https://osf.io/e5nvr/).

Resolve original DOIs and report publication dates; account for multiple effects and internal replications before defining the paper-level comparison. Check earlier corrections or retractions separately.

## Rebuild

From the repository root, run `make cohorts-import` using saved originals, or
`make cohorts-fetch` to download the recorded source URLs and verify their hashes.
Run `make cohorts` for offline consistency checks and regeneration of this index.
