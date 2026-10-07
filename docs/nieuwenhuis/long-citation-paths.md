# OpenAlex citation paths, 2009–2025

[Open the figure](../../figs/citation_paths_openalex.pdf).

This extends Figure 1's descriptive comparison to 2025 using OpenAlex. It follows the same 153 papers in every year: 76 flagged and 77 comparison papers. Each panel shows unadjusted annual citations per original paper, summarized by the median or mean. The vertical line marks publication of the critique in August 2011. These are citation paths, not estimates of the critique's effect.

The original papers appeared in 2009–2010. The first years therefore include partial publication years and zeros before a paper appeared. Downloads include citing publications through December 31, 2025; 2026 is excluded because it is incomplete. Completed API downloads do not establish complete database coverage, and indexing and publication-date errors remain possible.

The counts use the source comparison's existing rules: articles and reviews with verified references, excluding duplicate records, a work's citation to itself, and citations dated before the original paper. The same frozen canonical duplicate choices and source-verified overrides apply throughout. No new citations are fetched. Zero counts are filled only after verifying completed downloads and resolved identities for every paper. All 1,071 article-year counts for 2009–2015 must exactly equal the existing OpenAlex comparison panel before the figure can be generated.

Reproduce from the public repository inputs:

```sh
make nieuwenhuis-paths
```

- `scripts/nieuwenhuis_design/03_long_paths.py` prepares and validates counts, calls the plot script, and records the run.
- `scripts/nieuwenhuis_design/long_paths.R` renders the figure.
- [Article-year panel](../../data/nieuwenhuis/paths/panel.csv) and [annual summaries](../../data/nieuwenhuis/paths/annual_summary.csv) contain the plotted data.
- [Run receipt](../../data/nieuwenhuis/paths/receipts/03_long_paths.json) records input, code, and output hashes, coverage checks, fixed group sizes, and exact agreement with the existing panel.
