# Construction and dictionary

The original 157-row classification remains unchanged. `scripts/nieuwenhuis.py` builds an identity crosswalk, retrieves citations separately, and constructs the paired database comparison. `make nieuwenhuis` first regenerates the historical cleaned data using the existing R pipeline. It then rebuilds the bridge from public, frozen identity and citation inputs without network access.

## Article identity

The workbook's `issue` and `link` columns have different meanings across journal sections. Date strings are not issue numbers. For 2010 Neuron entries, numeric issue cells are volumes and blank volume cells inherit the preceding volume within that section. For 2009 Neuron, the link cell gives volume–issue. Numeric link cells give issues for Science and the Journal of Neuroscience, but Nature DOI suffixes for Nature. A supplied publisher URL can identify volume, issue or DOI directly. These recodes are confined to identity lookup and leave the source fields and error classifications intact.

Publisher metadata must agree on journal, print year, available volume/issue and the supplied page lying inside the article's page range. Slash-separated source pages must all lie inside that range. A supplied DOI suffix must agree too. Queries generate candidates; their rank is not acceptance evidence. Journal indexes supplement searches that fail to return the correct article.

Several Science papers share an endpoint page with an adjacent article. Those cases need the source's study description, not automatic first-page preference. `identity_decisions.csv` documents each such decision and two erroneous page locators. The resolved DOI/title must exist in acquired publisher metadata. The independent pilot identities provide additional checks. Different classified rows cannot silently become the same DOI.

## Citation histories and paired sample

The OpenAlex acquisition verifies the target DOI and every incoming reference, complete pagination, stable result counts and unique work IDs. A completed history is bound to its target DOI; correcting an identity prevents reuse of a history for another target. API responses are cached with URLs, retrieval times and SHA-256 hashes. Acquisition reads the same rate-limit checkpoint as I4R.

Here, a complete history means retrieval of every record returned by the recorded API query, not independent proof that the database contains every real citation. An incomplete download or uncollected paper is an acquisition gap, not evidence of missing citations in OpenAlex. Database coverage can be compared only on completed, matched source histories, with document types and dating differences retained explicitly.

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
| `period_summary.csv` | Cohort–window–source–flag | Paired-paper count; mean and median baseline, annual post-period average and within-paper change |
| `source_contrasts.csv` | Cohort–window–OpenAlex definition–estimand | Same-paper source contrasts, OpenAlex-minus-Web-of-Science discrepancy, paired bootstrap SE and percentile interval, sample sizes, draw counts, seed and explicit availability status; empty estimates are unavailable, not zero |
| `doi_overlap.csv` | Paired original–citing DOI; `paper_id,doi` | Both source years, OpenAlex type and target-relative date indicator, presence and year agreement |
| `status.json` | Current bridge | Complete-pair and group counts, full-cohort readiness, DOI overlap counts |
| `source_manifest.csv` | Cached source file; `path` | Source URL, retrieval timestamp, SHA-256 and byte count |
| `input_hashes.json` | Local input file | SHA-256 hashes after the documented line-ending normalization |
| `validation_edges.csv` | Original–OpenCitations citation identifier | All retrieved citation relationships, citing/cited identifier aliases and available publication dates |
| `validation_coverage.csv` | Paired original paper | Target DOI, response/count-endpoint agreement, undated records and acquisition status |
| `validation_sources.csv` | Cached OpenCitations response | Exact URL, retrieval time, SHA-256 and bytes |
| `link_validation.csv` | Original–reconciled citing DOI | Existing source-overlap frame joined to third-source links; present, not found or not collected, matching citation IDs and dates |
| `validation_summary.csv` | Original-source presence–validation status | Link counts within the selected paired-paper frame |

Raw PDFs and API responses remain private; public metadata and derived records support the offline build. Counts describe database records, not independently read full-text citations.

## Completing and validating the citation data

