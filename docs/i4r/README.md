# Does publicizing a significant error change citations?

This extension builds an article-level record of consequential errors documented in the Institute for Replication (I4R) collection. The question is how citations change **after the error becomes public**, relative to comparable articles without a public assessment in the observation window.

The [coverage report](coverage.md) gives the current counts and unresolved stages. The inventory includes all 331 discussion papers and 383 report listings found in the frozen catalogs. These are overlapping source records, not 714 distinct original articles. Every listing now has a second review disposition. Confirmed duplicate versions are linked, and shared projects containing several assessments remain explicit coverage gaps. **The 90% assessment-resolution target has not been met. No I4R treatment-effect estimate is available.**

See [validation](validation.md) for the local checks and independent review.

Use the [searchable evidence catalog](catalog.html) to inspect sources, passages, classifications, and review depth. The [design](design.md), [dictionary](codebook.md), and [join and recode contract](data-construction.md) explain how those records become an analysis sample.

## What qualifies

The primary cohort requires a demonstrated coding, data, or statistical error that materially changes a substantive finding. A failed replication or sensitivity to an alternative specification is recorded separately. Verification here means checking source evidence and replies; it does not mean rerunning every original analysis.

The exposure date is the earliest substantiated public disclosure containing the relevant criticism. An OSF creation date, a PDF's date, or a later I4R publication does not establish that date. For several cases, the public critique predates its I4R appearance by years. Moving the clock to the later report would manufacture an untreated baseline.

The design compares citation changes from the full year before disclosure to the full year afterward, omitting the disclosure year. Up to three controls come from the same journal and article type, published within one year of the affected paper, with similar topics and prior citation histories. Each affected article receives equal weight. Means, medians, absolute differences and uncertainty will be reported, with longer horizons and specification checks in the appendix. Matching cannot by itself establish that publicity caused a change.

## Rebuild without network access

Install R dependencies with the repository's `make restore`. Install the Python extension dependencies, then run:

```sh
python3 -m pip install -r requirements-i4r.txt
make i4r
make i4r-test
```

The offline build uses committed source inventories, reviewed evidence, verified bibliographic metadata, and any completed citation tables. `source_adjudications.csv` records the catalog review decisions; `claim_adjudications.json` preserves claim-specific consequences, disputes and dating evidence; `curated_claims.csv` supplies the verified and unresolved claims to the registry. `assessment_inventory.json` enumerates independent reviewer-team assessments in the reconciled bundles; its generated tables link each unit to its original article, reports, plans and replies. These units are distinct from claim-level error records. It regenerates registry tables, matching decisions, analysis outputs, and the coverage report. Private PDFs and API caches are not needed. Empty analysis output is an explicit incomplete-data status, not a zero effect.

## Resume acquisition

Source collection, identity resolution, control selection and analysis are separate stages:

```sh
make i4r-sources
python3 scripts/i4r_registry.py crossref --search-titles
python3 scripts/i4r_registry.py resolve
python3 scripts/i4r_citations.py candidates
python3 scripts/i4r_citations.py control-metadata
python3 scripts/i4r_citations.py retractions
python3 scripts/i4r_citations.py fetch
python3 scripts/i4r_sources.py manifest
make i4r
```

`make i4r-sources` resumes the frozen inventory. To deliberately refresh the catalog, first run `python3 scripts/i4r_sources.py discover`; changing the study cutoff requires an explicit design update. Document extraction also requires Poppler's `pdftotext`.

OSF acquisition has resumed after an earlier quota limit. Anonymous OpenAlex access remains rate-limited. Optional `OSF_TOKEN` (or `OSF_API_TOKEN`) and `OPENALEX_API_KEY` environment variables enable authenticated access. Tokens are sent in headers and are not written into public data or logs. See the official [OSF API](https://developer.osf.io/) and [OpenAlex authentication](https://help.openalex.org/api/authentication/) documentation. The collector respects rate-limit checkpoints; successful responses are cached with source URLs and hashes.

Full-text PDFs and raw responses remain in ignored `private-data/i4r/`. Public files contain bibliographic facts, source pointers, derived measurements and review notes. Publisher PDFs are not redistributed. The economics/political-science aggregate replication package anonymizes original-paper identities, so it cannot provide an identity-to-error crosswalk. Its published appendix and the psychology report roster supply identities, with individual findings still requiring review.

## Remaining work

Resolve missing/full-text-limited assessments and establish the eligible-assessment denominator. Provider and child-component queries have been checked for every OSF-linked catalog entry. Two projects are unauthorized, and non-OSF attachments remain a separate gap. The archive collector inventories ZIP contents and extracts bounded-size PDFs and text documents without executing their code. All 62 root ZIP archives have been acquired and inventoried. The acquisition target permits downloads up to 3,000 MiB and streams them to disk; already cached archives remain reusable under smaller download limits. Nested ZIP files and oversized members remain visible gaps. An extracted figure or original paper is not an assessment. Keep these cases unresolved until their evidence is examined.

Verify additional original-paper identities and earliest disclosure dates; retrieve complete journal risk sets and incoming citation edges; then inspect support, pretrends, timing and uncertainty. Automated title search requires exact normalized agreement, a unique DOI and at least four title words; ambiguous results remain in the queue. Short titles can still be verified against an independently supplied DOI. The control metadata step checks publisher dates separately from the indexed years used to collect comparable articles. Retraction Watch supplies dated retraction screens but cannot establish that all other public criticisms have been found.

This extends existing citation-response research, including Ankel-Peters, Fiala and Neubauer's [*Is Economics Self-Correcting? Replications in the American Economic Review*](https://ideas.repec.org/p/zbw/i4rdps/68.html). The contribution sought is a documented, broader set of significant non-retraction errors and their disclosure histories. Retractions are studied separately in [propagation_of_error](https://github.com/recite/propagation_of_error).
