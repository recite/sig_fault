# I4R data dictionary

Empty strings mean unavailable metadata or structurally absent evidence; complete zero citation counts are observed. R estimates may use NA for unavailable uncertainty. All identifiers are strings.

Generated from the declared schema and current CSV contents. Row units, sources and transformations are explained in [the construction contract](data-construction.md).

## analysis_panel.csv

One row: article-period in a matched stack. Rows: 0. Key: stack_id, article_id, post. Producer: `i4r_match`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `stack_id` | string | Identifier for a matched event/horizon or sensitivity comparison. | 0 |  |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 |  |
| `warning_id` | string | Shared disclosure identifier for dependence when one warning affects multiple articles. | 0 |  |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 |  |
| `year` | integer | Public disclosure year in events; observed citation year in citation/panel tables. | 0 |  |
| `event_time` | integer | Calendar year relative to disclosure; zero omitted from primary estimation. | 0 |  |
| `horizon` | integer | Full calendar years after disclosure, primary 1; secondary 2 and 3. | 0 |  |
| `treated` | integer | 1 for affected original article; 0 for matched control. | 0 |  |
| `post` | integer | 1 for after period, 0 for before period; placebo period coding follows comparison order. | 0 |  |
| `weight` | number | Treated article weight 1; selected controls total 1 per stack. | 0 |  |
| `citations` | number | Deduplicated citing journal articles/reviews; sensitivity averages may be fractional. | 0 |  |

## article_aliases.csv

One row: superseded article ID. Rows: 4. Key: alias. Producer: `i4r_registry build`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `alias` | string | Superseded title-derived ID mapping to canonical article_id. | 0 | i4r_1ba6b15fcc8cd9; i4r_975b8fb7dcee2d; i4r_a92040849a75db; i4r_ed0c323ab14dc4 |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | i4r_093bc85ab4502e; i4r_1e972a57ca9cf5; i4r_bdbd4c55c23f42 |

## articles.csv

One row: candidate original article. Rows: 436. Key: article_id. Producer: `i4r_registry build`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 436 distinct nonmissing values |
| `title` | string | Catalog or bibliographic title; candidate titles may remain unresolved. | 0 | 436 distinct nonmissing values |
| `doi` | string | Normalized original-article DOI; empty if unresolved. | 244 | 192 distinct nonmissing values |
| `openalex_id` | string | Full OpenAlex work URL for resolved identity. | 426 | https://openalex.org/W2618893046; https://openalex.org/W2735584017; https://openalex.org/W2738960030; https://openalex.org/W2783385777; https://openalex.org/W3124366560; https://openalex.org/W3198801792; https://openalex.org/W3203294756; https://openalex.org/W4283645972; https://openalex.org/W4283722583; https://openalex.org/W4392104295 |
| `journal` | string | Journal name from catalog or verified metadata. | 57 | 35 distinct nonmissing values |
| `journal_id` | string | OpenAlex journal/source URL used for exact journal matching. | 426 | https://openalex.org/S23254222; https://openalex.org/S2764866340; https://openalex.org/S42893225; https://openalex.org/S45992627; https://openalex.org/S88935262; https://openalex.org/S95323914 |
| `publication_date` | string | Earliest indexed original publication date; ISO year, month or day precision retained. | 244 | 129 distinct nonmissing values |
| `publication_year` | integer | Calendar year of original publication. | 244 | 2001 to 2026 |
| `type` | string | OpenAlex-compatible document type; primary outcomes count article and review. | 244 | article |
| `abstract` | string | Original-article abstract text where supplied by OpenAlex; blank uses title-only matching. | 427 | 9 distinct nonmissing values |
| `identity_verified` | string | yes only after accepted bibliographic match; pending otherwise. | 0 | pending; yes |
| `retracted` | string | Current indexed retraction flag: yes, no or unknown; not a historical treatment indicator. | 0 | no; unknown; yes |
| `retraction_date` | string | Earliest known retraction date from dated notice ledger. | 433 | 2025-04-06; 2025-06-24; 2026-05-21 |
| `retraction_source` | string | Notice URL establishing retraction date. | 433 | https://doi.org/10.1007/s00148-025-01114-2; https://doi.org/10.1016/j.euroecorev.2025.105026; https://doi.org/10.1371/journal.pone.0349829 |

