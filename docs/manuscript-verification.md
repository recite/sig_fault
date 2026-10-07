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
