# Synthetic difference-in-differences around the pseudoreplication audit

This retrospective extension was specified after the earlier audit estimates and
annual summaries were inspected, and before fitting synthetic DiD weights. It is
not a preregistration. The previous multi-year plan remains a separate analysis;
this stage adds synthetic DiD at the author's request. It does not replace the
existing synthesis or select a result by its sign, interval, or pre-period fit.

## Target and comparison

Estimate the mean change in annual citations attributable to the 2017 publicity
among the classified Lazic-audit papers published by 2013 and not subject to the
already documented 2013 warning. Each flagged paper and each follow-up year
receives equal target weight. The outcome is distinct OpenCitations citing works,
all indexed types. Compare 2018–2020 with 2014–2016, omitting the disclosure year
2017. This population contains 50 flagged and 26 comparison papers. Preserve
unknown audit classifications as unknown, outside the estimand; do not impute them.

The estimator uses nonnegative comparison-paper and pre-year weights, each summing
to one, with article and time intercepts. It estimates an additive count effect,
not the proportional contrast used in the existing meta-analysis. Identification
requires the weighted comparison trajectory, after the weighted pre-period level
adjustment, to represent the flagged papers' absent-publicity trajectory. No
anticipation, no differential coincident shock, and no effect on comparison papers
are needed for a total publicity-effect interpretation. Otherwise the contrast is
the differential response between the two audit groups. All papers share one
publicity event, so inference is conditional on that event.

## Data and feasibility

Use the frozen article inventory, prior-warning roster, and completed citation
panel. Require one verified classification per article, unique article/year keys,
complete counts in every requested year, and publication before the first baseline
year. Never convert a missing history to zero or fill years before publication.
Save every original article's inclusion or exclusion reason for every specification.

Nieuwenhuis has no common multi-year, fully post-publication baseline before its
2011 critique. Lal's 2024 publication followed a 2021 manuscript, and Hainmueller,
Mummolo and Xu's 2018 publication followed a 2016 draft whose full roster is not
verified. Their formal-publication histories cannot be labeled unexposed histories
for first disclosure. Existing I4R synthetic comparisons have very few targets.
Lazic is selected on timing and baseline support, not synthetic-control results.

## Models and diagnostics

Use the authors' `synthdid` implementation, pinned to commit
`70c1ce3eac58e28c30b67435ca377bb48baa9b8a` (version 0.0.9), with documented default
regularization, intercepts, sparsification, and convergence settings. Save model
objects and package/session information. Verify the estimate independently as the
post-period treated-minus-weighted-control gap minus its weighted pre-period gap.
Export all paper and time weights, their maximum and effective counts, weighted publication-cohort and split-unit-design balance, raw group
means and medians, the level-adjusted synthetic path, and pre-period fit error.

Before the full-window fit, fit a fresh model to 2014–2016 with 2016 designated
as the placebo follow-up and 2014–2015 as the training years. This withholds the
flagged papers' 2016 outcomes from fitting. Comparison papers' 2016 outcomes enter
time-weight estimation, as SDID requires. No 2018–2020 data or tuning enters this
check. Report its gap beside the same-sample ordinary DiD gap, without treating a
small gap or a nonsignificant estimate as proof of validity. No sample is excluded
or specification changed according to this diagnostic.

Estimate all of the following:

1. Main: published by 2013, pre 2014–2016, post 2018–2020.
2. Longer baseline: published by 2012, pre 2013–2016, post 2018–2020
   (30 flagged, 14 comparison papers). Repeat the last-pre-year check, training
   on 2013–2015 and withholding flagged outcomes in 2016.
3. Older population with the original three-year baseline (2014–2016) and
   2018–2020 follow-up. This separates sample restriction from baseline extension.
4. Shorter follow-up: main population and baseline, post 2018–2019.
5. Ordinary equal-paper DiD on every identical sample and time window, with
   a Welch interval from each paper's change. This is also the balanced-panel
   article/year linear fixed-effects point estimate. It distinguishes estimator
   differences from sample or follow-up changes.

## Uncertainty and reporting

Use the package's whole-article bootstrap with 1,999 accepted draws and recorded
seeds, preserving each resampled article's entire history. Explicitly enable
re-estimation of both paper and time weights. The official algorithm retains the
original fit's regularization and stopping tolerances, while refitting weights;
this is conditional-tuning bootstrap inference, not a full tuning-selection
bootstrap. Save each accepted bootstrap estimate and sampled article indices, plus any rejected
single-group attempts. Verify the recorded resampling against the official variance
method on a deterministic test fixture. Report its standard error and normal 95% interval. It assumes independent
articles and adequate effective information, allows serial dependence within an
article, and does not account for dependence between originals from shared citing
papers. It is not randomization inference or uncertainty over independent audits.

Report the pre-period placebo point estimates and prediction errors as diagnostics,
not an extra significance-testing family. Save all specified estimates even if
weights concentrate or validation fails. No synthetic estimate is added as an
independent study to the meta-analysis. An external design review precedes fitting;
code and interpretation receive independent review and numerical verification.

Sources: [Arkhangelsky et al. (2021)](https://doi.org/10.1257/aer.20190159),
[estimator documentation](https://synth-inference.github.io/synthdid/reference/synthdid_estimate.html),
[variance documentation](https://synth-inference.github.io/synthdid/reference/vcov.synthdid_estimate.html),
and [pinned variance implementation](https://github.com/synth-inference/synthdid/blob/70c1ce3eac58e28c30b67435ca377bb48baa9b8a/R/vcov.R).