## assessments.csv

One row: candidate significant-error assessment. Rows: 23. Key: assessment_id. Producer: `i4r_registry build`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `assessment_id` | string | Identifier for a particular article-specific error assessment. | 0 | 23 distinct nonmissing values |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 20 distinct nonmissing values |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 23 distinct nonmissing values |
| `category` | string | Type of error or broader concern; primary cohort requires demonstrated material error. | 0 | demonstrated_material_error; source_supported_material_error |
| `material` | string | yes/no/unresolved: whether the documented error materially changes a substantive finding. | 0 | yes |
| `error_verified` | string | yes, pending_second_review or unresolved; only yes enters verified-error cohort. | 0 | pending_second_review; yes |
| `affected_claim` | string | Substantive result affected; does not imply every finding in the article fails. | 0 | 14 distinct nonmissing values |
| `evidence_summary` | string | Paraphrased evidence supporting a candidate assessment, including limitations. | 0 | 22 distinct nonmissing values |
| `evidence_locator` | string | Public source and page/table/section identifying the error and consequence. | 1 | 20 distinct nonmissing values |
| `dispute_status` | string | Author acknowledgment, response, dispute or unresolved status. | 0 | No original-author reply reviewed; source evidence independently checked.; See disclosure_adjudications.json, including author responses; acknowledged; author_disputes_connection; author_feedback_acknowledged; no separate reply reviewed; code_text_discrepancies_acknowledged; materiality_disputed; not_reviewed; proposed_author_correction; approval_not_established; see_full_review_record |
| `verification_scope` | string | Evidence actually checked; source verification is distinct from re-running code. | 0 | 16 distinct nonmissing values |
| `public_year` | integer | Known public assessment year for time-aware control exclusions. | 17 | 2020 to 2024 |

## citation_edges.csv

One row: deduplicated original–citing article pair. Rows: 0. Key: article_id, citing_work_id. Producer: `i4r_citations fetch`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 |  |
| `citing_work_id` | string | OpenAlex work ID of the citing publication. | 0 |  |
| `citing_doi` | string | Normalized DOI of the citing publication; absent uses work ID for deduplication. | 0 |  |
| `publication_year` | integer | Calendar year of original publication. | 0 |  |
| `publication_date` | string | Earliest indexed original publication date; ISO year, month or day precision retained. | 0 |  |
| `type` | string | OpenAlex-compatible document type; primary outcomes count article and review. | 0 |  |

## citation_retrieval.csv

One row: original article citation retrieval. Rows: 1. Key: article_id. Producer: `i4r_citations fetch`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | i4r_9008b2600de80c |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | incomplete |
| `detail` | string | Retrieval error or diagnostic detail; empty for successful retrieval. | 0 | 1 distinct nonmissing values |

## citations.csv

One row: original article–calendar-year. Rows: 0. Key: article_id, year. Producer: `i4r_citations fetch`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 |  |
| `year` | integer | Public disclosure year in events; observed citation year in citation/panel tables. | 0 |  |
| `citations` | number | Deduplicated citing journal articles/reviews; sensitivity averages may be fractional. | 0 |  |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 |  |

## control_aliases.csv

One row: known indexed control-work alias. Rows: 0. Key: alias_openalex_id. Producer: `i4r_citations candidates`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `alias_openalex_id` | string | Known OpenAlex work alias of a canonical control article; incoming edges are combined across aliases. | 0 |  |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 |  |

## control_articles.csv

