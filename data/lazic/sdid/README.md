# Synthetic DiD for the pseudoreplication audit

Citations are distinct OpenCitations works per original article per year, all indexed types.
Negative estimates mean fewer citations than the weighted comparison trajectory predicts.

| Sample/window | Flagged/control | Synthetic DiD (95% interval) | Ordinary DiD (95% interval) |
|---|---:|---:|---:|
| Main | 50/26 | -0.89 [-2.01, 0.22] | -0.78 [-1.86, 0.30] |
| Older, four pre-years | 30/14 | -0.82 [-2.13, 0.48] | -0.88 [-2.37, 0.62] |
| Older, three pre-years | 30/14 | -0.84 [-2.22, 0.54] | -0.55 [-1.99, 0.88] |
| Two post-years | 50/26 | -0.84 [-1.81, 0.14] | -0.66 [-1.72, 0.41] |

Main synthetic comparison: effective donor count 25.86 of 26; largest donor weight 4.42%.

| Sample/window | Held-out 2016 actual | Predicted | Synthetic DiD gap | Ordinary DiD gap |
|---|---:|---:|---:|---:|
| Main | 3.68 | 4.04 | -0.36 | -0.20 |
| Older, four pre-years | 2.70 | 2.87 | -0.17 | -0.43 |
| Older, three pre-years | 2.70 | 2.88 | -0.18 | 0.00 |
| Two post-years | 3.68 | 4.04 | -0.36 | -0.20 |

## Interpretation and reproduction

These are additive comparisons for older classified papers, not new independent audits.
The main sample uses 2014–2016 and 2018–2020. The older four-year baseline starts in 2013;
the older three-year fit holds its population fixed. The shorter follow-up ends in 2019.
Intervals use 1,999 whole-article bootstrap draws with paper/time weights refitted,
conditional on original regularization. Ordinary DiD uses Welch uncertainty on article changes.
Neither interval is randomization inference or covers variation across publicity events.
The held-out check fits anew without flagged 2016 or post-disclosure outcomes in weights.
Comparison 2016 counts do enter its time weights. Donor weights remain broadly spread.
The synthetic comparison does not improve the main held-out prediction over ordinary DiD.
The older four-year fit assigns zero time weight to 2013 in its baseline adjustment,
although that year still informs donor fitting. Its similarity to the three-year fit
therefore supplies limited additional reassurance. Publication-cohort and split-unit-design
balance also change little after weighting. All specified comparisons remain reported.

Run `make lazic-sdid` from the repository root after restoring `renv.lock`.
The numbered stages verify original identities, complete counts and sample dispositions.
`paper_weights.csv` and `time_weights.csv` contain all estimation weights; `balance.csv`
reports cohort and split-unit composition. `bootstrap_indices.csv` refers to article order
in `models.rds`, also reproduced by `paper_weights.csv` within each specification.
`bootstrap.csv` retains all accepted estimates. Seeds, rejected attempt counts, pinned software
and transitive input/code/output hashes are recorded. Missing counts never become zero.

[Design and sources](../../../docs/lazic/synthetic-did-design.md).
