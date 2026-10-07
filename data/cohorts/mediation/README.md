# Mediation analysis in observational research

Judith J. M. Rijnhart and colleagues

Methods and reporting practices in observational mediation analyses

The inventory preserves 174 paper records and 174 assessment rows concerning 174 papers.

## Files

- `papers.csv`: one row per source paper ID, including unassessed roster entries.
- `assessments.csv`: source-level outcomes; multiple rows may belong to one paper.
- `source_records/`: selected original columns or an exact source-table extraction.
- `sources.csv`: exact download URLs, original-file checksums and local source paths.
- `study.json`: study-specific definitions, timing evidence and remaining work.

Original downloads are preserved in `private-data/cohorts/mediation/source/`.
The [shared dictionary](../dictionary.md) defines the normalized columns.

## Construction and outcomes

Keep all 174 rows and 48 columns of the semicolon-delimited source. The numbered bibliography is saved alongside the source CSV in the private source folder. CSV IDs contain gaps and run to 182; bibliography numbering runs to 174. Do not join those identifiers directly or silently assume row order.

method_num: 0 traditional mediation (123), 1 causal steps (14), 2 causal mediation (23), 3 joint significance (5), 4 change in coefficient (9). Other source fields include confounder_adjustment_yn_num, xm_int_yn_num, sensitivity_ana_yn_num and outcome-model details; their codebook requires further verification before recoding. Method choice or omitted reporting is not itself a verified error.

## Disclosure timing

Source files were publicly released on 25 October 2021. First disclosure of a paper-specific adverse finding is not established.

## Sources and next step

[Study](https://pmc.ncbi.nlm.nih.gov/articles/PMC8543973/); [archive](https://ndownloader.figshare.com/files/31176772).

Verify all 174 ID-to-bibliography links and obtain the complete variable label map. Identify diagnostics that bear on the original causal claim rather than treating any traditional method as an error.

## Rebuild

From the repository root, run `make cohorts-import` using saved originals, or
`make cohorts-fetch` to download the recorded source URLs and verify their hashes.
Run `make cohorts` for offline consistency checks and regeneration of this index.