One row: external control candidate. Rows: 0. Key: article_id. Producer: `i4r_citations candidates/retractions`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 |  |
| `title` | string | Catalog or bibliographic title; candidate titles may remain unresolved. | 0 |  |
| `doi` | string | Normalized original-article DOI; empty if unresolved. | 0 |  |
| `openalex_id` | string | Full OpenAlex work URL for resolved identity. | 0 |  |
| `journal` | string | Journal name from catalog or verified metadata. | 0 |  |
| `journal_id` | string | OpenAlex journal/source URL used for exact journal matching. | 0 |  |
| `publication_date` | string | Earliest indexed original publication date; ISO year, month or day precision retained. | 0 |  |
| `publication_year` | integer | Calendar year of original publication. | 0 |  |
| `type` | string | OpenAlex-compatible document type; primary outcomes count article and review. | 0 |  |
| `abstract` | string | Original-article abstract text where supplied by OpenAlex; blank uses title-only matching. | 0 |  |
| `identity_verified` | string | yes only after accepted bibliographic match; pending otherwise. | 0 |  |
| `retracted` | string | Current indexed retraction flag: yes, no or unknown; not a historical treatment indicator. | 0 |  |
| `retraction_date` | string | Earliest known retraction date from dated notice ledger. | 0 |  |
| `retraction_source` | string | Notice URL establishing retraction date. | 0 |  |

## crossref_retrieval.csv

One row: publisher lookup. Rows: 436. Key: article_id. Producer: `i4r_registry crossref`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 436 distinct nonmissing values |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | no_doi; retrieved |

## curated_claims.csv

One row: adjudicated candidate claim/disclosure. Rows: 23. Key: assessment_id. Producer: `manual evidence review`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `title` | string | Catalog or bibliographic title; candidate titles may remain unresolved. | 0 | 21 distinct nonmissing values |
| `doi` | string | Normalized original-article DOI; empty if unresolved. | 9 | 13 distinct nonmissing values |
| `assessment_id` | string | Identifier for a particular article-specific error assessment. | 0 | 23 distinct nonmissing values |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 23 distinct nonmissing values |
| `category` | string | Type of error or broader concern; primary cohort requires demonstrated material error. | 0 | demonstrated_material_error; source_supported_material_error |
| `material` | string | yes/no/unresolved: whether the documented error materially changes a substantive finding. | 0 | yes |
| `error_verified` | string | yes, pending_second_review or unresolved; only yes enters verified-error cohort. | 0 | pending_second_review; yes |
| `affected_claim` | string | Substantive result affected; does not imply every finding in the article fails. | 0 | 14 distinct nonmissing values |
| `evidence_summary` | string | Paraphrased evidence supporting a candidate assessment, including limitations. | 0 | 22 distinct nonmissing values |
| `evidence_locator` | string | Public source and page/table/section identifying the error and consequence. | 1 | 20 distinct nonmissing values |
| `dispute_status` | string | Author acknowledgment, response, dispute or unresolved status. | 0 | No original-author reply reviewed; source evidence independently checked.; See disclosure_adjudications.json, including author responses; acknowledged; author_disputes_connection; author_feedback_acknowledged; no separate reply reviewed; code_text_discrepancies_acknowledged; materiality_disputed; not_reviewed; proposed_author_correction; approval_not_established; see_full_review_record |
| `verification_scope` | string | Evidence actually checked; source verification is distinct from re-running code. | 0 | 16 distinct nonmissing values |
| `public_year` | integer | Known public assessment year for time-aware control exclusions. | 23 |  |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 | 23 distinct nonmissing values |
| `warning_id` | string | Shared disclosure identifier for dependence when one warning affects multiple articles. | 0 | 23 distinct nonmissing values |
| `date` | string | Disclosure date in events/claims, retraction date in retractions; blank when exact day unknown. | 20 | 2021-02-11; 2024-01-17; 2024-03-27 |
| `year` | integer | Public disclosure year in events; observed citation year in citation/panel tables. | 17 | 2020 to 2024 |
| `date_precision` | string | day/month/year: precision supported by public evidence. | 17 | day; year |
| `publicity_verified` | string | yes only when public timing has a documented source. | 0 | no; yes |
| `date_evidence_url` | string | Public evidence establishing disclosure timing. | 17 | https://andreaskotsadam.files.wordpress.com/2023/02/accepted-comment.pdf; https://arxiv.org/abs/2401.13694; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3645463; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3744650; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3980178; https://x.com/johannarickne/status/1773002832632836549 |
| `date_evidence` | string | Reasoning for earliest substantiated public year/day and unresolved earlier versions. | 17 | 6 distinct nonmissing values |
| `already_retracted` | string | Retraction status at disclosure: no required for primary cohort. | 0 | no; unknown |

