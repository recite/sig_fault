# I4R data construction

## Sources and row units

`sources.csv` freezes the I4R report catalog and the union of I4R/RePEc discussion-paper listings on 2026-10-05. `source_id` identifies a listing. An OSF node can host assessments of multiple articles, and several listings can point to the same file. Neither shared nodes nor repeated downloads establish original-paper identity.

`reviews/*.json` are source-reader records, including scope, passages, caveats and replies. `source_reviews.csv` harmonizes their varying field names and incorporates `source_adjudications.csv`. The latter records independent targeted review, eligibility, resolution, duplicate evidence and limitations. `source_adjudication_notes.json` retains additional review details, including multiple assessment teams within a project. `source_units.csv` collapses only declared duplicate links; conflicting classifications or eligibility block resolution. These are catalog-source groups, not an enumerated population of independent assessments. `coverage_scope.json` prevents the 90% completion gate from passing while shared bundles and unacquired attachments remain unresolved. A favorable assessment is not certification that an article is error-free.

`assessment_inventory.json` is the reviewed input for independent assessment units across reviewed discussion papers and reconciled report bundles. A confirmed unit is one reviewer team assessing one original article; its plans, versions and author replies are supporting documents. `assessment_inventory.csv`, `assessment_sources.csv` and `assessment_documents.csv` expose the unit, catalog and document relations. Different teams assessing the same article remain separate. Reports without a byline remain as observed assessment records with an empty reviewer team, `reviewer_team_identification=not_reported`, and `unit_equivalence=unresolved`. Their findings can still be assessed, but these records are not confirmed additional independent teams and cannot pass the population-completion gate. `supporting_source_ids` attaches replies to the relevant assessment without treating the respondent authors as another assessment team. A shared-project file can be acquired through another catalog listing only with an explicit, evidenced retrieval alias. The misdirected effort entry links to actual exercise-review attachments without resolving its intended effort assessment. `assessment_scope.json` records the scope review for each examined catalog source; `assessment_scope.csv` retains every catalog entry, including pending ones. Fully enumerated reports must link all identified units; supporting replies link existing units; non-assessment records require evidence; unresolved multi-article audits remain open. Both a complete source-scope ledger and the independent-assessment resolution fraction are required before the coverage gate can pass. This partial unit inventory is not a denominator for the full collection.

`archive_retrieval.csv` records acquisition and size-limit outcomes for each root ZIP. `archive_members.csv` inventories all non-directory members, including data/code and unextracted nested archives. Extracted members retain their original internal path, CRC, parent-archive SHA-256 and extracted-byte SHA-256. Destinations use member identifiers, so archive paths cannot write outside the cache. Standard metadata forks are excluded; PDFs without filename extensions are detected by their bytes. Direct DOCX bodies, footnotes and endnotes are extracted as text without executing document code; images and page layout are not inferred from that text. Catalog-listed TXT, TeX and Rmd files are retained as raw source text. `repository_queries.csv` records provider/child/folder pages and failures, and `repository_documents.csv` holds the traversed files. Private or incomplete listings never establish absence of a report. `nested_archive_reviews.json` records the content-role review and complete member hashes for all five nested archives: input data, original-paper documentation and unfilled templates, with no additional assessment identified.

`curated_claims.csv` is the manually adjudicated input linking a particular error, its consequence, its evidence and a disclosure history. `claim_adjudications.json` records detailed error mechanisms, affected findings, numerical consequences and disputes. Material secondary findings can qualify under the stated design; their correction does not imply that the headline conclusion fails. The parent–teacher design discrepancy remains unresolved because improbable allocation alone does not establish a randomization error. `disclosure_adjudications.json` records additional checks on selected early public versions. `aggregate_article_roster.json` transcribes the bibliographic roster in discussion paper 107, Appendix B; `psychology_article_roster.json` transcribes discussion paper 326's article/report roster. These are identity inputs, not article-specific error classifications. The economics/political-science aggregate package's numerical identifiers cannot be joined to named papers.

`metadata_provenance.csv` preserves every accepted provider response separately, including OpenAlex fields retained when Crossref supplies a publication date.

