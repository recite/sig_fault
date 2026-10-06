# Synthesis estimand and inference

The scientific question is how publicizing a statistical problem changes citations
to affected papers. The synthesis estimates a narrower descriptive quantity:
the equally weighted average log relative citation-growth contrast in the three
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

Each synthesis includes one contrast per audit. Instrument strength and
inferential sensitivity are alternative classifications of the same IV evidence;
never count them as independent studies. The earlier two-audit summaries also
report their union and the exploratory AR-only screen. Equal audit weights define
the summary rather than allowing sample size or citation dispersion to choose
which critique dominates. The synthesis choices are retrospective, with component
estimates already known.

For `K` components with log estimates `b[j]`, standard errors `s[j]`, and degrees
of freedom `d[j]`, the estimate is `mean(b)`, with variance `sum(s^2)/K^2`.
The Welch–Satterthwaite degrees of freedom are
`sum(s^2)^2 / sum(s^4/d)`. Transform the estimate and both endpoints of the
corresponding t interval to percentages. Component variances are clustered by
article; the I4R sensitivity below instead uses disclosure-level uncertainty.

This calculation assumes independent component estimates. Intervals condition on
the included audits and classifications; they omit audit-selection and
between-audit generalization uncertainty, unmeasured exposure, database error,
and specification selection. They are not prediction intervals for a new critique.
The identity ledger checks DOI overlap among included original and control papers.
One included animal-study paper has no DOI. No detected DOI overlap prevents known
direct double counting but does not establish independence of scientific processes,
shared citing documents, or unobserved shocks across audits.

## I4R sensitivity

I4R remains a small, selected matched-case pilot, not one methodological audit.
The current eligible cases and exclusions are documented in the
[I4R results](../i4r/aggregate-results.md). Its component compares proportional
growth in affected and matched-control mean annual citations, counting all document
types in the full calendar years before and after first documented disclosure.

For disclosure `j`, let `T[j,t]` be the affected paper's count and `C[j,t]` its
weighted control count. With `T[t] = mean(T[j,t])` and `C[t] = mean(C[j,t])`, the
component is `log(T[post]/T[pre]) - log(C[post]/C[pre])`. This differs from averaging
individual case log ratios: highly cited papers contribute more to growth in the
group means. Both are reported separately.

With `Z[j] = (Tpre,Tpost,Cpre,Cpost)` and
`g = (-1/Tpre,1/Tpost,1/Cpre,-1/Cpost)` evaluated at group means, the delta-method
variance is `g' cov(Z) g / J`, with `J-1` degrees of freedom. This preserves
within-disclosure covariance across periods and between affected and control
counts. Inference conditions on the selected matches and is fragile with few
cases. Recurring disclosures or reused articles require dependence to be handled
explicitly. Nonpositive group-period means make the proportional contrast
unavailable; no pseudocounts are added.

The sensitivity adds I4R as a fourth equally weighted component. Call it an
equal-component descriptive summary. Pre-period differences, leave-one-case-out
results, and synthetic-control checks remain separate diagnostics. A weighted
article-fixed-effects/common-relative-period Poisson fit reproduces the aggregate
point estimate; event-specific period effects would estimate a different quantity.
The differing outcome definitions and exposure clocks remain in the synthesis.

## Reproduction and citation-source checks

`make synthesis` rebuilds the component analyses, the two-audit sensitivity
comparisons, the three-audit summary, and its I4R sensitivity. `R/meta.R` implements
the shared estimator. `scripts/synthesis.R` and `scripts/synthesis_secondary.R`
build the neuroscience/IV comparisons and I4R addition; `scripts/lazic_synthesis.R`
assembles the current three-audit results, manuscript table, and current status.
Tests independently verify Welch inference, geometric transformation, and rejection
of multiple rows with the same audit identity.

The two-audit OpenCitations sensitivity substitutes its neuroscience estimate for
the historical estimate on identical papers and years. It does not add an
independent audit or harmonize document types with Lal. The complete paired
OpenAlex comparison remains pending. Source contrasts measure how recorded counts
and estimates change when switching databases; neither index is assumed to be
truth, so a discrepancy alone is not an estimate of database bias.