## document_retrieval.csv

One row: file retrieval. Rows: 622. Key: document_id. Producer: `i4r_sources documents`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `document_id` | string | Identifier for a source-linked file; duplicate contents can have different IDs. | 0 | 622 distinct nonmissing values |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | retrieved |
| `detail` | string | Retrieval error or diagnostic detail; empty for successful retrieval. | 622 |  |
| `sha256` | string | SHA-256 content checksum of retrieved bytes. | 0 | 622 distinct nonmissing values |

## documents.csv

One row: source-linked file. Rows: 706. Key: document_id. Producer: `i4r_sources inventory`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 572 distinct nonmissing values |
| `document_id` | string | Identifier for a source-linked file; duplicate contents can have different IDs. | 0 | 706 distinct nonmissing values |
| `name` | string | Source-provided document filename or linked_fulltext placeholder. | 0 | 326 distinct nonmissing values |
| `url` | string | Source or download URL; no authentication credentials. | 0 | 706 distinct nonmissing values |
| `format` | string | Filename-derived document format; unknown when not inferred. | 4 | csv; do; docx; dta; ipynb; pdf; r; rmd; rproj; txt; xlsx; zip |
| `created_at` | string | Provider creation timestamp; does not establish public disclosure. | 331 | 375 distinct nonmissing values |
| `modified_at` | string | Provider modification timestamp; does not establish public disclosure. | 331 | 375 distinct nonmissing values |
| `date_meaning` | string | Explicit interpretation of the accompanying source timestamp. | 0 | File upload/modification, not established public disclosure; No public disclosure date inferred |

## event_trajectories.csv

One row: matched article–event–relative-year. Rows: 0. Key: event_id, article_id, event_time. Producer: `i4r_match`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 |  |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 |  |
| `treated` | integer | 1 for affected original article; 0 for matched control. | 0 |  |
| `weight` | number | Treated article weight 1; selected controls total 1 per stack. | 0 |  |
| `event_time` | integer | Calendar year relative to disclosure; zero omitted from primary estimation. | 0 |  |
| `citations` | number | Deduplicated citing journal articles/reviews; sensitivity averages may be fractional. | 0 |  |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 |  |
| `disclosure_date` | string | Exact public-disclosure date when known, otherwise blank. | 0 |  |
| `date_precision` | string | day/month/year: precision supported by public evidence. | 0 |  |

## events.csv

One row: candidate error disclosure. Rows: 23. Key: event_id. Producer: `i4r_registry build`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 | 23 distinct nonmissing values |
| `warning_id` | string | Shared disclosure identifier for dependence when one warning affects multiple articles. | 0 | 23 distinct nonmissing values |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 20 distinct nonmissing values |
| `assessment_id` | string | Identifier for a particular article-specific error assessment. | 0 | 23 distinct nonmissing values |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 23 distinct nonmissing values |
| `date` | string | Disclosure date in events/claims, retraction date in retractions; blank when exact day unknown. | 20 | 2021-02-11; 2024-01-17; 2024-03-27 |
| `year` | integer | Public disclosure year in events; observed citation year in citation/panel tables. | 17 | 2020 to 2024 |
| `date_precision` | string | day/month/year: precision supported by public evidence. | 17 | day; year |
| `publicity_verified` | string | yes only when public timing has a documented source. | 0 | no; yes |
| `date_evidence_url` | string | Public evidence establishing disclosure timing. | 17 | https://andreaskotsadam.files.wordpress.com/2023/02/accepted-comment.pdf; https://arxiv.org/abs/2401.13694; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3645463; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3744650; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3980178; https://x.com/johannarickne/status/1773002832632836549 |
| `date_evidence` | string | Reasoning for earliest substantiated public year/day and unresolved earlier versions. | 17 | 6 distinct nonmissing values |
| `error_verified` | string | yes, pending_second_review or unresolved; only yes enters verified-error cohort. | 0 | pending_second_review; yes |
| `material` | string | yes/no/unresolved: whether the documented error materially changes a substantive finding. | 0 | yes |
| `already_retracted` | string | Retraction status at disclosure: no required for primary cohort. | 0 | no; unknown |

