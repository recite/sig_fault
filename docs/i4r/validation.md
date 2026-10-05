# Validation

The offline registry was rebuilt in a temporary checkout containing public inputs and no private documents or API caches. Article, event, assessment, source-link and source-review outputs matched the working build byte for byte.

The local checks cover:

- Complete catalog extraction beyond the visible website cards, pagination truncation, query-specific cache identity, and cached response checksums.
- Original and citing DOI aliases, preservation of completed downloads across interrupted acquisition, and dated retraction records surviving CSV export/import.
- First-disclosure timing before age restrictions, eligible control pools, pre-outcome-only matching, missing versus observed-zero citations, deterministic ties, calipers and weights.
- Whole-stack missing-outcome exclusions; common +1/+h cohorts; exclusion of partial publication years from the earlier placebo.
- Exact agreement of the regression with direct matched differences under positive, zero and negative known effects, heterogeneous effects, one-control stacks, reused controls, and malformed panels.
- A reused-control clustered standard error independently derived from the two-way sandwich formula and reproduced numerically.

The I4R suite passes 21 Python tests and 16 R expectations. The full repository suite also passed (247 R expectations, including the I4R checks; 18 pilot and 6 Lal Python tests). Python formatting/import/lint checks and the repository R lint checks pass. The existing manuscript rebuilt successfully. Initial R checks used `Rscript --vanilla` while the execution sandbox blocked the shared renv-cache lock. The complete `make check` was then run in the normal locked renv environment with access to that cache.

Independent reviews examined source classifications, the design, metadata provenance, matching, the estimator and its variance calculation. Corrections included preserving both metadata providers, retaining the earliest disclosure clock, excluding incomplete risk sets, preserving dated retractions, and fixing the longer-horizon comparison cohort. These checks establish implementation behavior, not validity of an unobserved treatment effect. No complete I4R matched citation panel is currently available.
