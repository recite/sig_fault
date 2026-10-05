# Validation

The offline registry was rebuilt in a temporary checkout containing public inputs and no private documents or API caches. All seven article, alias, event, assessment, source-link, source-review and source-unit outputs matched the working build byte for byte. All 1,355 document-retrieval records were also checked against the actual cached bytes.

The local checks cover:

- Complete catalog extraction beyond the visible website cards, pagination truncation, query-specific cache identity, and cached response checksums.
- Original and citing DOI aliases, preservation of completed downloads across interrupted acquisition, dated retraction records surviving CSV export/import, and repair of stale cached copies when a file is shared by several listings.
- Extensionless PDF extraction, unique exact-title searches, direct DOI verification for short titles, separate indexed and publisher dates, and preservation of publisher dates across control aliases.
- Verified source equivalences, conflicting eligibility/classifications, and evidence requirements for resolved adjudications.
- First-disclosure timing before age restrictions, eligible control pools, pre-outcome-only matching, missing versus observed-zero citations, deterministic ties, calipers and weights.
- Whole-stack missing-outcome exclusions; common +1/+h cohorts; exclusion of partial publication years from the earlier placebo.
- Exact agreement of the regression with direct matched differences under positive, zero and negative known effects, heterogeneous effects, one-control stacks, reused controls, and malformed panels.
- A reused-control clustered standard error independently derived from the two-way sandwich formula and reproduced numerically.

The I4R suite passes 32 Python tests and 16 R expectations. The full repository suite also passed (247 R expectations, including the I4R checks; 18 pilot and 6 Lal Python tests). Python formatting/import/lint checks and the repository R lint checks pass. The existing manuscript rebuilt successfully. The complete `make check` passed using `Rscript --vanilla` with `R_LIBS_USER` pointing to the project library. All 72 installed project-package versions were checked against `renv.lock`; the explicit library avoids the shared-cache autoloader.

Independent reviews examined source classifications, the design, metadata provenance, matching, the estimator and its variance calculation. Corrections included preserving both metadata providers, retaining the earliest disclosure clock, excluding incomplete risk sets, preserving dated retractions, and fixing the longer-horizon comparison cohort. These checks establish implementation behavior, not validity of an unobserved treatment effect. No complete I4R matched citation panel is currently available.