## identity_decisions.csv

One row: clerical identity decision. Rows: 1. Key: article_id. Producer: `manual evidence review`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | i4r_40fdc820b2481c |
| `title` | string | Catalog or bibliographic title; candidate titles may remain unresolved. | 0 | Peer Effects in Academic Research: Senders and Receivers |
| `doi` | string | Normalized original-article DOI; empty if unresolved. | 0 | 10.1093/ej/ueac031 |
| `evidence` | string | Source pointer or documented identity/link decision. | 0 | 1 distinct nonmissing values |
| `source_url` | string | Public evidence or notice URL. | 0 | https://api.crossref.org/works/10.1093/ej/ueac031 |

## identity_resolution.csv

One row: OpenAlex resolution attempt. Rows: 7. Key: article_id. Producer: `i4r_registry resolve`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | i4r_40a2331682db05; i4r_6d77bf53ba0e83; i4r_9008b2600de80c; i4r_9add9d2fff6627; i4r_a8e2f8f02be321; i4r_ba9c5a9dc17190; i4r_ece0397b04bfa9 |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | doi_resolved; failed |
| `detail` | string | Retrieval error or diagnostic detail; empty for successful retrieval. | 6 | HTTP Error 429: Too Many Requests |

## match_balance.csv

One row: selected control balance. Rows: 0. Key: event_id, control_id, horizon. Producer: `i4r_match`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 |  |
| `control_id` | string | Original control-article ID retained across reused matches. | 0 |  |
| `pre2_smd` | number | Control minus treated log1p citations in year -2, divided by pooled risk-set SD. | 0 |  |
| `pre1_smd` | number | Control minus treated log1p citations in year -1, divided by pooled risk-set SD. | 0 |  |
| `change_smd` | number | Standardized difference in the two-year pre-citation log change. | 0 |  |
| `text_cosine_distance` | number | One minus title/abstract TF-IDF cosine similarity. | 0 |  |
| `horizon` | integer | Full calendar years after disclosure, primary 1; secondary 2 and 3. | 0 |  |

## match_candidates.csv

One row: screened event–control–horizon. Rows: 0. Key: event_id, control_id, horizon. Producer: `i4r_match`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 |  |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 |  |
| `control_id` | string | Original control-article ID retained across reused matches. | 0 |  |
| `distance` | number | Standardized pre-citation and text matching distance; no post outcomes used. | 0 |  |
| `eligible` | string | yes/no after metadata, age, exposure and citation-caliper gates. | 0 |  |
| `reason` | string | Explicit exclusion reason; blank if eligible. | 0 |  |
| `horizon` | integer | Full calendar years after disclosure, primary 1; secondary 2 and 3. | 0 |  |

## match_exclusions.csv

One row: excluded event–horizon. Rows: 69. Key: event_id, horizon. Producer: `i4r_match`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 | 23 distinct nonmissing values |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 20 distinct nonmissing values |
| `reason` | string | Explicit exclusion reason; blank if eligible. | 0 | error_not_verified_material; incomplete_followup; incomplete_risk_set_retrieval; insufficient_article_age; subsequent_disclosure |
| `horizon` | integer | Full calendar years after disclosure, primary 1; secondary 2 and 3. | 0 | 1 to 3 |

## matches.csv

