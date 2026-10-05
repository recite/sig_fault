# I4R data construction

## Sources and row units

`sources.csv` freezes the I4R report catalog and the union of I4R/RePEc discussion-paper listings on 2026-10-05. `source_id` identifies a listing. An OSF node can host assessments of multiple articles, and several listings can point to the same file. Neither shared nodes nor repeated downloads establish original-paper identity.

`reviews/*.json` are source-reader records, including scope, passages, caveats and replies. `source_reviews.csv` harmonizes their varying field names; a review record is not an independently verified material-error label. The explicit `assessment_eligibility` and `assessment_resolved` fields support the eventual 90% coverage calculation. Unadjudicated eligibility remains unresolved, so the denominator is not yet established.

`curated_claims.csv` is the manually adjudicated input linking a particular error, its consequence, its evidence and a disclosure history. `disclosure_adjudications.json` records additional checks on selected early public versions. `aggregate_article_roster.json` transcribes the bibliographic roster in discussion paper 107, Appendix B; `psychology_article_roster.json` transcribes discussion paper 326's article/report roster. These are identity inputs, not article-specific error classifications. The economics/political-science aggregate package's numerical identifiers cannot be joined to named papers.

`metadata_provenance.csv` preserves every accepted provider response separately, including OpenAlex fields retained when Crossref supplies a publication date.

`verified_metadata.csv` freezes the verified bibliographic fields used by the offline build, with the lookup URL, response hash and retrieval time. `build --refresh-metadata` recreates it from successful local Crossref/OpenAlex responses. Ordinary `build` uses this public snapshot. `identity_decisions.csv` records clerical corrections. No approximate-title match is silently accepted.

`source_manifest.csv` records retrieved source URLs, UTC timestamps, bytes and SHA-256 hashes. Paths are relative to the repository. Private full texts and raw responses can be reacquired using these pointers; redistributing a source file is distinct from citing it.

## Join contracts

| Left universe | Right table/key | Cardinality and output | Unmatched policy |
| --- | --- | --- | --- |
| All catalog entries | Reviews / `source_id` | One-to-one; same number of catalog rows | Explicit pending disposition |
| Sources and original articles | `source_articles` / (`source_id`, `article_id`) | Deliberate many-to-many bridge, one row per source–article pair | Unresolved sources remain in the catalog |
| Title candidates | Metadata / `article_id`, DOI/title checks | At most one accepted identity per candidate; DOI aliases map many-to-one | Keep unresolved candidates without analysis eligibility |
| Curated claim | Article / normalized-title ID then alias | Many claims to one original article | Validation fails on absent article/source |
| Event | Assessment / `assessment_id` | Many-to-one; article ID and materiality/verification must agree | Validation fails on absent or contradictory evidence |
| Original article and calendar year | Citations / (`article_id`, `year`) | At most one count per year | Missing/incomplete remains missing |
| Event and horizon | Ranked controls | At most three controls per event; controls may recur across events | Exclusion ledger; no fallback journal expansion |
| Selected stack | Annual citation counts | Exactly two observations per member per horizon | Exclude whole stack if any required outcome is missing |

The registry validator checks keys and foreign keys. Matching checks unique original IDs, events and annual counts. The analysis rejects duplicate or incomplete article-period pairs and verifies its coefficient against the direct matched change. Reused controls retain their original article ID for clustering. The profile in the dictionary reports actual row counts, key duplicates and missingness.

## Recode ledger

| Operation | Rule and rationale | Audit record |
| --- | --- | --- |
| DOI normalization | Remove DOI URL/prefix and lowercase; do not invent a DOI from a title | Source DOI, lookup record and identity decision |
| Title identity | Normalize Unicode/case/punctuation; allow documented formatting, retraction prefix and team suffix | Unresolved/ambiguous resolution logs retained |
| Source transcription repair | Appendix B's `110.1257/aer.20210182` becomes `10.1257/aer.20210182`; verify against publisher | Roster note and metadata response |
| Clerical identity repair | “Senders and Receives” becomes “Senders and Receivers” | `identity_decisions.csv` |
| DOI aliases | Same supplied/resolved DOI maps to one article; retain alias crosswalk | `article_aliases.csv` |
| Error labels | Source screen never becomes verified error automatically; materiality and source verification are separate | `curated_claims.csv`, assessments, reviews |
| Disclosure dates | Earliest substantiated public error disclosure; preserve day/month/year precision | Events and dated evidence |
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

The source review is assisted screening followed by selective independent checks, not a reliability-validated census of material errors. The unresolved assessment denominator prevents a claim of 90% completion. DOI/title verification establishes identity, not claim correctness. Citation edges establish an indexed relationship, not reliance on the erroneous finding. The matched sample will be selected by age, exposure timing, metadata availability and overlap; it cannot be described as representative of all errors without additional evidence.