`verified_metadata.csv` freezes the verified bibliographic fields used by the offline build, with the lookup URL, response hash and retrieval time. `build --refresh-metadata` recreates it from successful local Crossref/OpenAlex responses. Ordinary `build` uses this public snapshot. `identity_decisions.csv` records clerical corrections. No approximate-title match is silently accepted. Crossref title search accepts only unique exact normalized journal-article matches with at least four title words; direct DOI verification also permits short titles.

`indexed_publication_year` and `indexed_publication_date` retain OpenAlex indexing. Both treated and control risk-set queries use that same indexed year. `publication_date` and `publication_year` use the earliest date supplied in the accepted Crossref online/print/publication fields, with `publication_date_source` retained. The strict age gate uses these publisher dates symmetrically. Crossref may omit an earlier online-first date: this can conservatively exclude an article, and its date is not described as a verified earliest public appearance. Unknown publisher dates remain unknown. `control-metadata` supplies the same publisher-date check for controls; alias deduplication preserves that check independently of the indexed representative.

`source_manifest.csv` records retrieved source URLs, UTC timestamps, bytes and SHA-256 hashes. Paths are relative to the repository. Private full texts and raw responses can be reacquired using these pointers; redistributing a source file is distinct from citing it.

## Join contracts

| Left universe | Right table/key | Cardinality and output | Unmatched policy |
| --- | --- | --- | --- |
| All catalog entries | Reviews and adjudications / `source_id` | One-to-one; same number of catalog rows | Explicit unresolved disposition |
| Sources and original articles | `source_articles` / (`source_id`, `article_id`) | Deliberate many-to-many bridge, one row per source–article pair; catalog target hints are not verified assessment links | Unresolved sources remain in the catalog |
| Title candidates | Metadata / `article_id`, DOI/title checks | At most one accepted identity per candidate; DOI aliases map many-to-one | Keep unresolved candidates without analysis eligibility |
| Independent assessment unit | Catalog sources and document IDs | Many-to-many support relations; one team/article unit regardless of reply/version count | Fail on undeclared document sources; preserve evidenced retrieval aliases |
| ZIP member | Root archive / `archive_document_id` | One row per member index/path; duplicate names retained separately | Size limits, nested ZIPs and extraction failures are explicit |
| Curated claim | Article / normalized-title ID then alias | Many claims to one original article | Validation fails on absent article/source |
| Event | Assessment / `assessment_id` | Many-to-one; article ID and materiality/verification must agree | Validation fails on absent or contradictory evidence |
| Original article and calendar year | Citations / (`article_id`, `year`) | At most one count per year | Missing/incomplete remains missing |
| Event and horizon | Ranked controls | At most three controls per event; controls may recur across events | Exclusion ledger; no fallback journal expansion |
| Selected stack | Annual citation counts | Exactly two observations per member per horizon | Exclude whole stack if any required outcome is missing |

The registry validator checks keys and foreign keys. Matching checks unique original IDs, events and annual counts. The analysis rejects duplicate or incomplete article-period pairs and verifies its coefficient against the direct matched change. Reused controls retain their original article ID for clustering. The profile in the dictionary reports actual row counts, key duplicates and missingness.

## Recode ledger

