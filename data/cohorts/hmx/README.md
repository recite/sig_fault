# Interaction-model audit

Jens Hainmueller, Jonathan Mummolo and Yiqing Xu

Linearity, common support and conditional-effect diagnostics

The inventory preserves 22 paper records and 138 assessment rows concerning 22 papers.

## Files

- `papers.csv`: one row per source paper ID, including unassessed roster entries.
- `assessments.csv`: source-level outcomes; multiple rows may belong to one paper.
- `source_records/`: selected original columns or an exact source-table extraction.
- `sources.csv`: exact download URLs, original-file checksums and local source paths.
- `study.json`: study-specific definitions, timing evidence and remaining work.

Original downloads are preserved in `private-data/cohorts/hmx/source/`.
The [shared dictionary](../dictionary.md) defines the normalized columns.

## Construction and outcomes

Extract the published author PDF, Table A1, PDF page 27: 46 interactions in 22 papers. Author-year-journal labels are preserved as bibliographic references; they are not full titles. Earlier author drafts contain different classifications. All observed scores equal the sum of the three observed flags.

low_high_not_rejected: 1 means the low-versus-high difference is not rejected; severe_extrapolation: 1 is the authors' support flag; linearity_rejected: 1 means the linear model is rejected. Zero means unflagged on that diagnostic. Empty cells mean the test could not be conducted, not favorable evidence. Preserve these as distinct diagnostics; nonrejection alone is not proof of error. The published table has 44 low-high tests, 46 extrapolation assessments and 42 linearity tests.

## Disclosure timing

The SSRN first-posted date is 29 February 2016, earlier than journal publication. Whether every final-roster paper appeared in that version remains unresolved. The 2019 corrigendum only completes a bibliographic reference.

## Sources and next step

[Study](https://doi.org/10.1017/pan.2018.46); [archive](https://doi.org/10.7910/DVN/Q1V0OG).

The numbered pipeline resolves all 22 DOIs and estimates the formal-publication contrast. Verify the earliest SSRN roster before making a first-disclosure claim. See pipeline/README.md for citation results, diagnostic-specific comparisons and overlap exclusions.

## Rebuild

From the repository root, run `make cohorts-import` using saved originals, or
`make cohorts-fetch` to download the recorded source URLs and verify their hashes.
Run `make cohorts` for offline consistency checks and regeneration of this index.