First complete the OpenAlex histories for the fixed historical cohort, including comparison papers. A free account key raises the anonymous daily allowance tenfold; the collector already accepts `OPENALEX_API_KEY`, caches responses and respects retry times. Record-level citation retrieval is necessary for 2010–2015; recent annual totals cannot replace those histories. [OpenAlex authentication](https://help.openalex.org/api/authentication/).

Then compare both databases on identical papers and windows. Examine link discrepancies separately by flag group and before/after the warning, retaining document types, duplicate/version decisions and online/print dates. A source that yields more citations is not automatically more accurate, and more citations in both groups need not change their relative growth. The paired source-contrast estimator tests the latter directly.

The historical Web of Science exports supply the first independent source frame. If institutional access permits, obtain current citing-record exports or the Expanded API's citing items, which would also separate some historical-vintage differences from present database differences. Semantic Scholar and OpenCitations offer additional citation-link APIs for validation samples. Their disagreements should be checked against bibliographies; agreement between databases is not independent proof because providers can share upstream records. [Web of Science APIs](https://webofscience.zendesk.com/hc/en-us/articles/48141490389905-APIs), [Semantic Scholar API](https://webflow.semanticscholar.org/product/api), [OpenCitations Index API](https://api.opencitations.net/index/v2).

Review a prespecified sample of links found in both sources and in only one, stratified by flag group and period. Preserve sampling probabilities and retrieval failures so the review can distinguish false links, missed links, date conventions and unresolved cases. Link validation and citation-context coding answer different questions: the former checks whether a paper cites the original; the latter checks whether it acknowledges the problem or relies on the affected claim. Keep source-specific estimates primary and any deduplicated union a labeled sensitivity, rather than silently treating all extra records as valid citations.

## Validation

An offline rebuild in a temporary directory, with no private caches and network calls disabled, reproduced the paired panel, annual summaries, DOI crosswalk, duplicate checks, status, input hashes and report byte for byte. Every cached Crossref source was checked against its recorded SHA-256.

Behavioral tests cover journal-specific locators, abbreviated and shared page ranges, DOI and print-year agreement, missing versus zero counts, identical overlap populations, histories bound to the verified target DOI, and conflicting duplicate dates or document types. Independent review identified the need to restrict both sides of the DOI overlap to the same completed historical cohort and to prevent reuse of histories after a target-identity change; both checks now have regression tests. These checks validate construction, not the completeness or accuracy of either citation database.

The paired source-contrast module adds 32 R assertions covering exact agreement, known source discrepancies, proportional invariance to common scaling, agreement with article/year fixed-effects Poisson and OLS estimates, incomplete years, missing groups and undefined proportional resamples. The period summaries and source-contrast table reproduce byte for byte in a temporary directory containing only the frozen paired panel and the two analysis scripts. Independent review found no material implementation defect and separately checked the closed form against numerical Poisson fits. The current ten flagged histories produce explicit unavailable contrasts; they do not generate an estimated database effect.

The [OpenCitations link check](validation.md) uses the same paired-paper frame. It tests whether a third index records each citing DOI for the same target, independently of agreement on publication year. The API list and count endpoints must agree, citation identifiers must be unique and every relationship must identify the queried original DOI. Behavioral tests cover identity mismatch, truncation, duplicates, identifier aliases, unknown dates and uncollected versus absent links. Cross-index agreement corroborates records but is not independent bibliographic verification. Raw responses and source hashes remain available for reconstruction.

All four third-source outputs reproduce byte for byte in a temporary directory containing public inputs only, with network calls disabled. Independent review reproduced the link counts and checked raw-response hashes. The complete repository check passes 292 R expectations and 104 Python tests, and the revised manuscript compiles; the changed appendix pages were rendered and inspected. The twenty raw responses and their provenance sidecars are preserved in the durable checkout.

## Diagnosing source discrepancies

`make nieuwenhuis` also rebuilds `count_decomposition.csv` and its group/year summary. The contributions must sum exactly to the observed OpenAlex-minus-Web-of-Science count difference for every paired paper-year; a mismatch stops the build. Contributions separate publication-year shifts on shared eligible DOIs, shared links excluded by document type or original-relative date, unmatched DOI-bearing records, and unresolved records lacking DOIs. The order assigns ineligible shared records to exclusions before attributing year shifts.

`link_review.csv` records evidence for unmatched historical identifiers. Verified DOI transcription errors are reconciled in `reconciled_overlap.csv`, which retains the original historical DOI. Translations and book components remain separate records. The original exact-DOI crosswalk and historical counts remain available.

`date_metadata.csv` records publisher-deposited online, print and general publication dates from Crossref for shared citing DOIs with conflicting years. `date_disagreements.csv` joins those dates to each original–citing-paper relationship. A date-convention explanation requires agreement on both years; one missing date does not suffice. These are selected diagnostic records, not a representative validation sample. Fetch with `python3 scripts/nieuwenhuis_diagnostics.py fetch-dates`, then rebuild with `make nieuwenhuis`. The source manifest includes cached date responses and their hashes.

The decomposition and DOI reconciliation received an independent review. Every paired paper-year reconstructed exactly, only evidenced transcription errors merged, and translations and book components remained distinct. All seven diagnostic data/report/macro outputs also reproduced byte for byte in a temporary offline directory without private caches. The full source manifest was checked against the downloaded bytes.

## Full-cohort OpenCitations measurement

`make nieuwenhuis-opencitations` reconstructs the fixed 153-paper historical panel
using the completed OpenCitations responses. `creation` is the citing work's
publication date under the provider's definition. The documented CSV format is a
fallback for interrupted JSON responses, with the same identity and count checks.
Raw list/count responses have URL, retrieval time, byte size and SHA-256 provenance.
Collection respects its own host-level retry checkpoint and sends neither OpenAlex
nor OSF credentials to OpenCitations.

| Output | Row unit | Definition |
| --- | --- | --- |
| `opencitations_works.csv` | Target paper × merged citing work | Transitive OMID/DOI identity components; all identifiers and original OCIs retained. A unique supplied year is dated; absent or conflicting years remain unresolved. |
| `opencitations_panel.csv` | Historical paper × calendar year | Fixed historical frame with original WoS count and dated-work OpenCitations count; incomplete acquisition is missing, never zero. Unresolved-year relationships are recorded separately. |
| `opencitations_status.json` | Acquisition summary | Complete histories by original flag, raw relationships, merged records and unresolved dates; full-cohort availability is separate from estimator feasibility. |
| `opencitations_contrasts.csv` | Sample × publication cohort × post window × estimand | Same-paper source estimates, their paired difference and a flag-stratified 9,999-draw bootstrap interval. `wos` is the historical estimate and `alternative` is the named replacement source. |
| `opencitations_period_summary.csv` | Sample × cohort × window × source × flag | Means and medians of pre counts and each paper's post-period annual average. Post medians are not averages of yearly medians. |
| `opencitations_annual_summary.csv` | Sample × source × year × flag | Annual paper counts, means and medians, including observed zero counts. |
| `opencitations_models.csv` | Sample × cohort × window × source | Article/year fixed-effects Poisson estimates and article-clustered intervals, checked against the closed-form ratio used in the paired comparison. |

Both source-contrast files use the generic `alternative` column (the OpenAlex
comparison previously named it `openalex`). The `source` column identifies its
measurement. The absolute difference is replacement-source DiD minus historical
DiD. The log-ratio difference compares the two estimated growth ratios; exponentiating
it does not produce a percentage-point difference between percentage effects.

The selected sensitivity drops every history with any unresolved citing year,
even if that missing year might lie outside the analysis window. It retains 60
papers and is not representative of the full cohort. No missing date is inferred
from `timespan` or a paper's total citations. Both databases use exactly the same
papers within every contrast. All-type OpenCitations counts are not the pending
OpenAlex article/review outcome.

The meta-analysis source sensitivity, `data/meta/opencitations_synthesis.csv`,
replaces the neuroscience component with this measurement at the common 2010–2012
window. It preserves equal audit weights and the existing conditional inference.
It does not add a third independent audit.

Independent reconstruction reproduced all list/count matches, source hashes,
annual means and medians, point estimates and paired bootstrap intervals. The
main source-difference estimates and intervals agree to numerical precision.
