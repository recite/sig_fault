# Construction and dictionary

The original 157-row classification remains unchanged. `scripts/nieuwenhuis.py` builds an identity crosswalk, retrieves citations separately, and constructs the paired database comparison. `make nieuwenhuis` first regenerates the historical cleaned data using the existing R pipeline. It then rebuilds the bridge from public, frozen identity and citation inputs without network access.

## Article identity

The workbook's `issue` and `link` columns have different meanings across journal sections. Date strings are not issue numbers. For 2010 Neuron entries, numeric issue cells are volumes and blank volume cells inherit the preceding volume within that section. For 2009 Neuron, the link cell gives volume–issue. Numeric link cells give issues for Science and the Journal of Neuroscience, but Nature DOI suffixes for Nature. A supplied publisher URL can identify volume, issue or DOI directly. These recodes are confined to identity lookup and leave the source fields and error classifications intact.

Publisher metadata must agree on journal, print year, available volume/issue and the supplied page lying inside the article's page range. Slash-separated source pages must all lie inside that range. A supplied DOI suffix must agree too. Queries generate candidates; their rank is not acceptance evidence. Journal indexes supplement searches that fail to return the correct article.

Several Science papers share an endpoint page with an adjacent article. Those cases need the source's study description, not automatic first-page preference. `identity_decisions.csv` documents each such decision and two erroneous page locators. The resolved DOI/title must exist in acquired publisher metadata. The independent pilot identities provide additional checks. Different classified rows cannot silently become the same DOI.

## Citation histories and paired sample

The OpenAlex acquisition verifies the target DOI and every incoming reference, complete pagination, stable result counts and unique work IDs. A completed history is bound to its target DOI; correcting an identity prevents reuse of a history for another target. API responses are cached with URLs, retrieval times and SHA-256 hashes. Acquisition reads the same rate-limit checkpoint as I4R.

The ten completed neuroscience pilot histories are reused from their frozen public records, with `origin=frozen_pilot` and the target DOI retained. The pilot's raw responses remain in its private cache and source manifest. `input_hashes.json` identifies the frozen pilot and historical inputs used in each bridge build. Its text-input hashes normalize CRLF to LF so Git checkout conventions do not change the fingerprint; downloaded source hashes remain byte-exact.

The historical bridge always contains the original 153 included source IDs. Source IDs 23 and 25 retain their historical unreliable-search exclusion; IDs 95 and 124 retain their missing-export exclusion. All four remain in the full OpenAlex acquisition roster. They cannot enter paired overlap denominators without a valid historical comparator.

Within a complete history, eligible missing year counts are zero. An incomplete or identity-mismatched history yields empty counts. Known false links and duplicate DOI records are removed from historical counts by the original pipeline. The primary OpenAlex count includes articles and reviews, excludes self-links and records dated before the target publication date, and deduplicates citing DOIs within each target. The broader sensitivity adds preprints, book chapters and proceedings. Different-DOI versions remain a limitation. Conflicting years or eligibility among same-DOI versions that could affect 2009–2015 block that paper's bridge pending adjudication; later conflicts remain recorded without changing this earlier window.

The DOI crosswalk uses the same complete historical-cohort papers on both sides. It retains all retrieved OpenAlex types and original-relative dates to distinguish absent links from links excluded by the counting rule. A relationship enters if either database dates it to 2009–2015. Missing DOIs are not matched on title automatically. Both source years are preserved even when one lies outside that window.

## Files and row units

| File | Row unit and key | Contents |
| --- | --- | --- |
| `identities.csv` | Classified original paper; `paper_id` | Original numeric ID and flag/cohort/journal, resolved DOI/title/volume/issue/pages, identity status, evidence and source URLs |
| `identity_candidates.csv` | Bibliographic search candidate | Candidate title, DOI and locators; candidate agreement is not a final decision |
| `identity_decisions.csv` | Manually resolved identity; `paper_id` | Accepted DOI/title, conflicting locator, substantive identity evidence and source |
| `citation_edges.csv` | Original–citing-work relationship; `paper_id,citing_work_id` | Target and citing OpenAlex IDs, citing DOI/title/date/year/type, verified-reference indicator, duplicate and eligibility flags, available text locations; fields follow the pilot schema |
| `coverage.csv` | Acquisition status per original; `paper_id` | Target DOI, API count, pages, completeness, origin and failure detail; absence is uncollected |
| `duplicate_checks.csv` | Repeated citing DOI per original; `paper_id,doi` | Record count, observed years/types, and whether the bridge needs adjudication |
| `paired_panel.csv` | Historical original–year; `article_id,year` | Source flag/cohort/journal, historical count, primary/broad OpenAlex counts, completeness status |
| `paired_summary.csv` | Year–flag–source | Number of paired papers, total citations, mean and median |
| `doi_overlap.csv` | Paired original–citing DOI; `paper_id,doi` | Both source years, OpenAlex type and target-relative date indicator, presence and year agreement |
| `status.json` | Current bridge | Complete-pair and group counts, full-cohort readiness, DOI overlap counts |
| `source_manifest.csv` | Cached source file; `path` | Source URL, retrieval timestamp, SHA-256 and byte count |
| `input_hashes.json` | Local input file | SHA-256 hashes after the documented line-ending normalization |

Raw PDFs and API responses remain private; public metadata and derived records support the offline build. Counts describe database records, not independently read full-text citations.

## Validation

An offline rebuild in a temporary directory, with no private caches and network calls disabled, reproduced the paired panel, annual summaries, DOI crosswalk, duplicate checks, status, input hashes and report byte for byte. Every cached Crossref source was checked against its recorded SHA-256.

Behavioral tests cover journal-specific locators, abbreviated and shared page ranges, DOI and print-year agreement, missing versus zero counts, identical overlap populations, histories bound to the verified target DOI, and conflicting duplicate dates or document types. Independent review identified the need to restrict both sides of the DOI overlap to the same completed historical cohort and to prevent reuse of histories after a target-identity change; both checks now have regression tests. These checks validate construction, not the completeness or accuracy of either citation database.
