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
pre change between unsuccessful and successful papers, giving each paper equal
weight. Report group means, medians and annual paths, a Welch interval, and the
equivalent article/year fixed-effects specification with article-clustered
inference. Report the proportional ratio of group post/pre growth and an article-
level, group-stratified percentile bootstrap (9,999 draws, seed 20261007).

A separate external comparison uses original research articles from the same
journal and 2008 print-publication cohort. Exclude all RPP papers, corrections,
retractions and known replication-assessed originals from the other cohort
inventories. Record exclusions individually. Rank candidate controls using only
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

None at initial writing. Record subsequent changes with their evidence and timing.
