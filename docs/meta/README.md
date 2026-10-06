# Provisional synthesis across two methodological audits

The completed neuroscience and IV cohorts permit a common-window summary, while
the full OpenAlex neuroscience comparison and primary I4R article/review panels remain pending.
Every row below includes one estimate from each audit, with equal audit weights.
Alternative IV diagnostics are separate analyses of the same evidence.

| Neuroscience sample | IV diagnostic | Neuroscience (%) | IV (%) | Combined (%) | 95% interval |
| --- | --- | ---: | ---: | ---: | --- |
| Historical cohort | Effective F below 10 | -14.1 | -14.5 | -14.3 | [-29.0, 3.4] |
| Historical cohort | Inferential sensitivity | -14.1 | 23.9 | 3.1 | [-14.5, 24.4] |
| Historical cohort | Either diagnostic | -14.1 | 11.8 | -2.0 | [-18.2, 17.4] |
| Historical cohort | AR-only sensitivity | -14.1 | -44.0 | -30.6 | [-45.2, -12.2] |
| 2009 publication cohort | Effective F below 10 | -8.5 | -14.5 | -11.5 | [-25.8, 5.4] |
| 2009 publication cohort | Inferential sensitivity | -8.5 | 23.9 | 6.5 | [-10.6, 26.9] |
| 2009 publication cohort | Either diagnostic | -8.5 | 11.8 | 1.2 | [-14.4, 19.6] |
| 2009 publication cohort | AR-only sensitivity | -8.5 | -44.0 | -28.4 | [-42.8, -10.3] |

The combined estimate changes with the IV diagnostic. It is not evidence for
a uniform citation response, nor an estimate of the effect of the typical scientific error.
The AR-only rows are exploratory: their IV component has only three flagged papers.

A [secondary three-component synthesis](secondary.md) adds the proportional contrast
from the separately matched I4R annual-total analysis. It preserves the different
measurement and exposure definitions and is an exploratory descriptive extension.

See [methods](design.md), [component estimates](../../data/meta/audit_contrasts.csv),
[synthesis data](../../data/meta/synthesis.csv), and [status](../../data/meta/status.json).
Run `make synthesis` to reproduce these results and the manuscript table.
