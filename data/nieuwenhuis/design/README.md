# Citation comparisons within journal and publication year

All 153 original papers have comparison support within their journal and publication year.
The ten groups contain 76 flagged and 77 comparison papers. No papers are dropped for lack
of group support. The smallest group has three flagged papers and one comparison paper.

Article fixed effects absorb baseline citation levels. Journal/publication-year groups
have separate calendar-year effects, allowing different aging and journal citation paths.
The comparison asks whether flagged papers' citations change differently within these groups.

| Source | Sample | Window | Model | Estimate | 95% interval | Flagged / comparison |
| --- | --- | --- | --- | ---: | ---: | ---: |
| wos | all | longer_followup | PPML | -8.5% | [-24.7, 11.2]% | 76 / 77 |
| wos | all | longer_followup | OLS | 0.9 | [-2.7, 4.5] | 76 / 77 |
| wos | all | first_followup | PPML | -8.8% | [-24.7, 10.4]% | 76 / 77 |
| wos | all | first_followup | OLS | 0.4 | [-2.7, 3.6] | 76 / 77 |
| wos | published_2009 | longer_followup | PPML | -8.8% | [-25.5, 11.8]% | 44 / 47 |
| wos | published_2009 | longer_followup | OLS | 2.3 | [-2.0, 6.5] | 44 / 47 |
| wos | published_2009 | first_followup | PPML | -8.1% | [-24.6, 12.0]% | 44 / 47 |
| wos | published_2009 | first_followup | OLS | 2.0 | [-1.9, 5.9] | 44 / 47 |
| wos | published_2009 | publication_year_diagnostic | PPML | 7.6% | [-35.5, 79.7]% | 42 / 46 |
| openalex | all | longer_followup | PPML | -7.3% | [-22.6, 10.9]% | 76 / 77 |
| openalex | all | longer_followup | OLS | -0.0 | [-3.6, 3.5] | 76 / 77 |
| openalex | all | first_followup | PPML | -8.4% | [-23.7, 9.9]% | 76 / 77 |
| openalex | all | first_followup | OLS | -0.9 | [-4.1, 2.3] | 76 / 77 |
| openalex | published_2009 | longer_followup | PPML | -9.9% | [-25.7, 9.2]% | 44 / 47 |
| openalex | published_2009 | longer_followup | OLS | 0.7 | [-3.1, 4.6] | 44 / 47 |
| openalex | published_2009 | first_followup | PPML | -9.1% | [-25.1, 10.5]% | 44 / 47 |
| openalex | published_2009 | first_followup | OLS | 0.3 | [-3.4, 4.0] | 44 / 47 |
| openalex | published_2009 | publication_year_diagnostic | PPML | 24.6% | [-21.2, 97.0]% | 43 / 47 |

The baseline is 2010; longer follow-up is 2012–2015, and first follow-up is 2012.
The publication-year diagnostic compares 2009 with 2010 for 2009 originals only.
Its baseline is a partial publication year. OLS estimates are citations per paper per year;
PPML estimates are percentage changes in relative citation growth. Intervals cluster by
article, with the recorded finite-sample adjustment and t(G−1) reference.

The proportional and additive models impose common within-group effects. Causal interpretation
requires comparable absent-publicity growth within the journal/publication-year groups,
on the corresponding scale. Shared citing papers and publicity shocks can create dependence
across originals not represented by article clustering.

[Standardized trajectories](../../../figs/journal_cohort_paths.pdf) use the flagged papers'
journal/publication-year composition for both groups. The comparison weights depend only on
group membership, not citations. Medians describe the reweighted article distribution; they
are not averages of group medians. These descriptive weights differ from the regression's
implicit weighting, so the plotted growth ratio need not equal the PPML coefficient.

The raw trajectories remain Figure 1 in the manuscript. Full support, weights, annual paths,
pointwise annual estimates and model exclusions are saved beside this report.

[Design and assumptions](../../../docs/nieuwenhuis/journal-cohort-design.md).
