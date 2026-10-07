# Causal panel analysis under parallel trends

Albert Chiu, Xingchen Lan, Ziyi Liu and Yiqing Xu

Reanalysis of panel studies and parallel-trends diagnostics

The inventory preserves 49 paper records and 245 assessment rows concerning 49 papers.

## Files

- `papers.csv`: one row per source paper ID, including unassessed roster entries.
- `assessments.csv`: source-level outcomes; multiple rows may belong to one paper.
- `source_records/`: selected original columns or an exact source-table extraction.
- `sources.csv`: exact download URLs, original-file checksums and local source paths.
- `study.json`: study-specific definitions, timing evidence and remaining work.

Original downloads are preserved in `private-data/cohorts/panel/source/`.
The [shared dictionary](../dictionary.md) defines the normalized columns.

## Construction and outcomes

Retain all 49 rows of Supplement A Table A1, PDF page 34, plus the 349-page Supplement B with paper-specific results. The larger search screened 102 papers and identified 64 TWFE studies; the 49 reanalyses are not the full screened population. Author-year-journal labels remain unresolved to DOI.

These are FEct reanalysis results and diagnostics. The source checkmark becomes true, a blank becomes false, and n.a. remains not_applicable. Each flag is named by its test: att_p_below_05, pretrend_p_above_05, placebo_p_above_05, carryover_p_above_05. A false diagnostic does not automatically prove a consequential error. breakdown_m is the reported sensitivity threshold; n.a. remains unavailable.

## Disclosure timing

The first arXiv version appeared on 27 September 2023. Match the final 49-paper roster against that version and any earlier individual reports before assigning disclosure dates.

## Sources and next step

[Study](https://arxiv.org/abs/2309.15983); [archive](https://doi.org/10.7910/DVN/9RJFZF).

Resolve original identities and recover machine-readable estimates from Dataverse or the detailed Supplement B. Freeze the assessment rule and same-audit comparisons before collecting citation outcomes.

## Rebuild

From the repository root, run `make cohorts-import` using saved originals, or
`make cohorts-fetch` to download the recorded source URLs and verify their hashes.
Run `make cohorts` for offline consistency checks and regeneration of this index.
