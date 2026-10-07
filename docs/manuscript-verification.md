# Manuscript and analysis verification

The manuscript studies four methodological audits. Failed-replication citation
research is separate. The working journal target is Quantitative Science Studies.

The neuroscience design compares papers within journal and publication year,
with article effects and separate annual paths for those groups. The original
Figure 1 is unchanged. Numbered stages in `scripts/nieuwenhuis_design/` generate
source comparisons, sample support, balance, weights, estimates and exhibits.

- The R suite passes 408 expectations, with no failures, warnings or skips.
  Repository Python formatting and lint checks and R linting pass.
- The two bibliography tests and metadata validation of all 14 cited entries pass.
- Explicit dummy-variable regressions and independently assembled clustered
  covariance matrices reproduce eight core model coefficients and standard errors
  within 1e-7. The permanent tests include these comparisons.
- Independent article-change calculations reproduce all ten equal-flagged-paper
  estimates and HC3 standard errors and all ten linear fixed-effects estimates.
- Planted heterogeneous effects verify that the equal-flagged and fixed-effects
  weights can produce different, correctly labeled estimates.
- Original classification labels, missing species information, supported and
  excluded papers, balance, estimation weights, leverage and variance contributions
  are preserved in public analytical outputs. The finer comparisons repeat the
  original adjustment on the same retained papers before adding study-type controls.
- The transitive numbered-stage receipts verify input, code and output hashes.
  These stages read public archived inputs and require no citation acquisition.
- The earlier independent paired-count calculation reproduces all four original
  meta-analysis standard errors. Those pooled estimates remain unchanged.
- The manuscript compiles to 25 pages. Rendered pages were checked for legibility,
  clipping, tables and figures. There are no unresolved citations/references or
  overfull content. The existing microtype footnote-patch warning remains.

Balance is not a randomization test. The design requires comparable absent-critique
citation changes within its comparison groups, on the stated scale. The main
journal/year target and the restricted study-type targets are distinct. HC3
intervals for the equal-flagged contrast are conditional approximations; small
cells do not permit separate fully nonparametric within-arm variance estimates.
Poisson information shares describe objective curvature, not robust variance or
an exact average of heterogeneous percentage effects.

The complete earlier replication checks include the source reconstruction,
figures, tables, meta-analysis and archived citation-source comparisons. An isolated
public-input checkout reproduced the synthesis and bibliography artifacts. Funding,
competing interests and author contributions remain for the authors to supply
before journal submission.
