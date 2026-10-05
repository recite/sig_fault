# Validation

The offline registry was rebuilt in a temporary checkout containing public inputs and no private documents or API caches. All ten article, alias, event, claim-assessment, source-link, source-review, source-unit and independent-assessment outputs matched the working build byte for byte. All 62 archived ZIP files were checked against their recorded sizes and SHA-256 hashes. All 3,952 member records reference the correct parent archive hash, and the 454 extracted documents match their recorded sizes and hashes. The earlier check of all 1,355 document-retrieval records against cached bytes also passed.

The local checks cover:

- Complete catalog extraction beyond the visible website cards, pagination truncation, query-specific cache identity, and cached response checksums.
- Original and citing DOI aliases, preservation of completed downloads across interrupted acquisition, dated retraction records surviving CSV export/import, and repair of stale cached copies when a file is shared by several listings.
- Extensionless PDF extraction, unique exact-title searches, direct DOI verification for short titles, separate indexed and publisher dates, and preservation of publisher dates across control aliases.
- Verified source equivalences, conflicting eligibility/classifications, and evidence requirements for resolved adjudications.
- Independent assessment units, distinct reviewer teams, report/plan/reply roles, evidenced retrieval aliases, and misdirected catalog attachments. The assessment-completion gate uses enumerated assessments, not the source-listing resolution fraction.
- Provider/component traversal, pagination cycles, archive path safety, duplicate filenames, extensionless PDFs, metadata sidecars, extraction failures, and bounded streaming downloads. Tests cover partial-download cleanup and reuse of cached archives above the download-size limit.
- First-disclosure timing before age restrictions, eligible control pools, pre-outcome-only matching, missing versus observed-zero citations, deterministic ties, calipers and weights.
- Whole-stack missing-outcome exclusions; common +1/+h cohorts; exclusion of partial publication years from the earlier placebo.
- Exact agreement of the regression with direct matched differences under positive, zero and negative known effects, heterogeneous effects, one-control stacks, reused controls, and malformed panels.
- A reused-control clustered standard error independently derived from the two-way sandwich formula and reproduced numerically.

The current I4R suite passes 42 Python tests and 16 R expectations; `make lint i4r-test` passes. Before this acquisition and registry expansion, the full repository suite also passed (247 R expectations, including the I4R checks; 18 pilot and 6 Lal Python tests). Python formatting/import/lint checks and the repository R lint checks pass. The existing manuscript rebuilt successfully. The complete `make check` passed using `Rscript --vanilla` with `R_LIBS_USER` pointing to the project library. All 72 installed project-package versions were checked against `renv.lock`; the explicit library avoids the shared-cache autoloader.

Independent reviews examined source classifications, the design, metadata provenance, matching, the estimator and its variance calculation. Corrections included preserving both metadata providers, retaining the earliest disclosure clock, excluding incomplete risk sets, preserving dated retractions, and fixing the longer-horizon comparison cohort. These checks establish implementation behavior, not validity of an unobserved treatment effect. No complete I4R matched citation panel is currently available.
