# Synthetic controls for the supported I4R cases

These retrospective checks use the same annual all-type citation data as the matched-case analysis. We replace three nearest controls with convex combinations of all structurally eligible donors, without the citation caliper or text ranking. The disclosure year is omitted. Each target has its own citation scale and counterfactual; the case gaps are not pooled.

| Paper | Pre-years | Donors | Pre-fit RMS error | Held-out year: actual / predicted | Post year: actual / synthetic | Post gap | Change in gap |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Parental leave | 2018;2019;2020 | 194 | 0.00 | 6.0 / 8.4 | 9.0 / 9.6 | -0.6 | -0.6 |
| Fast internet | 2020;2021;2022;2023 | 218 | 10.52 | 125.0 / 148.0 | 137.0 / 100.3 | +36.7 | +37.9 |
| Inventor clusters | 2022;2023 | 198 | Not fit: fewer than three pre-years | — | — | — | — |
| Electrification | 2017;2018;2019;2020 | 117 | 0.00 | 34.0 / 40.5 | 28.0 / 35.2 | -7.2 | -7.2 |

The held-out prediction fits weights on all but the last pre-disclosure year. The final synthetic path refits weights using every pre-year. Pre-fit error measures this final fit; it is not out-of-sample accuracy. Post gap is actual minus synthetic citations in the year after disclosure; change in gap subtracts the final pre-year gap. None is a significance test.

## Sensitivity to donor weights

| Paper | Specification | Post gap | Held-out prediction | Largest weight | Effective donors |
| --- | --- | ---: | ---: | ---: | ---: |
| Parental leave | main | -0.6 | 8.4 | 0.102 | 20.4 |
| Parental leave | ridge_0.01 | -0.6 | 8.4 | 0.100 | 20.7 |
| Parental leave | omit_largest_donor | -0.6 | 8.8 | 0.137 | 15.8 |
| Fast internet | main | +36.7 | 148.0 | 0.646 | 2.1 |
| Fast internet | ridge_0.01 | +13.7 | 133.6 | 0.479 | 2.9 |
| Fast internet | omit_largest_donor | -57.3 | 113.3 | 0.689 | 1.9 |
| Electrification | main | -7.2 | 40.5 | 0.070 | 29.0 |
| Electrification | ridge_0.01 | -7.4 | 40.4 | 0.069 | 29.6 |
| Electrification | omit_largest_donor | -8.6 | 41.1 | 0.066 | 24.3 |

The largest-donor check removes the donor with the largest weight in the full-pre-period main fit. Its held-out prediction therefore is a sensitivity calculation, not a clean validation prediction: that donor removal uses the last pre-year. The main held-out prediction and fixed-ridge prediction do not use that year's citations to fit or select donors.

All donor weights and eligibility decisions are saved in [data/i4r/synthetic](../../data/i4r/synthetic). The [design](synthetic-design.md) defines the fitting, validation and sensitivity rules. Short histories and many possible donor combinations limit identification even when in-sample fit is close. A causal reading also requires no anticipation, no coincident target-specific shock and unexposed donors. These assumptions are not established by the optimization.
