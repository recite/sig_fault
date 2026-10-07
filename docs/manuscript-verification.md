# Verification of the focused manuscript

The manuscript uses four methodological audits and excludes replication outcomes.
The working journal target is Quantitative Science Studies.

- Rebuilt the underlying analyses, figures, tables, source comparisons and manuscript.
- Local formatting and lint checks passed; the R suite passed 359 expectations,
  with additional cohort checks and all Python suites passing.
- All 14 cited BibTeX entries passed DOI-specific metadata checks for ordered
  authors, title, journal, year, volume, issue, pagination and identifier.
- Independently recomputed all four synthesis specifications from component
  estimates and sampling variances using Python.
- An isolated checkout containing only public input/code files reproduced
  all 12 synthesis and bibliography validation artifacts byte for byte.
  It had no private-data directory.
- Compiled the final 21-page PDF, rendered and inspected every page. No unresolved
  citations/references or overfull content remain. The unchanged microtype
  footnote-patch warning does not affect these checks.
- Verified the transitive methodology, bibliography, HMX and RPP receipt chains.

The source identities and empirical assumptions remain those stated in the
manuscript. Bibliographic agreement and reproducible code do not establish
parallel counterfactual citation trends. Funding, competing interests and author
contributions remain for the authors to supply before journal submission.

## Precision and interpretation review

Reconstructed the four two-period coefficients and clustered standard errors
from article-level pre/post citation totals, independently of the fitted models.
All coefficients and standard errors agree within 1e-7. The new numbered
precision stage records group sizes, variance contributions, input hashes,
checks and outputs. Five tests cover scaling and comparison invariance, all-zero
pairs, invalid counts and incomplete or duplicated histories. All passed, along
with repository linting and the two bibliography tests. The 14-entry bibliography
validation passed again. The revised 21-page PDF compiled and every rendered
page was inspected; no unresolved references or overfull content remain.

The abstract and README now distinguish observed continued citation from the
uncertain causal interpretation of the comparative estimates. Numerical estimates
are unchanged. The precision calculation verifies the reported model-based
uncertainty; it does not validate the comparison assumptions.
