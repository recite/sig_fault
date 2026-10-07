# Comparing citation sources in the Nieuwenhuis cohort

The measurement question is whether replacing the historical Web of Science exports with current OpenAlex records changes the measured citation trajectories and the flagged-versus-comparison contrast for the same papers and years. A disagreement is a source discrepancy, not an identified estimate of database bias: neither source is assumed to contain every valid citation. Database coverage, reference errors, document types, version aggregation and publication dates can all contribute.

## Population and identity

Retain all 157 assessments in the supplied Nieuwenhuis workbook. The historical main analysis contains 153 papers: two lack citation exports and two have demonstrably unreliable export histories. The primary source comparison holds those 153 identities fixed. The OpenAlex extension can include the four additional papers only in a separately labeled sample. Missing API histories remain missing, never zero. Publication-year restrictions do not alter the historical bridge sample.

Resolve original articles from the source journal, issue/volume, page (which can be an internal page), and supplied URL. A unique bibliographic match must agree on the available locators. Keep candidates and conflicting locators explicit. DOI identity is checked before collecting references. Source classification remains fixed; a metadata match does not re-adjudicate the original statistical assessment.

## Outcomes and contrasts

For each database, show annual means and medians for 2009–2015, the 2010 baseline and 2012–2015 post-period average, absolute differences in changes, and the existing article/year fixed-effects Poisson proportional contrast. Repeat the proportional contrast for the common one-full-year follow-up (2010 versus 2012). For pooling with newer audits, use the latter window and show the 2009 publication cohort separately: 2010 is only a partial exposure year for papers published during 2010. Do not impose I4R's two-full-pre-year age rule retrospectively on this cohort.

OpenAlex's primary count includes articles and reviews, matching the Lal extension. Historical exports lack a document-type field beyond Web of Science's broad publication type, so their original counts cannot be described as identically type-restricted. Report that asymmetry and preserve a broader OpenAlex sensitivity. DOI overlap and year disagreement among shared citation links separate some sources of discrepancy; non-DOI links remain unresolved rather than automatically false. Manual review can establish particular false or missing links, but absence from one database alone cannot.

Source differences in the growth contrast must be estimated on the same complete-paper sample. The completed mixed-source cohorts support a descriptive synthesis; source substitution must additionally pass the full paired-cohort gate. Bootstrap paired paper histories within flag groups to estimate uncertainty in the difference between database contrasts. Do not subtract independent standard errors for paired measurements. At protocol construction, the ten-paper pilot included flagged papers only and could not identify a flagged-versus-comparison effect. The completed collection now covers the entire historical cohort.

The implemented paired comparison uses 9,999 resamples, with seed 20261006 and percentile 95% intervals. Each draw samples original papers with replacement separately within flag groups and retains all source counts for each selected paper. Fewer than two paired papers in either group withholds intervals. A zero group-period total makes the proportional contrast undefined; the number of undefined draws is recorded, and any such draw withholds the proportional interval rather than conditioning it on successful draws. The absolute contrast remains defined at zero counts. Intervals are conditional on the available paired cohort and fixed database records; they do not quantify uncertainty from missing histories, citation-link errors or the choice of database.

