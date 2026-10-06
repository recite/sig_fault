# The neuroscience comparison using OpenCitations

Changing the citation source leaves the full-cohort growth comparison almost unchanged: -11.9% using OpenCitations and -11.5% using the historical Web of Science exports.
These estimates compare flagged and comparison papers' post/pre citation ratios, with 2010 as baseline and the 2012–2015 annual average afterward.

All 153 historical papers have complete API histories: 76 flagged and 77 comparison papers. The index supplies 48,597 incoming relationships across all years. Of these, 310 have no resolved publication year and remain unassigned to annual outcomes. Complete acquisition does not mean complete real-world citation coverage.

## Citation levels on the same papers

| Source | Group | Papers | Mean 2010 | Mean 2012–15 | Median 2010 | Median of paper post averages |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Web of Science | Comparison | 77 | 6.51 | 16.66 | 4.00 | 11.50 |
| Web of Science | Flagged | 76 | 9.43 | 21.37 | 5.00 | 15.62 |
| OpenCitations | Comparison | 77 | 8.19 | 19.52 | 6.00 | 13.75 |
| OpenCitations | Flagged | 76 | 11.59 | 24.34 | 6.00 | 17.75 |

Both sources record continued citation in both groups. OpenCitations records more citations in the baseline and post periods. That difference does not translate into a large change in their relative-growth comparison. Post medians above summarize each paper's annual post-period average; annual medians are available separately.

## Paired source discrepancies

| Post years | Contrast | Web of Science | OpenCitations | Source discrepancy | Paired 95% interval |
| --- | --- | ---: | ---: | ---: | --- |
| 2012 | Absolute citation change | 1.05 | 0.67 | -0.38 | [-1.62, 0.84] |
| 2012 | Growth ratio (%) | -14.14 | -13.62 | 0.61 | [-8.13, 11.57] |
| 2012-2015 | Absolute citation change | 1.78 | 1.42 | -0.36 | [-1.28, 0.56] |
| 2012-2015 | Growth ratio (%) | -11.53 | -11.86 | -0.36 | [-8.00, 9.24] |

The absolute discrepancy subtracts the two difference-in-changes estimates. The proportional discrepancy is the percentage change in the estimated growth ratio when replacing Web of Science with OpenCitations; it is not the percentage-point difference between displayed estimates. Intervals use 9,999 paired paper resamples within flag groups, seed 20261006. They condition on this cohort and the frozen database records.

## Dating and scope

The [full results](../../data/nieuwenhuis/opencitations_contrasts.csv) also restrict both sources to the same histories without unresolved publication years and separately to the 2009 publication cohort. The date-complete subset is selected; it is not another full-cohort estimate. No missing year is imputed or assumed to lie outside the analysis window.

OpenCitations counts dated citing works across document types. This is different from the pending OpenAlex article/review comparison. Shared upstream records, coverage, vintage and dating differences prevent calling either index ground truth. Similar aggregate contrasts do not validate every citation link or establish that publicity had no effect. This is another measurement of the same audit, not another independent study for the meta-analysis.

## Reproduce

```sh
make nieuwenhuis-opencitations
```

Acquisition is separate: `make nieuwenhuis-opencitations-fetch`. The collector uses the documented CSV representation when a large JSON response arrives truncated. Both formats undergo the same target-DOI, unique-relationship and count-endpoint checks. Cached raw responses, URLs, retrieval times and hashes are preserved.

See [design](design.md), [dictionary](data.md), [annual summaries](../../data/nieuwenhuis/opencitations_annual_summary.csv), [panel](../../data/nieuwenhuis/opencitations_panel.csv), and [API documentation](https://api.opencitations.net/index/v2).
