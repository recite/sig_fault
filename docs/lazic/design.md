# Citation response to the Lazic audit

Prepared before collecting this cohort's citation histories. We have examined
paper identities, audit classifications, publication dates and reporting/design
covariates, but no citation outcomes for this cohort. This is a retrospective,
self-documented analysis plan, not a registered experiment.

## Question and sample

Did citations to papers classified as pseudoreplication grow less after the audit
became public than citations to papers the same audit classified as correctly
analyzed? The target is the average change attributable to publicizing the problem
among the flagged papers. The observed contrast is the difference in equal-paper
mean annual citation changes between flagged and comparison papers with no identified prior public warning
about the same statistical issue. The original assessed cohort has 91 flagged
and 45 comparison papers; the primary cohort currently has 90 and 45.

The source sampled 200 eligible studies from a PubMed search of 500 abstracts,
screening and replenishing the sample until 200 eligible papers were included.
Eligibility concerned English-language prenatal-exposure experiments in multiparous
mammals that examined offspring. The population is this sampled literature, not
all animal research. Retain all 64 unclear assessments in the inventory and in
descriptive coverage reports; do not assign them to either comparison group.

Use 2016 as the full baseline and 2019 as the primary post year, after both the
2017 dataset release and 2018 journal publication. All 136 classified papers
were published by 2015. The main absolute contrast is
`mean(citations_2019 - citations_2016 | flagged) -
mean(citations_2019 - citations_2016 | correct_analysis)`.
Report mean levels, medians, the distribution of changes, and trajectories through
2025. No partial 2026 outcome. Years 2017–2018 describe the transition but are
excluded from the primary contrast. Also report the 2019–2021 average as a
longer-window sensitivity, keeping the same papers.

The dataset's release date establishes public availability, not readership.
The official bioRxiv API verifies September 2, 2017 as the first preprint date.
Verify the deposited file-version history before finalizing timing. PubMed lists prior errata for five papers (two flagged, one correct, two
unclear). Review those notices and retain separate dates and types. The primary sample excludes PMID 23449593: a public Science comment dated
May 17, 2013 already raised the incorrect treatment of pregnant-female and cage-level
assignment. The authors disputed that criticism in a same-day reply. This is first
*known* publicity; a notice search cannot prove no earlier unlinked criticism exists.
The [prior-warning ledger](../../data/lazic/prior_warnings.csv) supplies the evidence.
Keep the original classifications and all 136 papers in a repeated-publicity
sensitivity. Also report a sensitivity excluding all papers with
pre-audit erratum links, with a further evidence-based exclusion if a notice already
publicized the assessed statistical problem. Do not relabel a name correction as
a substantive statistical error.

## Identification and diagnostics

A causal interpretation needs comparable citation changes absent publicity and
no differential concurrent shocks. Flagged status was not randomly assigned.
Field, topic, journal, paper age and design quality could produce different growth
even without the audit. Correctly analyzed papers may themselves benefit from the
public assessment, so the contrast need not isolate the effect against no publicity.

In the full classified cohort, design complexity differs: 37/91 flagged and 7/45 comparison papers used split-unit
designs. Report a split-unit-stratified difference in changes, averaging stratum
contrasts using the flagged papers' stratum shares. Use article-level resampling
within classification and stratum for its interval, preserving these target shares.
This addresses one observable imbalance; it does not establish identification.

Plot a fixed-cohort pretrend for papers published by 2013 (51 flagged, 26 correct before the prior-warning exclusion;
50 flagged and 26 correct afterward),
using 2014–2016, and estimate the main contrast within that same restricted cohort.
Never treat prepublication years as observed citation zeros. Report the size and
uncertainty of pretrend differences, not a pass/fail significance test. Differing
pretrends weaken causal interpretation even if an estimate is imprecise.

## Outcomes, uncertainty and synthesis

Collect link-level citation histories for all 200 identities and document database
coverage by classification. Only completed, validated histories may supply zero
counts. Missing histories remain missing; missing citing-paper dates are reported
and excluded from year assignment. Retain both papers without DOI through their
PMID identities. Use all indexed citing-document types for the OpenCitations
analysis and label it accordingly; article/review-only analyses require verified
type metadata and remain a separate outcome.

Count distinct citing publications per target, not duplicated citation edges.
Collapse records sharing the same normalized DOI; preserve the identity-resolution
ledger for remaining records. Review version pairs and book/chapter records for
repeated copies of one reference list, using bibliographic metadata and source
references before merging. Do not automatically merge distinct chapters or papers
by title similarity. Report unresolved duplicate candidates and the contrast with
and without them; never choose a resolution based on the resulting effect estimate.

For the absolute difference in article-level changes, use a Welch interval with
Satterthwaite degrees of freedom. A separate proportional comparison uses Poisson
pseudo-maximum likelihood with article and year fixed effects, article-clustered
uncertainty, and reports any all-zero papers removed by the estimator. Whole-paper
bootstrap intervals (5,000 resamples within classification, seed 2017) assess
sensitivity to skew. None of these intervals captures uncertainty across public
audits: these 136 papers were exposed to one common event.

Hypothesis: publicity reduces subsequent use of flagged papers relative to the
comparison group. No numerical effect magnitude is justified in advance. Report
effect sizes and intervals without treating nonsignificance as evidence of no
effect or continued citations as proof that readers ignored the error. Citations
may concern unaffected results or criticize the paper; aggregate links cannot
measure unqualified reliance.

For the existing synthesis of the year before versus the year after a warning,
also estimate 2016 versus 2018. That is the year after the first public release,
but the year of journal publication; it is a harmonized secondary contrast, not
a replacement for the primary 2019 follow-up. Report the horizon difference.

This is one audit-level contribution to synthesis, labeled source-assessed
pseudoreplication. Do not count its individual papers as independent publicization
events, pool the unclear group into controls, or equate these assessments with
independently verified material numerical corrections. Additional models and timing
changes must be labeled and explained rather than selected by their results.

## Eligibility amendment before estimation

The initial plan retained all 136 classified papers. Primary-notice review identified
a 2013 warning about the same problem in PMID 23449593. Before estimating citation
effects, the primary sample was restricted to papers without an identified prior
warning, preserving the original full-cohort contrast as a sensitivity. Citation
collection had begun, but no treatment-effect estimates had been examined.