For these balanced panels with a common exposure date and one common post-period coefficient, the article/year fixed-effects Poisson coefficient equals the log ratio of group post/pre mean citation ratios. To see this, write the fitted count as an article multiplier times a year multiplier times the flagged-post multiplier. The group-pre and group-post score equations match the corresponding observed totals; dividing post by pre within each group cancels article multipliers, and dividing those ratios across groups cancels the shared year multipliers. The number of post years also cancels. This closed form avoids fitting the same fixed-effects model thousands of times. Tests compare it to `fixest::fepois` for both windows, including zero-count observations and all-zero paper histories. This identity does not extend to the journal-by-year or cohort-by-year specifications. [Model documentation](https://lrberge.github.io/fixest/reference/feglm.html).

The stored source discrepancy is OpenAlex minus Web of Science, in citation units for the absolute contrast and log-ratio units for the proportional contrast. Transforming the latter as `100 * (exp(discrepancy) - 1)` gives the percentage change in the estimated growth ratio caused by changing the source; it is not a percentage-point difference between two percentage effects. Full-cohort readiness remains a separate acquisition gate even if both groups become estimable in a partial sample.

## Reproducibility and status

The protocol is retrospective: historical estimates and the Lal results are already known, and ten flagged-paper OpenAlex histories have been inspected in the separate context pilot. This document records the bridge design before acquiring the remaining histories. Public metadata, reference edges, acquisition status and source hashes remain distinct. Cached pilot histories may be reused with their original provenance; no new API result silently overwrites a frozen frame. Collection respects the shared OpenAlex rate-limit checkpoint.

A cross-audit synthesis will first display each study-specific contrast. Any pooled quantity must be labeled as an average association in the assembled cases, unless assumptions needed to identify the effect of publicity are separately justified. Lal's diagnostic flags and formal-publication date are not equivalent to verified material errors and their first public disclosure. Report those differences alongside the estimates rather than making perfect population enumeration a prerequisite for every descriptive result.

## Full-cohort OpenCitations comparison

Recorded October 6, 2026 before collecting OpenCitations histories beyond the ten-paper flagged pilot. Historical results, OpenAlex pilot results and the ten-paper third-index link check have already been examined. This is a retrospective measurement check, not a new independent audit of statistical errors.

Keep the 153 historical main-analysis papers, their original error classifications, the 2010 baseline and both post windows (2012 and 2012–2015). Collect the complete OpenCitations incoming-link response and verify its length against the count endpoint. Preserve raw relationships and provenance. Count distinct citing works with a recorded publication year, retaining undated works separately. Merge citation records sharing a citing OMID or DOI; conflicting years within a merged work make its year unresolved rather than selecting the convenient date. Empty or incomplete acquisition is not a zero history. API completeness does not establish that the index captures all real citations.

The outcome is dated citing works recorded by this index, across document types. It is not the primary OpenAlex article/review outcome. Report annual means and medians, absolute differences in changes, and ratios of group post/pre means. Compare each contrast with Web of Science on exactly the same available papers. Use the existing paired, flag-stratified paper bootstrap (9,999 draws, seed 20261006) for the source difference. Also report the subset of histories with no undated works, keeping the two sources on that identical subset. Do not generalize this selected subset as a full-cohort result. Missing years cannot be imputed from citation counts or classified as outside the analysis window. Unresolved records and full-cohort coverage must be visible alongside the dated-work analysis.

A source discrepancy combines coverage, dating, document-type and vintage differences. Neither index is ground truth; shared upstream sources also prevent treating index agreement as independent validation. This measurement check does not add another independent study to the meta-analysis and does not replace the original historical estimate or the pending OpenAlex bridge.

After inspecting the completed OpenCitations source contrasts, we also repeat the
existing equal-audit, one-full-year synthesis with its neuroscience component
measured using OpenCitations. This is a retrospective source sensitivity. It keeps
the same original papers, audit weights, IV alternatives and article-clustered
component inference; it substitutes the source rather than adding another audit.
The main historical synthesis and the separate OpenAlex acquisition remain intact.

## Duplicate-record adjudication

Full collection identified same-DOI records with conflicting dates. The
[resolution ledger](../../data/nieuwenhuis/duplicate_resolutions.csv) records
OpenAlex's DOI-resolved work ID, the exact retrieved candidate IDs, and hashes
of the OpenAlex and Crossref identity evidence. Retain that canonical OpenAlex
record once per target. This does not replace its year with Crossref's year or
establish its first-publication date; the preprint case includes different
version titles and dates under one DOI. Raw edges remain unchanged. The build
rejects a stale resolution if the candidate IDs, canonical date, type, or verified
reference no longer match, and unresolved relevant conflicts still block a paper.

The source-specific Poisson fits must reproduce the group growth-ratio identity.
The synthesis requires complete coverage of the historical cohort and verifies
the paired sample size on every substituted model; an estimable partial sample
is not enough. OpenAlex replaces the neuroscience component rather than adding
another independent audit.
