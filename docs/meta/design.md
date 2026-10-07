# Synthesis estimand and inference

The scientific question is how publicizing a statistical problem changes citations
to affected papers. The synthesis estimates a narrower descriptive quantity:
the inverse-variance weighted average log relative citation-growth contrast in the three
assembled audits. Within each audit, the contrast compares flagged and comparison
papers' post/pre citation ratios. Transforming that average as
`100 * (exp(mean_log_ratio) - 1)` gives the percentage difference corresponding to
the geometric average ratio. It is not a pooled-paper ratio or the average effect
of publicizing an error across science.

## Populations, exposure dates, and outcomes

- **Nieuwenhuis:** the historical analysis cohort, after excluding two invalid
  citation histories. The source assessed neuroscience papers from selected
  journals in 2009–2010 for an erroneous comparison of statistical significance.
  The main synthesis compares 2010 with 2012 around the August 2011 critique,
  using the historical Web of Science exports. Papers published in 2010 have a
  partial publication-year baseline. A 2009-publication cohort is a sensitivity.
- **Lal:** the identified political-science papers in an instrumental-variables
  audit. The instrument-strength screen uses all assessed papers; inferential
  sensitivity uses papers with at least one analytically significant estimate.
  Each paper is flagged if any assessed design meets the selected diagnostic.
  Counts include OpenAlex articles and reviews, comparing 2023 with 2025 around
  formal publication in 2024. The critique circulated earlier, so that publication
  is not first exposure to previously unknown criticism. Adverse diagnostics do
  not establish that the original substantive conclusions are false.
- **Lazic:** the complete deposited sample of prenatal-exposure animal experiments,
  excluding unclear classifications and one paper with a documented earlier
  public warning about the same problem. The source assessed whether dependent
  observations were treated as independent replications. The preprint and
  identified dataset appeared in September 2017; journal publication followed in
  April 2018. The synthesis uses 2016 versus 2018 and also reports the audit's main
  2016-versus-2019 contrast. Counts include all indexed OpenCitations document
  types, including distinct book chapters.

The [component ledger](../../data/meta/lazic_components.csv) records the estimates,
standard errors, and degrees of freedom used in every synthesis. The audit-level
[neuroscience and IV estimates](../../data/meta/audit_contrasts.csv) and
[animal-study estimates](../../data/lazic/estimates.csv) record the fitted sample
sizes. Article fixed-effects Poisson fits omit papers with zero citations in both
selected years; the animal-study absolute contrasts and descriptive summaries
retain those papers. These populations must not be inferred from the size of the
original inventory alone.

Public availability is not verified readership. A causal interpretation requires
that the flagged and comparison papers would otherwise have followed comparable
proportional citation trajectories. Assessment status is not randomized; paper
age, topic, quality, and pre-existing trends can differ. Comparisons assessed in
the same audit may themselves respond to publicity. Thus the measured difference
need not capture the critique's total influence on citations, much less reliance
on its affected findings.

## Weighting and uncertainty

The primary synthesis uses inverse sampling variance weights on each audit's log
relative-growth contrast: `w[j] = (1/s[j]^2) / sum(1/s^2)`. The estimate is
`sum(w*b)` and its standard error is `sqrt(1/sum(1/s^2))`. We use the standard
normal fixed-effect method in `metafor::rma.uni(method="FE", test="z")` and
transform the estimate and interval endpoints as `100 * (exp(b) - 1)`.
This is a precision-weighted mean of the included audit effects, not an assertion
that every audit has the same effect. Variances are estimated inputs; the usual
normal approximation conditions on them. One-sided 95% lower bounds use the
95th percentile of the standard normal distribution.

Each analysis contains one contrast per audit. Alternative IV definitions, citation
sources and follow-up years do not create additional independent studies. Weights
are recalculated when a source changes its component variance. Choices are
retrospective, after inspecting the component results. The I4R pilot is excluded
from every pooled estimate; its three matched cases remain standalone evidence.

The pipeline exports each component's normalized weight and leave-one-audit-out
estimates. Equal-audit weighting remains a sensitivity, using the existing
Welch--Satterthwaite interval. A random-effects sensitivity uses REML and modified
Knapp--Hartung inference (`method="REML", test="adhoc"`), with two degrees of
freedom for three audits. This prevents the adjustment from shrinking standard
errors below the unadjusted values. Random-effects weights are proportional to
`1/(s[j]^2 + tau^2)`. Its interval concerns the model's mean across audit effects;
it is not a prediction interval for a future critique. With three audits,
between-audit variation is estimated imprecisely.

The main output records Cochran's Q and its degrees of freedom. Its fixed-effect
`tau2=0` is imposed by that model, not evidence of homogeneous effects. The
random-effects output separately estimates tau-squared. Cross-audit independence
is assumed. The identity ledger checks known DOI overlap among original and
comparison papers, but distinct papers can share citing documents or shocks.

[Official metafor documentation](https://wviechtb.github.io/metafor/reference/rma.uni.html)
describes the estimators and finite-sample adjustment.

## I4R standalone checks

I4R remains a small, selected matched-case pilot. Its case-level proportional
contrasts, pre-period differences, leave-one-case-out results and synthetic
controls remain available in the [I4R results](../i4r/aggregate-results.md).
They do not enter the cross-audit synthesis.

## Reproduction and citation-source checks

`make synthesis` rebuilds the component analyses, the two-audit sensitivity
comparisons, the three-audit summary, and standalone I4R checks. `R/meta.R` implements
the shared estimator. `scripts/synthesis.R` and `scripts/synthesis_secondary.R`
build the neuroscience/IV comparisons and standalone I4R checks; `scripts/lazic_synthesis.R`
assembles the current three-audit results, manuscript table, and current status.
Tests independently verify Welch inference, geometric transformation, and rejection
of multiple rows with the same audit identity.

The two-audit OpenCitations sensitivity substitutes its neuroscience estimate for
the historical estimate on identical papers and years. It does not add an
independent audit or harmonize document types with Lal. The OpenAlex sensitivity likewise substitutes its source-specific neuroscience
contrast into the three-audit synthesis, keeping the audit identities and time windows fixed,
while recalculating precision weights. Articles/reviews and the broader document-type definition
are reported separately. Source contrasts measure how recorded counts
and estimates change when switching databases; neither index is assumed to be
truth, so a discrepancy alone is not an estimate of database bias.