One row: selected event–control–horizon. Rows: 0. Key: event_id, control_id, horizon. Producer: `i4r_match`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 |  |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 |  |
| `control_id` | string | Original control-article ID retained across reused matches. | 0 |  |
| `rank` | integer | Distance order within event/horizon; 1 is closest; stable ID breaks ties. | 0 |  |
| `distance` | number | Standardized pre-citation and text matching distance; no post outcomes used. | 0 |  |
| `weight` | number | Treated article weight 1; selected controls total 1 per stack. | 0 |  |
| `horizon` | integer | Full calendar years after disclosure, primary 1; secondary 2 and 3. | 0 |  |

## metadata_provenance.csv

One row: accepted bibliographic provider response for an identity. Rows: 202. Key: article_id, provider. Producer: `i4r_registry build --refresh-metadata`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 192 distinct nonmissing values |
| `provider` | string | Accepted bibliographic provider: crossref or openalex. | 0 | crossref; openalex |
| `path` | string | Repository-relative cache path; private raw contents are not redistributed. | 0 | 202 distinct nonmissing values |
| `url` | string | Source or download URL; no authentication credentials. | 0 | 202 distinct nonmissing values |
| `sha256` | string | SHA-256 content checksum of retrieved bytes. | 0 | 202 distinct nonmissing values |
| `retrieved_at` | string | UTC retrieval timestamp from cached response provenance. | 0 | 202 distinct nonmissing values |

## panel_exclusions.csv

One row: incomplete event–horizon. Rows: 0. Key: event_id, horizon. Producer: `i4r_match`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 |  |
| `horizon` | integer | Full calendar years after disclosure, primary 1; secondary 2 and 3. | 0 |  |
| `reason` | string | Explicit exclusion reason; blank if eligible. | 0 |  |

## retractions.csv

One row: retraction notice. Rows: 3. Key: record_id. Producer: `i4r_citations retractions`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `doi` | string | Normalized original-article DOI; empty if unresolved. | 0 | 10.1007/s00148-024-00984-2; 10.1016/j.euroecorev.2018.09.008; 10.1371/journal.pone.0255392 |
| `date` | string | Disclosure date in events/claims, retraction date in retractions; blank when exact day unknown. | 0 | 2025-04-06; 2025-06-24; 2026-05-21 |
| `source_url` | string | Public evidence or notice URL. | 0 | https://doi.org/10.1007/s00148-025-01114-2; https://doi.org/10.1016/j.euroecorev.2025.105026; https://doi.org/10.1371/journal.pone.0349829 |
| `notice_doi` | string | Normalized DOI of the retraction notice. | 0 | 10.1007/s00148-025-01114-2; 10.1016/j.euroecorev.2025.105026; 10.1371/journal.pone.0349829 |
| `record_id` | string | Retraction Watch database record ID. | 0 | 63183; 70777; 70932 |
| `dataset_url` | string | Public dataset supplying the dated retraction record. | 0 | 1 distinct nonmissing values |

## retrieval.csv

One row: catalog source retrieval. Rows: 714. Key: source_id. Producer: `i4r_sources fetch`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 714 distinct nonmissing values |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | failed; non_osf_landing; retrieved |
| `detail` | string | Retrieval error or diagnostic detail; empty for successful retrieval. | 638 | HTTP Error 401: Unauthorized; HTTP Error 404: Not Found; HTTP Error 429: Too Many Requests; unknown url type: '' |

## risk_set_retrieval.csv

One row: event control-pool retrieval. Rows: 3. Key: event_id. Producer: `i4r_citations candidates`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 | dp_020_disclosure; dp_021_disclosure; dp_294_disclosure |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | 2 distinct nonmissing values |
| `candidates` | integer | Number of raw works returned by a complete journal/type/cohort risk-set query. | 0 | 0 to 0 |
| `query_filter` | string | Exact OpenAlex risk-set filter; must agree with current treated metadata before matching. | 2 | 1 distinct nonmissing values |

## sensitivity_panel.csv

