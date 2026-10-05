# Analysis guide

## Main specification

The main regression uses `fixest::fepois` on 2010 and 2012–2015, with article and year fixed effects and a flagged-paper × post-period term. The outcome is annual citation counts including zeros. We report `100 * (exp(beta) - 1)`, a relative post/pre citation change. Article-clustered covariance uses `ssc(K.adj = TRUE, K.fixef = "nonnested", K.exact = FALSE, G.adj = TRUE, G.df = "min", t.df = "min")`; intervals use `t(G - 1)` critical values. One-sided lower bounds use the 0.95 quantile and two-sided intervals the 0.975 quantile, then transform from the log scale. Bounds appear in the appendix, not the headline.

The main text emphasizes the observed median and mean trajectories and post-publicity qualification codes. Rising medians show continued use beyond a few highly cited papers; they do not identify a counterfactual citation path. Percentage effects and absolute citation differences are different estimands and may have different signs.

The proportional model variations add journal-by-year effects, publication-cohort-by-year effects, or both; the remaining rows preserve the baseline fixed effects and change only the labeled sample or post window. All-zero article histories within a particular fit imply an infinite negative article intercept and no slope information. The pipeline explicitly removes those histories, reports their IDs and observation counts, and rejects any additional silent removal. The main model retains all 153 papers.

The proportional bootstrap resamples whole articles within groups, uses 9,999 draws and seed 31415, and computes each baseline estimate from the exactly equivalent ratio of group post/pre mean ratios. A draw with a zero group mean fails the build rather than being silently discarded.

`tabs/proportional.csv` and `tabs/proportional_years.csv` contain coefficients on the log scale, ratios, percentage transformations, two-sided intervals, one-sided lower bounds, and sample accounting. `tabs/linear_fe.csv` contains the absolute fixed-effects comparison. In `tabs/results.json`, `main` is the proportional model; `absolute_comparison` names the original absolute estimand explicitly. Existing absolute sensitivity outputs retain their units.

## Claims and computations

| Question | Quantity | Output |
| --- | --- | --- |
| Did typical papers remain in use? | Annual group medians and share of papers with higher post-period annual means | `tabs/annual.csv`, `tabs/results.json` |
| Did proportional citation growth differ? | Relative post/pre ratio with article and year effects | `tabs/proportional.csv` |
| How large a relative decline is excluded under the model? | One-sided 95% lower bound on the ratio, transformed to percent | `tabs/proportional.csv` |

### Absolute comparisons and coding

| Question | Quantity and denominator | Computation | Output | Interpretation |
| --- | --- | --- | --- | --- |
| Did flagged papers continue to attract citations? | Annual mean and median citing documents per included source paper, with zero years retained | `annual_summary()` | `tabs/annual.csv`, `figs/citation_paths.pdf` | Describes the covered papers and database records |
| Did citations change differently after the critique? | Each paper's 2012–2015 annual average minus 2010, then flagged minus comparison | `article_changes()`, `estimate_change()` | `tabs/estimates.csv`, `tabs/levels.csv` | Relative change; a causal interpretation requires comparable counterfactual trends |
| Does the comparison depend on data construction or sample? | Same contrast with named changes to inclusion, timing, or adjustment | `scripts/run_all.R` | `tabs/estimates.csv` | Restricted samples are different populations, not interchangeable estimates |
| Was citation growth already different? | 2010 minus 2009 among papers published in 2009 | Same functions, restricted cohort and years | Final row of `tabs/estimates.csv` | Checks an observable implication of comparable trends; the short publication-year baseline limits the diagnostic |
| Do citing papers acknowledge concerns? | Recorded acknowledgment among completed historical ratings | `read_coding()`, `wilson_interval()` | `tabs/coding_counts.csv`, `tabs/results.json` | Statements in citing papers, not authors' awareness or validity of every cited finding |

## Statistical choices

The absolute comparison gives equal weight to source papers. It averages post-critique years within each paper before calculating a between-group contrast. Its Welch interval permits unequal variances and keeps repeated observations on each paper together. The adjusted comparison regresses the paper-level change on the error flag, journal, and publication cohort, using HC3 standard errors. Error status is not randomized; no permutation test treats it as randomized.

The mean is appropriate for the number of citations received per paper. Medians describe a different feature of the distribution and are plotted separately. Whole-paper bootstrap and leave-one-paper-out calculations assess sampling approximation and influence. The bootstrap resamples within groups, uses a local fixed seed in the build script, and retains every draw. It does not model dependence across papers. The rate of shared citing documents is reported as a diagnostic of that assumption.

The main post period starts in 2012. Later-window comparisons retain 2010 as the baseline and exclude the unused intermediate years. The potentially-serious-error comparison retains the original no-error comparison group. The annual contrast figure uses simultaneous Bonferroni intervals for its five comparisons; the sensitivity table uses pointwise intervals and does not select models by significance.

These estimates are retrospective and conditional on the available literature sample and citation exports. There is no assignment mechanism, random sample of all science, measured readership intervention, instrument, or regression discontinuity. The paper therefore does not identify a population-wide causal effect or the effect of a reader becoming aware of the error.

## Validation

The build checks classification agreement, unique keys, source-record membership, row conservation, recovery of the malformed export, duplicate definitions, missing whole histories, and complete paper-year grids. Data-source hashes accompany the generated output. Tests reconstruct the absolute estimate and interval independently from a citation-count matrix, compare its standard error with the equivalent paper-level HC2 regression, and recover a known planted change from synthetic panel data. The proportional tests compare the Poisson fixed-effects coefficient and clustered covariance with an explicit dummy-variable regression and independent sandwich calculation, recover a planted multiplicative change, and verify zero-history accounting.

The data audit distinguishes true zeros within exports from missing histories; identifies the two unreliable searches by chronology and target-self matches; and retains unknown coding separately from false links and completed ratings. Every model uses the same producing functions. Generated tables, manuscript macros, README values, and JSON summaries consume the same results object.

Identification checks consider publication timing, delayed response, different pre-critique growth, exposure to a general critique, publication-cohort composition, and sample coverage. Controls cannot establish parallel trends. Positive estimates do not establish an increase caused by publicity, and an interval covering zero does not establish no effect. The source review's “potentially serious” classification is not treated as proof that a paper's main conclusions are false.

The analysis does not reproduce a second rater's reliability statistic because the second item-level coding is not in the available materials. It also does not reconstruct missing or invalid original citation searches from a modern citation database: database revisions would change the measurement source and historical coverage. Original records are retained so that replacement histories can be incorporated if recovered.
