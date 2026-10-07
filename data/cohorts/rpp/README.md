# Reproducibility Project: Psychology

Open Science Collaboration

Direct replication of published psychology findings

The inventory preserves 98 paper records and 100 assessment rows concerning 98 papers.

## Files

- `papers.csv`: one row per source paper ID, including unassessed roster entries.
- `assessments.csv`: source-level outcomes; multiple rows may belong to one paper.
- `source_records/`: selected original columns or an exact source-table extraction.
- `sources.csv`: exact download URLs, original-file checksums and local source paths.
- `study.json`: study-specific definitions, timing evidence and remaining work.

Original downloads are preserved in `private-data/cohorts/rpp/source/`.
The [shared dictionary](../dictionary.md) defines the normalized columns.

## Construction and outcomes

Keep Completion.R == 1 in the primary 168-row file, yielding all 100 completed study records. These belong to 98 distinct original papers: two pairs share title, authors, journal, volume, issue and pages. paper_crosswalk.csv maps every study record to the original paper; both assessments survive. Do not require an observed p value: one completed study lacks it. The initial inventory preserves discovery DOI links. All 98 analysis identities are verified in pipeline/identities.csv; pipeline/identity_decisions.json documents source corrections, including one wrong journal/page locator.

Replicate.R is the source judgment: 39 yes, 59 no and 2 No, retained verbatim. T.pval.USE.R, T.sign.R.125, T.r.O and T.r.R remain in the source projection. These are source replication judgments, not original-error labels.

## Disclosure timing

The COS announcement dates to 27 August 2015. Check earlier individual reports before treating this as every paper's first disclosure.

## Sources and next step

[Study](https://doi.org/10.1126/science.aac4716); [archive](https://github.com/CenterForOpenScience/rpp).

See pipeline/README.md for the citation analysis and scripts/rpp/README.md for the numbered workflow. Earlier individual report candidates require content and historical-visibility review before assigning first-disclosure dates; the current estimate concerns the 2015 project announcement.

## Rebuild

From the repository root, run `make cohorts-import` using saved originals, or
`make cohorts-fetch` to download the recorded source URLs and verify their hashes.
Run `make cohorts` for offline consistency checks and regeneration of this index.