One row: article-period in a sensitivity stack. Rows: 0. Key: stack_id, article_id, post. Producer: `i4r_match`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `specification` | string | Named sensitivity comparison; see design and construction ledger. | 0 |  |
| `stack_id` | string | Identifier for a matched event/horizon or sensitivity comparison. | 0 |  |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 |  |
| `warning_id` | string | Shared disclosure identifier for dependence when one warning affects multiple articles. | 0 |  |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 |  |
| `horizon` | integer | Full calendar years after disclosure, primary 1; secondary 2 and 3. | 0 |  |
| `treated` | integer | 1 for affected original article; 0 for matched control. | 0 |  |
| `post` | integer | 1 for after period, 0 for before period; placebo period coding follows comparison order. | 0 |  |
| `weight` | number | Treated article weight 1; selected controls total 1 per stack. | 0 |  |
| `citations` | number | Deduplicated citing journal articles/reviews; sensitivity averages may be fractional. | 0 |  |

## source_articles.csv

One row: source–article relationship. Rows: 723. Key: source_id, article_id. Producer: `i4r_registry build`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 549 distinct nonmissing values |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 436 distinct nonmissing values |
| `relation` | string | Meaning of a source-to-source or source-to-article relationship. | 0 | assessed_article_roster; assesses_or_responds_to; curated_error_evidence; linked_assessment_or_reply; roster_linked_report_or_reply |
| `evidence` | string | Source pointer or documented identity/link decision. | 1 | 43 distinct nonmissing values |

## source_links.csv

One row: explicit external source link. Rows: 368. Key: no unique key declared. Producer: `i4r_sources inventory`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 206 distinct nonmissing values |
| `url` | string | Source or download URL; no authentication credentials. | 0 | 217 distinct nonmissing values |
| `related_source_id` | string | Explicitly linked discussion-paper ID; empty for other external links. | 295 | 73 distinct nonmissing values |
| `relation` | string | Meaning of a source-to-source or source-to-article relationship. | 0 | explicit_link_in_OSF_description |

## source_manifest.csv

One row: cached response. Rows: 1768. Key: path. Producer: `i4r_sources manifest`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `path` | string | Repository-relative cache path; private raw contents are not redistributed. | 0 | 1768 distinct nonmissing values |
| `url` | string | Source or download URL; no authentication credentials. | 0 | 1755 distinct nonmissing values |
| `retrieved_at` | string | UTC retrieval timestamp from cached response provenance. | 0 | 1768 distinct nonmissing values |
| `sha256` | string | SHA-256 content checksum of retrieved bytes. | 0 | 1705 distinct nonmissing values |
| `bytes` | integer | Response size in bytes. | 0 | 129 to 1.09075e+08 |

## source_metadata.csv

One row: source metadata. Rows: 714. Key: source_id. Producer: `i4r_sources inventory`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 714 distinct nonmissing values |
| `stated_date` | string | Date recorded by source provider, with meaning in date_meaning. | 91 | 297 distinct nonmissing values |
| `date_meaning` | string | Explicit interpretation of the accompanying source timestamp. | 91 | OSF node creation; not established public disclosure; RePEc current record publication date; first disclosure unverified |
| `original_title_hint` | string | Catalog-supplied original title; an identity hint. | 422 | 292 distinct nonmissing values |

## source_reviews.csv

One row: source reading/disposition. Rows: 714. Key: source_id. Producer: `i4r_registry build`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 714 distinct nonmissing values |
| `review_status` | string | Depth/disposition of source reading; not a verified error label. | 0 | 16 distinct nonmissing values |
| `classification` | string | Reviewer classification or candidate description; unresolved is not a negative finding. | 0 | 52 distinct nonmissing values |
| `target_title` | string | Reviewer-identified original-paper title, pending identity resolution. | 242 | 433 distinct nonmissing values |
| `target_doi` | string | Reviewer-identified original-paper DOI. | 680 | 33 distinct nonmissing values |
| `evidence_summary` | string | Paraphrased evidence supporting a candidate assessment, including limitations. | 20 | 496 distinct nonmissing values |
| `evidence_pages` | string | Source-reader locations; preserve stated PDF/printed page distinction. | 224 | 170 distinct nonmissing values |
| `review_scope` | string | Reviewer limitations and what was examined. | 0 | 37 distinct nonmissing values |
| `related_sources` | string | Semicolon-separated linked source IDs or reviewer cross-references. | 499 | 198 distinct nonmissing values |
| `assessment_eligibility` | string | yes/no/unresolved: whether the source is an eligible article-specific assessment for the coverage denominator. | 0 | unresolved |
| `assessment_resolved` | string | yes/no: explicit final adjudication for the coverage gate; default no. | 0 | no |

