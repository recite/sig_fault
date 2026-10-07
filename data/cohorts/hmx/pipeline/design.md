# Citations around publication of the interaction-model audit

This plan was written after inspecting identities, source assessments, publication
metadata and overlap with other studies, but before collecting HMX citation
histories or estimating its citation contrasts. It is a retrospective plan.

## Population, assessment and publicity

Retain all 22 original papers in the published Hainmueller–Mummolo–Xu audit,
identified through its publisher-deposited references and verified author, print
year and journal metadata. The 46 assessed interactions remain distinct source
records. An original is flagged on a diagnostic if any assessed interaction is
flagged; absent a flag, an unavailable test makes its paper-level status unknown.
The primary severe-extrapolation diagnostic is complete: 14 flagged and eight
comparison papers. Six comparison papers receive other adverse diagnostics.
They are unflagged on severe extrapolation, not cleared of all concerns.

Use the authors' published Table A1 labels. A severe-extrapolation label identifies
a concern about the data supporting an interaction model; it does not establish
that the original substantive conclusion is false. Linearity rejection and failure
to reject equal low/high effects remain separately named diagnostics, with missing
tests retained. Nonrejection is not by itself evidence of error.

The event is the 18 December 2018 online journal publication, verified by publisher
metadata. The archived replication files were already public in July 2018, and an
SSRN draft was first posted in February 2016. The earliest draft's complete roster
and classifications have not been verified. The July version-one archive contains
the 22-paper roster and detailed analyses; it does not establish that every final
binary label was already public in that form. The estimand is the additional
publication-era citation response, not the effect of first disclosure.

## Estimation

Primary: 2017 versus 2019, omitting 2018. Outcome: distinct OpenAlex citing articles
and reviews, with checked reference links and duplicate DOI decisions. Acquire
histories through 2025 for trends and sensitivities. Missing histories stay missing;
zero requires completed acquisition. Fit article and year fixed-effects Poisson
pseudo-maximum likelihood with article-clustered covariance and t(G−1) intervals,
using the existing shared model with an explicit baseline-year parameter. Report
100*(exp(beta)−1), the severe-group post/pre citation ratio relative to that of the
comparison group. All-zero histories omitted from a Poisson fit remain in means,
medians and absolute-change comparisons.

Retain the full 22-paper contrast as the standalone result. For meta-analysis,
exclude Vernby (2013), which already contributes to the Lal audit. That prespecified
nonoverlap variant contains 13 severe and eight comparison papers. Do not add both
versions, alternative diagnostics, or databases as independent studies.

Report means, medians, absolute difference-in-changes, a paired article bootstrap
within assessment groups (9,999 draws; seed 20261007), and leave-one-paper-out
estimates. Journal-specific group counts are explicit. International Organization
contains three flagged papers and no comparison papers; a journal-adjusted
sensitivity must restrict to the 19 papers with within-journal support. Do not use
RPP-style journal standardization on the full cohort or pretend singleton cells
supply nonparametric within-cell variance.

## Sensitivities and scope

- 2019–2021 average follow-up, and all indexed citing document types.
- Pre-publication placebo: 2015 versus 2017. Earlier circulation means this is a
  pre-formal-publication trend check, not an unexposed placebo.
- Separate linearity and low/high diagnostic contrasts; no automatic composite
  of 20 flagged versus only two wholly unflagged papers.
- Journal/year fixed effects on the common-support subset, with its sample named.
- Retain Malesky's original with an indicator for the 2013 Anderson critique;
  excluding it is a sensitivity, not a first-disclosure sample correction.

The authors posted an updated appendix in December 2019 addressing subsequent
methodological criticism. The longer follow-up includes that publicity. Do not
reinterpret the original classifications as undisputed truth or silently replace
them with later diagnoses. A causal reading requires comparable untreated
proportional citation trajectories within the selected population.

## Reproduction

Numbered scripts in scripts/hmx use the shared immutable cache and receipt helper.
The source archive, publisher responses, reference crosswalk, assessment records,
source dates, exclusions and original-paper overlap remain inspectable. Acquire
citations only after the source and design stages complete. The eventual paper
build must reproduce estimation from public frozen panels without private caches.
