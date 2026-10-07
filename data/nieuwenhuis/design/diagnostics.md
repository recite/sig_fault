# Comparability and weighting diagnostics

The design compares papers assessed in the same audit and published in the same journal/year.
The balance check uses original research characteristics and pre-critique citations.
It does not treat classification as randomized.

Journal/year standardization leaves an imbalance in study populations: 25% of flagged papers
study humans, versus about 55% of comparison papers. The richer comparison additionally holds
human/nonhuman status and within/between-subject design fixed. Unknown subject type remains
unknown. It retains 68 flagged and 52 comparison papers in 20 supported cells.
The balance table also shows a remaining mouse-study imbalance. Matching exact species
and within/between-subject design retains 49 flagged and 46 comparison papers in 19 cells.

| Source | Comparison | Papers, flagged / other | Proportional change, % | 95% interval |
| --- | --- | ---: | ---: | ---: |
| wos | journal_year | 76 / 77 | -8.5 | [-24.7, 11.2] |
| wos | same_sample_journal_year | 68 / 52 | -7.4 | [-26.9, 17.2] |
| wos | study_type | 68 / 52 | -5.6 | [-27.7, 23.3] |
| wos | species_sample_journal_year | 49 / 46 | -5.5 | [-27.0, 22.4] |
| wos | species | 49 / 46 | -7.2 | [-30.3, 23.6] |
| openalex | journal_year | 76 / 77 | -7.3 | [-22.6, 10.9] |
| openalex | same_sample_journal_year | 68 / 52 | -8.1 | [-26.7, 15.1] |
| openalex | study_type | 68 / 52 | -6.5 | [-27.5, 20.6] |
| openalex | species_sample_journal_year | 49 / 46 | -4.7 | [-25.0, 21.1] |
| openalex | species | 49 / 46 | -6.1 | [-28.4, 23.3] |

The middle comparison applies the original adjustment to the retained sample, separating
the change in sample from the additional adjustment. Models use 2010 versus 2012–2015.

## An explicit equal-flagged-paper contrast

This additive difference gives every flagged paper equal weight and compares its change with
the average change of comparison papers in its cell. Effects may differ across cells.

| Source | Comparison | Additional citations per paper per year | Approximate 95% interval |
| --- | --- | ---: | ---: |
| wos | journal_year | 0.61 | [-3.79, 5.00] |
| wos | same_sample_journal_year | 1.55 | [-4.17, 7.27] |
| wos | study_type | 0.33 | [-6.37, 7.02] |
| wos | species_sample_journal_year | 2.62 | [-2.82, 8.07] |
| wos | species | 0.69 | [-6.76, 8.14] |
| openalex | journal_year | -0.41 | [-4.80, 3.98] |
| openalex | same_sample_journal_year | 0.09 | [-5.75, 5.93] |
| openalex | study_type | -1.17 | [-8.04, 5.70] |
| openalex | species_sample_journal_year | 1.03 | [-3.91, 5.98] |
| openalex | species | -0.57 | [-8.05, 6.91] |

Equal-flagged estimates are independently checked against their weighted-regression identity.
Intervals use HC3 and residual t degrees of freedom, conditional on cells and weights.
Ten human/nonhuman/design cells have one comparison paper; six have one flagged paper.
Within-arm
variances cannot be estimated separately in those singleton cells. The HC3 intervals are
model-based approximations, not exact randomization or fully nonparametric intervals.

## What the checks establish

The original groups differ in study populations. Holding study population
and within/between-subject design fixed leaves similar estimates on the same sample.
This supports the comparison against that specific explanation. It does not show that all
possible determinants of citation growth are balanced. The balance file also reports species,
author-country labels and baseline citation counts, including standardized differences.

The linear fixed-effects weights are nonnegative in this common-date balanced design; their
formula and numerical checks are recorded. PPML information shares describe curvature
of the fitted objective, not robust variance or an exact heterogeneous-effect average. The
equal-flagged contrast makes its target population and article weights explicit.

[Design and assumptions](../../../docs/nieuwenhuis/design-diagnostics.md).
`design_characteristics.csv` records the original labels and every sample decision;
`balance.csv`, `estimation_weights.csv` and `equal_flagged_influence.csv` record the checks.