## sources.csv

One row: catalog listing. Rows: 714. Key: source_id. Producer: `i4r_sources discover`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 714 distinct nonmissing values |
| `collection` | string | Catalog class: reports or discussion_papers. | 0 | discussion_papers; reports |
| `catalog_url` | string | Catalog page establishing inclusion in the inventory. | 0 | https://ideas.repec.org/s/zbw/i4rdps.html; https://www.i4replication.org/papers; https://www.i4replication.org/reports |
| `url` | string | Source or download URL; no authentication credentials. | 1 | 695 distinct nonmissing values |
| `title` | string | Catalog or bibliographic title; candidate titles may remain unresolved. | 0 | 714 distinct nonmissing values |
| `authors` | string | Author text supplied by catalog. | 421 | 275 distinct nonmissing values |
| `journal` | string | Journal name from catalog or verified metadata. | 331 | 16 distinct nonmissing values |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | Completed; listed |

## verified_metadata.csv

One row: verified bibliographic identity. Rows: 192. Key: article_id. Producer: `i4r_registry build --refresh-metadata`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 192 distinct nonmissing values |
| `title` | string | Catalog or bibliographic title; candidate titles may remain unresolved. | 0 | 192 distinct nonmissing values |
| `doi` | string | Normalized original-article DOI; empty if unresolved. | 0 | 192 distinct nonmissing values |
| `openalex_id` | string | Full OpenAlex work URL for resolved identity. | 182 | https://openalex.org/W2618893046; https://openalex.org/W2735584017; https://openalex.org/W2738960030; https://openalex.org/W2783385777; https://openalex.org/W3124366560; https://openalex.org/W3198801792; https://openalex.org/W3203294756; https://openalex.org/W4283645972; https://openalex.org/W4283722583; https://openalex.org/W4392104295 |
| `journal` | string | Journal name from catalog or verified metadata. | 0 | 22 distinct nonmissing values |
| `journal_id` | string | OpenAlex journal/source URL used for exact journal matching. | 182 | https://openalex.org/S23254222; https://openalex.org/S2764866340; https://openalex.org/S42893225; https://openalex.org/S45992627; https://openalex.org/S88935262; https://openalex.org/S95323914 |
| `publication_date` | string | Earliest indexed original publication date; ISO year, month or day precision retained. | 0 | 129 distinct nonmissing values |
| `publication_year` | integer | Calendar year of original publication. | 0 | 2001 to 2026 |
| `type` | string | OpenAlex-compatible document type; primary outcomes count article and review. | 0 | article |
| `abstract` | string | Original-article abstract text where supplied by OpenAlex; blank uses title-only matching. | 183 | 9 distinct nonmissing values |
| `identity_verified` | string | yes only after accepted bibliographic match; pending otherwise. | 0 | yes |
| `retracted` | string | Current indexed retraction flag: yes, no or unknown; not a historical treatment indicator. | 0 | no; unknown; yes |
| `retraction_date` | string | Earliest known retraction date from dated notice ledger. | 192 |  |
| `retraction_source` | string | Notice URL establishing retraction date. | 192 |  |
| `metadata_source` | string | URL of accepted bibliographic lookup. | 0 | 192 distinct nonmissing values |
| `metadata_sha256` | string | Checksum of the raw accepted bibliographic response. | 0 | 192 distinct nonmissing values |
| `retrieved_at` | string | UTC retrieval timestamp from cached response provenance. | 0 | 192 distinct nonmissing values |
