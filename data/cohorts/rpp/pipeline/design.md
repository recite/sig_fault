# Citation response to the psychology replication project

This is a retrospective observational analysis. The source replication judgments,
paper identities and other audit results were inspected before writing this plan.
No RPP citation histories or RPP treatment-effect estimates have been examined at
this point. The plan is versioned, not preregistered.

## Population, event and outcomes

The unit is the original paper: 100 completed replications concern 98 papers.
The primary classification is the source's Replicate.R judgment, normalized only
for case. Both repeated-paper pairs report unsuccessful replication, giving 59
unsuccessful and 39 successful original papers. Any future mixed judgments remain
a separate category rather than silently becoming failures.

The immediate estimand is the change in annual citations following the project's
2015 public announcement for unsuccessful versus successful replications. This
is an adverse-versus-favorable disclosure contrast. It is not automatically the
effect of first revealing an error. The disclosure stage preserves dated primary
evidence and earlier report candidates; project creation, file upload and present
public availability alone do not establish historical public disclosure.

The event year 2015 is excluded from the main contrast. The primary pre-period is
2012–2014 and post-period 2016–2018; 2010–2014 and 2016–2025 annual trajectories
provide diagnostics and longer follow-up. The primary outcome counts distinct
OpenAlex citing articles/reviews, with verified reference links, by publication
year through 2025-12-31. All document types are a sensitivity. Incomplete histories
are missing; zero requires completed acquisition. Direct citations by the 2015
summary article are separately identified. Counts measure citation, not whether
the citing author accepted or qualified the original finding.

## Comparisons and estimation

The within-project primary estimate compares each paper's mean annual post-minus-
pre change between unsuccessful and successful papers within journal, then averages
the three journal contrasts using fixed shares of the 98-paper cohort (28/98,
30/98, 40/98). Papers receive equal weight within journal and replication group.
Report raw group means, medians and annual paths alongside standardized paths.
Use a Welch–Satterthwaite interval for the weighted difference. Report article/year
and journal×year fixed-effects specifications with article-clustered inference as
sensitivities. For proportional growth, average the three journal-specific log
post/pre growth ratios using the same fixed weights and transform with exp(beta)-1.
Use a journal-by-replication-group stratified article bootstrap (9,999 draws, seed
20261007); report any undefined ratio draws and do not silently discard them.

A separate external comparison uses original research articles from the same
journal and 2008 print-publication cohort. Exclude all RPP papers, corrections,
retractions and known replication-assessed originals from the other cohort
inventories. This deliberately excludes known assessed papers even if their
assessment came after our follow-up; it is a fixed conservative donor rule, not
a claim that later assessments contaminated earlier citations. Record exclusions individually. Rank candidate controls using only
2010–2014 annual log(1 + citations) trajectories, within journal, with deterministic
DOI tie-breaking; select three per target with replacement. Use the same controls
for all follow-up periods. Retain the full eligible donor pool for a nonnegative,
sum-to-one synthetic-control sensitivity. No post-2014 outcome enters matching.

External matched estimates concern each replication group versus unassessed
papers, helping distinguish unsuccessful-replication penalties from successful-
replication publicity benefits. Shared controls induce dependence: retain original
paper identities and use two-way clustering by matched target and original article
in a stacked article/year regression. Inference conditions on selected matches;
synthetic-control results are sensitivity estimates, with pre-fit reported, not
randomization p values. A thin or poorly fitting donor pool is reported, not
silently broadened across journals or publication years.

## Interpretation and checks

The comparisons require comparable untreated citation trajectories. Check annual
pre-trends, a placebo change comparing 2010–2011 with 2012–2014, pre-period levels,
matching balance, leave-one-paper-out influence and coverage by replication group.
Earlier disclosure changes the interpretation to additional publicity in 2015.
If precise first-disclosure dates cannot be verified, retain that limitation in
the estimand rather than assigning guessed dates. Journal-specific contrasts and
longer horizons are sensitivities, not separate independent studies.

The expected direction is a relative citation decline for unsuccessful replications;
no numerical prior is imposed. Flat relative paths with narrow intervals would
count against a large citation penalty. Nonreplication does not by itself prove an
original statistical error, so this cohort stays outside the statistical-error
meta-analysis until a separately defined replication synthesis exists.

## Execution evidence

Numbered scripts in `scripts/rpp/` write receipts under `pipeline/receipts/`.
Receipts contain commands, code/input/output hashes, source URLs and retrieval
timestamps, actual checks, sample counts and unresolved cases. Cached source
responses are preserved under `private-data/cohorts/rpp/pipeline/`. A changed input
or incomplete upstream stage invalidates downstream execution. Human identity or
timing decisions require an explicit, sourced ledger; scripts never infer them
from a desired final sample size.

## Deviations

2026-10-07, before citation acquisition: independent design review identified
different journal composition by replication outcome (successful/unsuccessful:
JEPLMC 15/13, JPSP 8/23, PS 16/23). Changed the primary contrast from the raw
pooled difference to fixed-share journal standardization and changed bootstrap
strata accordingly. The raw contrast remains descriptive. Clarified that excluding
future-assessed external donors is an eligibility choice, not historical exposure.

2026-10-07, before citation acquisition: source review found Row.82 has a
JPSP locator belonging to another article. Its OSF project and publisher identify
The Face of Success in Psychological Science. The sourced identity ledger corrects
the locator, changing journal counts to JEPLMC 28, JPSP 30, PS 40; the rule still
uses verified journal shares.

Implementation before estimation: matching distances standardize each pre-year
log(1 + citations) by its donor-pool standard deviation within journal. Synthetic
weights minimize mean squared error on these features plus a fixed 1e-6 squared-
weight penalty, subject to nonnegativity and sum one. Current OpenAlex retraction
flags and nonarticle types exclude donors, with the exclusions recorded.

After the first within-project estimates, but before reviewing external estimates:
independent donor-content review identified six comments/reviews/editorial records
that article-type metadata had admitted. Exclude them using primary-source evidence
in control_decisions.json and verify PubMed publication types; retain original
methodological analyses. This implements the stated original-research criterion.

After examining the initial external estimates: independent review found that
fitting synthetic weights to log counts while predicting arithmetic weighted counts
creates a scale mismatch. The final synthetic sensitivity fits raw counts,
standardized by donor-year standard deviations, on 2010–2014 only. The ridge
penalty and simplex constraints are unchanged. Pre-fit RMSE is reported in raw
citation units; this correction does not affect nearest-neighbor or within-project
estimates. The final public table contains the corrected specification.