| Operation | Rule and rationale | Audit record |
| --- | --- | --- |
| Title formatting | Decode HTML entities and strip recognized retraction/formatting prefixes for identity checks; preserve stable article IDs | Original provider title and verified metadata |
| DOI normalization | Remove DOI URL/prefix and lowercase; do not invent a DOI from a title | Source DOI, lookup record and identity decision |
| Title identity | Normalize Unicode/case/punctuation; allow documented formatting, retraction prefix and team suffix | Unresolved/ambiguous resolution logs retained |
| Source transcription repair | Appendix B's `110.1257/aer.20210182` becomes `10.1257/aer.20210182`; verify against publisher | Roster note and metadata response |
| Clerical identity repair | “Senders and Receives” becomes “Senders and Receivers” | `identity_decisions.csv` |
| DOI aliases | Same supplied/resolved DOI maps to one article; retain alias crosswalk | `article_aliases.csv` |
| Error labels | Source screen never becomes verified error automatically; materiality and source verification are separate | `curated_claims.csv`, assessments, reviews |
| Disclosure dates | Earliest substantiated public error disclosure; preserve day/month/year precision | Events and dated evidence |
| Incomplete control histories | Wait for all otherwise eligible controls to have both pre-year counts before ranking; a partial download cannot determine the match | Event exclusion ledger |
| Repeated disclosures | Use first verified material disclosure before applying age/follow-up restrictions | Match exclusion `subsequent_disclosure` |
| Retractions | Exclude controls retracted by the horizon; unknown retraction date is unresolved; retain later dates | `retractions.csv` and candidate exclusions |
| Control identity | Same-DOI indexed records form one control article; retain work aliases and combine their incoming edges | `control_aliases.csv` |
| Citation identity | DOI aliases count once at earliest indexed publication date; otherwise use OpenAlex work ID | `citation_edges.csv` |
| Citation zeros | Only complete, checked query coverage supports zero | Citation retrieval status and annual counts |
| Matching transform | `log1p` of two pre-year counts and their change; standardize within risk set plus treated article | Candidate distances and balance |
| Weights | Treated 1; each selected control 1/k; equal weight across treated articles | Matches and analysis panel |
| Missing outcomes | Complete stack required; longer-horizon cohorts require both +1 and +h | Panel exclusion ledger |
| Earlier placebo | All members published before year −3 begins | Sensitivity panel |
| Disclosure timing | Compare known-day disclosures in first versus second half of year; year-only dates omitted from this check | Sensitivity panel |

Dates with only a known year are not assigned January 1. Calendar-year eligibility uses the known public year; source creation/modification timestamps retain their separate meanings. CSV readers preserve IDs as strings and empty strings as missing metadata, with explicit numeric conversion at analysis boundaries. Zero citations is an observed value, never an unknown code.

## Interpretation limits

The source review combines initial screening and independent targeted adjudication, not a reliability-validated census of material errors. Source-level review resolves only the catalog-named target; it does not silently resolve every attachment in a shared project. The unresolved assessment denominator prevents a claim of 90% completion. DOI/title verification establishes identity, not claim correctness. Citation edges establish an indexed relationship, not reliance on the erroneous finding. The matched sample will be selected by age, exposure timing, metadata availability and overlap; it cannot be described as representative of all errors without additional evidence.

Publisher-date verification retains unresolved controls when Crossref returns a different DOI, even with a matching title. Several Economic Journal records have `ej` versus `ecoj` DOI forms; these require an explicit alias reconciliation before they can enter the verified pool. Formatting-only title differences are normalized. No DOI mismatch is silently accepted.

The DP107 and DP287 synthesis rosters were checked row by row: all 110 DOI identities match after the documented typo correction. They describe the same assessment cohort. The two monetary-policy-uncertainty rows link distinct DP076/077 teams; the roster therefore has 110 assessments of 109 original titles. Related aggregate-source links preserve this version relationship without adding treatment events.

The citation edge table retains indexed links that predate the target article’s publisher publication year, which can reflect working-paper citations or bibliographic dating problems. Annual counts begin at the publisher publication year (or the collection start, if later). Such earlier links are preserved for audit but do not extend the baseline or satisfy article-age requirements.

Publisher retraction notices verified directly are retained in `retractions.csv` with the notice URL as `dataset_url`; a Retraction Watch refresh replaces that provider's rows while preserving independently verified notices. This matters when indexed retraction status is known but the frozen external database does not supply the dated notice. Exposure eligibility uses the dated notice relative to the first public error disclosure, not current retracted status alone.

For a catalog listing naming one article, scope concerns all independent assessments of that article represented by the listing. A shared retrieval project does not turn each article-specific listing into an aggregate audit. The 17 w7vpu assessments are enumerated under DP124; fourteen individual listings can therefore be closed on their existing target-specific units without adding links to unrelated articles. Merchant Towns still requires both independently authored assessments. Scope closure does not resolve an uncertain error classification or disclosure date.

Journal-article title matching excludes identifiable SSRN deposits (`10.2139/ssrn.*` or the container title `SSRN Electronic Journal`), even when the deposited type is `journal-article`. A unique exact match to a journal article can then resolve the identity; two distinct matching journal DOIs still remain ambiguous. Source-checked short titles and spelling/title variants are recorded individually in `identity_decisions.csv`, with report pages and publisher metadata URLs. When two target names resolve to one DOI, the canonical record retains the verified OpenAlex work identity; conflicting work IDs require review instead of being silently discarded.
