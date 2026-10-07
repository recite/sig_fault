# Citation changes after adverse scientific assessments

This extension combines the completed psychology replication study with the three
existing methodological audits. The individual results have already been seen;
this is a retrospective synthesis, not a preregistered test.

## Estimand

For each study, compare the post/pre citation ratio of papers receiving an adverse
assessment with the corresponding ratio of comparison papers. Pool the log ratios
using inverse estimated sampling variances and report `100 * (exp(beta) - 1)`.
The target is the precision-weighted mean contrast in the included studies over
their stated follow-up windows. It is not the average effect across all scientific
papers, all errors, or all possible audits.

The broader question is whether adverse assessments are followed by lower relative
citation growth. The three methodological audits and the psychology replication
project remain separately identified: an unsuccessful replication is not evidence
of a particular statistical error. The within-project replication contrast also
includes any citation benefit from a successful replication. It cannot isolate
that benefit from the penalty for an unsuccessful replication.

A causal reading requires comparable untreated proportional citation trajectories
within each study. Same-audit comparison papers can themselves respond to the
announcement. Formal publication or a project announcement can amplify earlier
reports, so these estimates need not measure first disclosure. Public availability
does not establish that each citing author read the assessment.

## Component selection and timing

Use one contrast per independent study in each synthesis:

- Nieuwenhuis: the historical 153-paper cohort, Web of Science, 2010 versus 2012.
- Lal: effective F below 10, OpenAlex articles/reviews, 2023 versus 2025. Substitute
  inferential sensitivity in a separate analysis; never count both as studies.
- Lazic: the classified cohort after the earlier-publicity exclusion, OpenCitations,
  2016 versus 2018. The existing 2019 follow-up remains a sensitivity.
- Psychology replication project: 98 original papers, OpenAlex articles/reviews,
  2012–2014 versus 2016–2018, fixed journal composition and the source's replication
  judgments. Use the journal-standardized log growth ratio and its stratified
  article-bootstrap standard error.

The RPP multi-year window is its existing primary specification. Also compute its
2014-versus-2016 contrast before pooling as a timing sensitivity, using identical
journal weights and bootstrap rules. The other three studies retain their common
one-year-before/one-year-after windows. No citation contrast is selected by its
sign or significance.

Keep the three-audit synthesis as a distinct stratum. The four-study synthesis is
a broader summary, not an update that changes the replication result into an error
classification. The three selected I4R cases remain outside all pooled estimates.
Do not append inventories lacking an analyzed comparison or a usable follow-up
period. Track their present status separately from completed analyses.

## Inference and validation

Use the existing `R/meta.R` inverse-variance estimator. Report study weights,
leave-one-study-out results, and REML with modified Knapp–Hartung intervals as
sensitivity analyses. The main normal interval conditions on included studies and
estimated component variances. The random-effects interval concerns its modeled
mean, not the outcome of an unobserved future audit.

Check original-paper DOI overlap before assuming study independence. Replication
external donors do not enter the within-project component or the meta-analysis.
Distinct original papers can still share citing documents and field shocks;
article-level resampling does not measure all such dependence.

Recompute the RPP contrast and bootstrap from the public annual panel, compare it
with the published study estimates, and fail on disagreement. Retain the original
neuroscience source as primary. Substitute its complete paired OpenAlex estimate
in a separate synthesis, never as an additional study. These substitutions assess
source sensitivity, not bias against a verified citation census.

Generate manuscript numbers, tables and README summaries from the exported
components. Record all input and code hashes in a synthesis receipt. The ordinary
paper build must run from public frozen data without a key or private API cache;
acquisition and full source-receipt validation remain separate reproducible steps.
