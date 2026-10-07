# Multi100 analytical robustness

Multi100 collaboration

Independent reanalysis of claims from 100 social-science papers

The inventory preserves 100 paper records and 509 assessment rows concerning 100 papers.

## Files

- `papers.csv`: one row per source paper ID, including unassessed roster entries.
- `assessments.csv`: source-level outcomes; multiple rows may belong to one paper.
- `source_records/`: selected original columns or an exact source-table extraction.
- `sources.csv`: exact download URLs, original-file checksums and local source paths.
- `study.json`: study-specific definitions, timing evidence and remaining work.

Original downloads are preserved in `private-data/cohorts/multi100/source/`.
The [shared dictionary](../dictionary.md) defines the normalized columns.

## Construction and outcomes

Preserve all 100 paper records and 509 analyst-result rows. Original DOI linkage uses the source SCORE suffix identifier only when normalized original titles also match; unmatched titles are left unresolved. Source analyst IDs are retained without personal-name/contact columns in the projection.

task1_categorisation is retained as an analyst judgment in the source's words. original_reproduction_outcome, direction_of_result, p_value_report, reanalysis_cohens_d and peer_eval_pass remain separate. P values include inequalities and text, so the inventory does not silently coerce them to numbers. One row fails the peer-evaluation flag and four fail the incomplete-response flag; all remain explicit. No paper-level success rule is imposed.

## Disclosure timing

The summary article appeared on 1 April 2026. Recover earlier paper-level or project releases before defining the disclosure event.

## Sources and next step

[Study](https://doi.org/10.1038/s41586-025-09844-9); [archive](https://github.com/marton-balazs-kovacs/multi100).

Verify the analysis-stage definitions and original identity links, retain peer-review flags, and choose a paper-level outcome rule that accounts for multiple analysts. Check overlap with SCORE.

## Rebuild

From the repository root, run `make cohorts-import` using saved originals, or
`make cohorts-fetch` to download the recorded source URLs and verify their hashes.
Run `make cohorts` for offline consistency checks and regeneration of this index.
