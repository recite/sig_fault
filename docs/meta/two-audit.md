# Citation changes across two methodological audits

The completed neuroscience and IV cohorts permit a common-window summary, while
the primary I4R article/review panels remain incomplete. The current three-audit
summary also reports substitution of OpenAlex neuroscience counts on the same papers.
Every row below includes one estimate from each audit, with inverse-variance weights.
Alternative IV diagnostics are separate analyses of the same evidence.

| Neuroscience sample | IV diagnostic | Neuroscience (%) | IV (%) | Combined (%) | 95% interval |
| --- | --- | ---: | ---: | ---: | --- |
| Historical cohort | Effective F below 10 | -14.1 | -14.5 | -14.3 | [-28.7, 3.1] |
| Historical cohort | Inferential sensitivity | -14.1 | 23.9 | 0.4 | [-16.5, 20.6] |
| Historical cohort | Either diagnostic | -14.1 | 11.8 | -3.1 | [-19.0, 15.8] |
| Historical cohort | AR-only sensitivity | -14.1 | -44.0 | -23.6 | [-37.9, -6.0] |
| 2009 publication cohort | Effective F below 10 | -8.5 | -14.5 | -10.5 | [-24.0, 5.4] |
| 2009 publication cohort | Inferential sensitivity | -8.5 | 23.9 | 1.3 | [-13.9, 19.3] |
| 2009 publication cohort | Either diagnostic | -8.5 | 11.8 | -1.5 | [-16.1, 15.5] |
| 2009 publication cohort | AR-only sensitivity | -8.5 | -44.0 | -17.2 | [-30.7, -0.9] |

The combined estimate changes with the IV diagnostic. It is not evidence for
a uniform citation response, nor an estimate of the effect of the typical scientific error.
The AR-only rows are exploratory: their IV component has only three flagged papers.

The small I4R pilot is excluded from pooling and remains a standalone case analysis.

A [source sensitivity](../../data/meta/opencitations_synthesis.csv) replaces the
neuroscience component with OpenCitations on the same papers and years. It does
not add another independent audit; see the
[measurement comparison](../nieuwenhuis/opencitations.md).

See [methods](design.md), [component estimates](../../data/meta/audit_contrasts.csv),
[synthesis data](../../data/meta/synthesis.csv), and [status](../../data/meta/status.json).
Run `make synthesis` to reproduce these results and the current three-audit summary.
