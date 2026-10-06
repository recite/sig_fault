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

## archive_members.csv

One row: member within a retrieved ZIP archive. Rows: 3952. Key: member_id. Producer: `scripts/i4r_sources.py archives`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 57 distinct nonmissing values |
| `archive_document_id` | string | Parent ZIP document identifier in documents.csv. | 0 | 62 distinct nonmissing values |
| `member_id` | string | Archive document ID plus hash of member index and original member path; repeated member names remain distinct. | 0 | 3952 distinct nonmissing values |
| `member_path` | string | Original internal archive path, retained as evidence; never used as an extraction destination. | 0 | 3951 distinct nonmissing values |
| `format` | string | Filename-derived document format; unknown when not inferred. | 145 | 67 distinct nonmissing values |
| `uncompressed_bytes` | integer | Uncompressed archive member size from ZIP central directory. | 0 | 0 to 3.89502e+09 |
| `crc32` | string | ZIP member CRC32, retained as eight hexadecimal characters. | 0 | 3344 distinct nonmissing values |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | 7 distinct nonmissing values |
| `local_path` | string | Repository-relative ignored-cache path for a successfully extracted archive member; path is content-independent and does not trust the internal ZIP path. | 3496 | 456 distinct nonmissing values |
| `sha256` | string | SHA-256 content checksum of retrieved bytes. | 3496 | 431 distinct nonmissing values |
| `archive_sha256` | string | SHA-256 of parent archive bytes, tying member extraction to the cached source. | 0 | 62 distinct nonmissing values |

## archive_retrieval.csv

One row: ZIP acquisition/inventory attempt. Rows: 62. Key: archive_document_id. Producer: `scripts/i4r_sources.py archives`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `archive_document_id` | string | Parent ZIP document identifier in documents.csv. | 0 | 62 distinct nonmissing values |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | inventoried |
| `detail` | string | Retrieval error or diagnostic detail; empty for successful retrieval. | 62 |  |
| `members` | integer | Number of inventoried non-directory archive members; zero if archive acquisition or parsing incomplete. | 0 | 2 to 407 |

## article_aliases.csv

One row: superseded article ID. Rows: 6. Key: alias. Producer: `i4r_registry build`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `alias` | string | Superseded title-derived ID mapping to canonical article_id. | 0 | i4r_1ba6b15fcc8cd9; i4r_3105fba3e9d050; i4r_975b8fb7dcee2d; i4r_a92040849a75db; i4r_bdbd4c55c23f42; i4r_ed0c323ab14dc4 |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | i4r_093bc85ab4502e; i4r_1e972a57ca9cf5; i4r_3b074ab4b2ae3d |

## articles.csv

One row: candidate original article. Rows: 517. Key: article_id. Producer: `i4r_registry build`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 517 distinct nonmissing values |
| `title` | string | Catalog or bibliographic title; candidate titles may remain unresolved. | 0 | 517 distinct nonmissing values |
| `doi` | string | Normalized original-article DOI; empty if unresolved. | 59 | 458 distinct nonmissing values |
| `openalex_id` | string | Full OpenAlex work URL for resolved identity. | 134 | 383 distinct nonmissing values |
| `journal` | string | Journal name from catalog or verified metadata. | 26 | 71 distinct nonmissing values |
| `journal_id` | string | OpenAlex journal/source URL used for exact journal matching. | 134 | 26 distinct nonmissing values |
| `publication_date` | string | Earliest publication date reported in the accepted Crossref record; may be later than online-first. Conservative age gate; no outcome-derived dates. | 59 | 315 distinct nonmissing values |
| `publication_year` | integer | Calendar year of original publication. | 59 | 2001 to 2026 |
| `indexed_publication_date` | string | OpenAlex indexed original-publication date, preserved separately from publisher metadata. | 134 | 282 distinct nonmissing values |
| `indexed_publication_year` | integer | OpenAlex publication year used symmetrically for treated/control cohort retrieval and matching. | 134 | 2001 to 2026 |
| `publication_date_source` | string | Publisher metadata URL supporting the conservative article-age date; empty when unresolved. | 59 | 458 distinct nonmissing values |
| `type` | string | OpenAlex-compatible document type; primary outcomes count article and review. | 59 | article; review |
| `abstract` | string | Original-article abstract text where supplied by OpenAlex; blank uses title-only matching. | 195 | 322 distinct nonmissing values |
| `identity_verified` | string | yes only after accepted bibliographic match; pending otherwise. | 0 | pending; yes |
| `retracted` | string | Current indexed retraction flag: yes, no or unknown; not a historical treatment indicator. | 0 | no; unknown; yes |
| `retraction_date` | string | Earliest known retraction date from dated notice ledger. | 513 | 2025-04-06; 2025-06-24; 2026-01-08; 2026-05-21 |
| `retraction_source` | string | Notice URL establishing retraction date. | 513 | https://doi.org/10.1007/s00148-025-01114-2; https://doi.org/10.1016/j.euroecorev.2025.105026; https://doi.org/10.1371/journal.pone.0349829; https://www.nature.com/articles/s41562-025-02393-1 |

## assessment_documents.csv

One row: document and its role in an independent assessment. Rows: 707. Key: unit_id, document_id. Producer: `scripts/i4r_registry.py build`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `unit_id` | string | Stable independent assessment identifier: one reviewer team assessing one original article; distinct from a claim-level assessment_id. | 0 | 500 distinct nonmissing values |
| `document_id` | string | Identifier for a source-linked file; duplicate contents can have different IDs. | 0 | 650 distinct nonmissing values |
| `document_role` | string | Role of document for this assessment: report, version, plan, response, or identified retrieval alias. | 0 | 22 distinct nonmissing values |

## assessment_inventory.csv

One row: independently enumerated reviewer-team assessment of one original article. Rows: 500. Key: unit_id. Producer: `scripts/i4r_registry.py build`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `unit_id` | string | Stable independent assessment identifier: one reviewer team assessing one original article; distinct from a claim-level assessment_id. | 0 | 500 distinct nonmissing values |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 478 distinct nonmissing values |
| `reviewer_team` | string | Semicolon-separated assessment authors, read from the report. | 37 | 381 distinct nonmissing values |
| `reviewer_team_identification` | string | named or not_reported; missing bylines do not erase an observed article assessment. | 0 | named; not_reported |
| `unit_equivalence` | string | verified or unresolved; unidentified report authors prevent treating a potentially revised or duplicate assessment as a confirmed independent team. | 0 | unresolved; verified |
| `assessment_eligibility` | string | yes/no/unresolved: whether the source is an eligible article-specific assessment for the coverage denominator. | 0 | yes |
| `assessment_resolved` | string | yes/no: explicit final adjudication for the coverage gate; default no. | 0 | no; yes |
| `disposition` | string | Adjudicated source-assessment category; empty if unresolved. | 0 | 59 distinct nonmissing values |
| `evidence_summary` | string | Paraphrased evidence supporting a candidate assessment, including limitations. | 0 | 457 distinct nonmissing values |
| `evidence_locator` | string | Public source and page/table/section identifying the error and consequence. | 0 | 472 distinct nonmissing values |
| `limitations` | string | Scope limits of the source adjudication. | 0 | 42 distinct nonmissing values |

## assessment_scope.csv

One row: catalog source with reviewed independent-assessment enumeration status; pending sources retained. Rows: 714. Key: source_id. Producer: `scripts/i4r_registry.py from assessment_scope.json`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 714 distinct nonmissing values |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | fully_enumerated; non_assessment; supporting_document; unresolved |
| `unit_ids` | string | Semicolon-separated independent assessment IDs whose source linkage has been verified; empty for non-assessment or unenumerated sources. | 122 | 438 distinct nonmissing values |
| `evidence` | string | Source pointer or documented identity/link decision. | 0 | 478 distinct nonmissing values |
| `limitations` | string | Scope limits of the source adjudication. | 44 | 36 distinct nonmissing values |

## assessment_sources.csv

One row: assessment-to-catalog-source relation. Rows: 695. Key: unit_id, source_id, relation. Producer: `scripts/i4r_registry.py build`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `unit_id` | string | Stable independent assessment identifier: one reviewer team assessing one original article; distinct from a claim-level assessment_id. | 0 | 500 distinct nonmissing values |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 592 distinct nonmissing values |
| `relation` | string | Meaning of a source-to-source or source-to-article relationship. | 0 | aggregate_context; assessment_source; misdirected_catalog_attachment; supporting_response; verified_retrieval_alias |

## assessments.csv

One row: candidate significant-error assessment. Rows: 37. Key: assessment_id. Producer: `i4r_registry build`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `assessment_id` | string | Identifier for a particular article-specific error assessment. | 0 | 37 distinct nonmissing values |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 37 distinct nonmissing values |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 37 distinct nonmissing values |
| `category` | string | Type of error or broader concern; primary cohort requires demonstrated material error. | 0 | demonstrated_material_error; design_and_data_inconsistency_requires_adjudication; verified_error_materiality_unresolved; verified_limited_error |
| `material` | string | yes/no/unresolved: whether the documented error materially changes a substantive finding. | 0 | no; unresolved; yes |
| `error_verified` | string | yes, pending_second_review or unresolved; only yes enters verified-error cohort. | 0 | unresolved; yes |
| `affected_claim` | string | Substantive result affected; does not imply every finding in the article fails. | 0 | 37 distinct nonmissing values |
| `evidence_summary` | string | Paraphrased evidence supporting a candidate assessment, including limitations. | 0 | 37 distinct nonmissing values |
| `evidence_locator` | string | Public source and page/table/section identifying the error and consequence. | 0 | 37 distinct nonmissing values |
| `dispute_status` | string | Author acknowledgment, response, dispute or unresolved status. | 0 | 17 distinct nonmissing values |
| `verification_scope` | string | Evidence actually checked; source verification is distinct from re-running code. | 0 | 12 distinct nonmissing values |
| `public_year` | integer | Known public assessment year for time-aware control exclusions. | 1 | 2020 to 2026 |

## citation_edges.csv

One row: deduplicated original–citing article pair. Rows: 32069. Key: article_id, citing_work_id. Producer: `i4r_citations fetch`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 416 distinct nonmissing values |
| `citing_work_id` | string | OpenAlex work ID of the citing publication. | 0 | 28253 distinct nonmissing values |
| `citing_doi` | string | Normalized DOI of the citing publication; absent uses work ID for deduplication. | 105 | 28154 distinct nonmissing values |
| `publication_year` | integer | Calendar year of original publication. | 0 | 2017 to 2025 |
| `publication_date` | string | Earliest publication date reported in the accepted Crossref record; may be later than online-first. Conservative age gate; no outcome-derived dates. | 0 | 2966 distinct nonmissing values |
| `type` | string | OpenAlex-compatible document type; primary outcomes count article and review. | 0 | article; review |

## citation_retrieval.csv

One row: original article citation retrieval. Rows: 437. Key: article_id. Producer: `i4r_citations fetch`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 437 distinct nonmissing values |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | complete; incomplete; unresolved_identity |
| `detail` | string | Retrieval error or diagnostic detail; empty for successful retrieval. | 435 | HTTP Error 429: Too Many Requests; The read operation timed out |

## citations.csv

One row: original article–calendar-year. Rows: 2956. Key: article_id, year. Producer: `i4r_citations fetch`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 422 distinct nonmissing values |
| `year` | integer | Public disclosure year in events; observed citation year in citation/panel tables. | 0 | 2017 to 2025 |
| `citations` | number | Deduplicated citing journal articles/reviews; sensitivity averages may be fractional. | 0 | 0 to 882 |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | complete |

## control_aliases.csv

One row: known indexed control-work alias. Rows: 1022. Key: alias_openalex_id. Producer: `i4r_citations candidates`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `alias_openalex_id` | string | Known OpenAlex work alias of a canonical control article; incoming edges are combined across aliases. | 0 | 1022 distinct nonmissing values |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 1022 distinct nonmissing values |

## control_articles.csv

One row: external control candidate. Rows: 1022. Key: article_id. Producer: `i4r_citations candidates/retractions`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 1022 distinct nonmissing values |
| `title` | string | Catalog or bibliographic title; candidate titles may remain unresolved. | 0 | 1011 distinct nonmissing values |
| `doi` | string | Normalized original-article DOI; empty if unresolved. | 8 | 1014 distinct nonmissing values |
| `openalex_id` | string | Full OpenAlex work URL for resolved identity. | 0 | 1022 distinct nonmissing values |
| `journal` | string | Journal name from catalog or verified metadata. | 0 | American Economic Journal Applied Economics; American Economic Review; The Economic Journal |
| `journal_id` | string | OpenAlex journal/source URL used for exact journal matching. | 0 | https://openalex.org/S23254222; https://openalex.org/S42893225; https://openalex.org/S45992627 |
| `publication_date` | string | Earliest publication date reported in the accepted Crossref record; may be later than online-first. Conservative age gate; no outcome-derived dates. | 22 | 185 distinct nonmissing values |
| `publication_year` | integer | Calendar year of original publication. | 22 | 2012 to 2026 |
| `indexed_publication_date` | string | OpenAlex indexed original-publication date, preserved separately from publisher metadata. | 0 | 156 distinct nonmissing values |
| `indexed_publication_year` | integer | OpenAlex publication year used symmetrically for treated/control cohort retrieval and matching. | 0 | 2012 to 2022 |
| `publication_date_source` | string | Publisher metadata URL supporting the conservative article-age date; empty when unresolved. | 22 | 1000 distinct nonmissing values |
| `type` | string | OpenAlex-compatible document type; primary outcomes count article and review. | 0 | article |
| `abstract` | string | Original-article abstract text where supplied by OpenAlex; blank uses title-only matching. | 26 | 990 distinct nonmissing values |
| `identity_verified` | string | yes only after accepted bibliographic match; pending otherwise. | 0 | yes |
| `retracted` | string | Current indexed retraction flag: yes, no or unknown; not a historical treatment indicator. | 0 | no; yes |
| `retraction_date` | string | Earliest known retraction date from dated notice ledger. | 1021 | 2023-07-01 |
| `retraction_source` | string | Notice URL establishing retraction date. | 1021 | https://doi.org/10.1257/aer.113.7.2053 |

## control_exclusions.csv

One row: verified control-publication exclusion. Rows: 44. Key: article_id. Producer: `manual publication-genre and identity review`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 44 distinct nonmissing values |
| `title` | string | Catalog or bibliographic title; candidate titles may remain unresolved. | 0 | 42 distinct nonmissing values |
| `doi` | string | Normalized original-article DOI; empty if unresolved. | 0 | 44 distinct nonmissing values |
| `reason` | string | Explicit exclusion reason; blank if eligible. | 0 | assessment_or_reply; historical_republication; nonresearch_publication |
| `evidence` | string | Source pointer or documented identity/link decision. | 0 | 44 distinct nonmissing values |
| `source_url` | string | Public evidence or notice URL. | 0 | 44 distinct nonmissing values |

## control_metadata_provenance.csv

One row: accepted control publisher-metadata response. Rows: 1000. Key: article_id, provider. Producer: `i4r_citations control-metadata`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 1000 distinct nonmissing values |
| `provider` | string | Accepted bibliographic provider: crossref or openalex. | 0 | crossref |
| `path` | string | Repository-relative cache path; private raw contents are not redistributed. | 0 | 1000 distinct nonmissing values |
| `url` | string | Source or download URL; no authentication credentials. | 0 | 1000 distinct nonmissing values |
| `sha256` | string | SHA-256 content checksum of retrieved bytes. | 0 | 1000 distinct nonmissing values |
| `retrieved_at` | string | UTC retrieval timestamp from cached response provenance. | 0 | 1000 distinct nonmissing values |

## control_metadata_retrieval.csv

One row: control publisher-metadata retrieval. Rows: 1022. Key: article_id. Producer: `i4r_citations control-metadata`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 1022 distinct nonmissing values |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | HTTP Error 404: Not Found; no_doi; publisher_identity_mismatch; retrieved |

## crossref_retrieval.csv

One row: publisher lookup. Rows: 517. Key: article_id. Producer: `i4r_registry crossref`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 517 distinct nonmissing values |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | exact_title_resolved; no_unambiguous_exact_title_match; retrieved |

## curated_claims.csv

One row: adjudicated candidate claim/disclosure. Rows: 37. Key: assessment_id. Producer: `manual evidence review`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `title` | string | Catalog or bibliographic title; candidate titles may remain unresolved. | 0 | 37 distinct nonmissing values |
| `doi` | string | Normalized original-article DOI; empty if unresolved. | 0 | 37 distinct nonmissing values |
| `assessment_id` | string | Identifier for a particular article-specific error assessment. | 0 | 37 distinct nonmissing values |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 37 distinct nonmissing values |
| `category` | string | Type of error or broader concern; primary cohort requires demonstrated material error. | 0 | demonstrated_material_error; design_and_data_inconsistency_requires_adjudication; verified_error_materiality_unresolved; verified_limited_error |
| `material` | string | yes/no/unresolved: whether the documented error materially changes a substantive finding. | 0 | no; unresolved; yes |
| `error_verified` | string | yes, pending_second_review or unresolved; only yes enters verified-error cohort. | 0 | unresolved; yes |
| `affected_claim` | string | Substantive result affected; does not imply every finding in the article fails. | 0 | 37 distinct nonmissing values |
| `evidence_summary` | string | Paraphrased evidence supporting a candidate assessment, including limitations. | 0 | 37 distinct nonmissing values |
| `evidence_locator` | string | Public source and page/table/section identifying the error and consequence. | 0 | 37 distinct nonmissing values |
| `dispute_status` | string | Author acknowledgment, response, dispute or unresolved status. | 0 | 17 distinct nonmissing values |
| `verification_scope` | string | Evidence actually checked; source verification is distinct from re-running code. | 0 | 12 distinct nonmissing values |
| `public_year` | integer | Known public assessment year for time-aware control exclusions. | 25 | 2023 to 2025 |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 | 37 distinct nonmissing values |
| `warning_id` | string | Shared disclosure identifier for dependence when one warning affects multiple articles. | 0 | 37 distinct nonmissing values |
| `date` | string | Disclosure date in events/claims, retraction date in retractions; blank when exact day unknown. | 11 | 24 distinct nonmissing values |
| `year` | integer | Public disclosure year in events; observed citation year in citation/panel tables. | 1 | 2020 to 2026 |
| `date_precision` | string | day/month/year: precision supported by public evidence. | 0 | day; month; unknown; year |
| `publicity_verified` | string | yes only when public timing has a documented source. | 0 | no; yes |
| `date_evidence_url` | string | Public evidence establishing disclosure timing. | 0 | 37 distinct nonmissing values |
| `date_evidence` | string | Reasoning for earliest substantiated public year/day and unresolved earlier versions. | 0 | 37 distinct nonmissing values |
| `already_retracted` | string | Retraction status at disclosure: no required for primary cohort. | 0 | no; unknown |

## document_retrieval.csv

One row: file retrieval. Rows: 1514. Key: document_id. Producer: `i4r_sources documents`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `document_id` | string | Identifier for a source-linked file; duplicate contents can have different IDs. | 0 | 1514 distinct nonmissing values |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | retrieved |
| `detail` | string | Retrieval error or diagnostic detail; empty for successful retrieval. | 1514 |  |
| `sha256` | string | SHA-256 content checksum of retrieved bytes. | 0 | 767 distinct nonmissing values |

## documents.csv

One row: source-linked file. Rows: 2116. Key: document_id. Producer: `i4r_sources inventory`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 649 distinct nonmissing values |
| `document_id` | string | Identifier for a source-linked file; duplicate contents can have different IDs. | 0 | 2116 distinct nonmissing values |
| `name` | string | Source-provided document filename or linked_fulltext placeholder. | 0 | 509 distinct nonmissing values |
| `url` | string | Source or download URL; no authentication credentials. | 0 | 904 distinct nonmissing values |
| `format` | string | Filename-derived document format; unknown when not inferred. | 8 | 15 distinct nonmissing values |
| `created_at` | string | Provider creation timestamp; does not establish public disclosure. | 332 | 572 distinct nonmissing values |
| `modified_at` | string | Provider modification timestamp; does not establish public disclosure. | 332 | 572 distinct nonmissing values |
| `date_meaning` | string | Explicit interpretation of the accompanying source timestamp. | 0 | File upload/modification, not established public disclosure; No disclosure date inferred from URL; No public disclosure date inferred |

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

One row: candidate error disclosure. Rows: 37. Key: event_id. Producer: `i4r_registry build`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 | 37 distinct nonmissing values |
| `warning_id` | string | Shared disclosure identifier for dependence when one warning affects multiple articles. | 0 | 37 distinct nonmissing values |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 37 distinct nonmissing values |
| `assessment_id` | string | Identifier for a particular article-specific error assessment. | 0 | 37 distinct nonmissing values |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 37 distinct nonmissing values |
| `date` | string | Disclosure date in events/claims, retraction date in retractions; blank when exact day unknown. | 11 | 24 distinct nonmissing values |
| `year` | integer | Public disclosure year in events; observed citation year in citation/panel tables. | 1 | 2020 to 2026 |
| `date_precision` | string | day/month/year: precision supported by public evidence. | 0 | day; month; unknown; year |
| `publicity_verified` | string | yes only when public timing has a documented source. | 0 | no; yes |
| `date_evidence_url` | string | Public evidence establishing disclosure timing. | 0 | 37 distinct nonmissing values |
| `date_evidence` | string | Reasoning for earliest substantiated public year/day and unresolved earlier versions. | 0 | 37 distinct nonmissing values |
| `error_verified` | string | yes, pending_second_review or unresolved; only yes enters verified-error cohort. | 0 | unresolved; yes |
| `material` | string | yes/no/unresolved: whether the documented error materially changes a substantive finding. | 0 | no; unresolved; yes |
| `already_retracted` | string | Retraction status at disclosure: no required for primary cohort. | 0 | no; unknown |

## identity_decisions.csv

One row: clerical identity decision. Rows: 2. Key: article_id. Producer: `manual evidence review`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | i4r_20d617740fb019; i4r_40fdc820b2481c |
| `title` | string | Catalog or bibliographic title; candidate titles may remain unresolved. | 0 | Disloyal Managers and Shareholders’ Wealth; Peer Effects in Academic Research: Senders and Receivers |
| `doi` | string | Normalized original-article DOI; empty if unresolved. | 0 | 10.1093/ej/ueac031; 10.1093/rfs/hhac070 |
| `evidence` | string | Source pointer or documented identity/link decision. | 0 | 2 distinct nonmissing values |
| `source_url` | string | Public evidence or notice URL. | 0 | https://api.crossref.org/works/10.1093/ej/ueac031; https://api.crossref.org/works/10.1093/rfs/hhac070 |

## identity_resolution.csv

One row: OpenAlex resolution attempt. Rows: 385. Key: article_id. Producer: `i4r_registry resolve`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 385 distinct nonmissing values |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | doi_resolved |
| `detail` | string | Retrieval error or diagnostic detail; empty for successful retrieval. | 385 |  |

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

One row: screened event–control–horizon. Rows: 1323. Key: event_id, control_id, horizon. Producer: `i4r_match`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 | dp_021_disclosure; dp_148_disclosure; dp_292_disclosure; dp_294_disclosure |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | i4r_19321c88424658; i4r_55d334eaeb4010; i4r_ece0397b04bfa9; i4r_f45e09f5bc283f |
| `control_id` | string | Original control-article ID retained across reused matches. | 0 | 687 distinct nonmissing values |
| `distance` | number | Standardized pre-citation and text matching distance; no post outcomes used. | 1323 |  |
| `eligible` | string | yes/no after metadata, age, exposure and citation-caliper gates. | 0 | no |
| `reason` | string | Explicit exclusion reason; blank if eligible. | 0 | assessment_or_reply; historical_republication; incomplete_pre_citations; insufficient_article_age; known_retraction_in_window; nonresearch_publication |
| `horizon` | integer | Full calendar years after disclosure, primary 1; secondary 2 and 3. | 0 | 1 to 3 |

## match_exclusions.csv

One row: excluded event–horizon. Rows: 111. Key: event_id, horizon. Producer: `i4r_match`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 | 37 distinct nonmissing values |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 37 distinct nonmissing values |
| `reason` | string | Explicit exclusion reason; blank if eligible. | 0 | error_not_verified_material; incomplete_control_citation_retrieval; incomplete_followup; incomplete_risk_set_retrieval; insufficient_article_age; publicity_unverified; retraction_status_not_eligible |
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

One row: accepted bibliographic provider response for an identity. Rows: 843. Key: article_id, provider. Producer: `i4r_registry build --refresh-metadata`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 460 distinct nonmissing values |
| `provider` | string | Accepted bibliographic provider: crossref or openalex. | 0 | crossref; openalex |
| `path` | string | Repository-relative cache path; private raw contents are not redistributed. | 0 | 843 distinct nonmissing values |
| `url` | string | Source or download URL; no authentication credentials. | 0 | 841 distinct nonmissing values |
| `sha256` | string | SHA-256 content checksum of retrieved bytes. | 0 | 841 distinct nonmissing values |
| `retrieved_at` | string | UTC retrieval timestamp from cached response provenance. | 0 | 843 distinct nonmissing values |

## panel_exclusions.csv

One row: incomplete event–horizon. Rows: 0. Key: event_id, horizon. Producer: `i4r_match`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 |  |
| `horizon` | integer | Full calendar years after disclosure, primary 1; secondary 2 and 3. | 0 |  |
| `reason` | string | Explicit exclusion reason; blank if eligible. | 0 |  |

## repository_documents.csv

One row: file reached through child components or storage-provider traversal. Rows: 1784. Key: document_id. Producer: `scripts/i4r_sources.py expand`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 317 distinct nonmissing values |
| `document_id` | string | Identifier for a source-linked file; duplicate contents can have different IDs. | 0 | 1784 distinct nonmissing values |
| `name` | string | Source-provided document filename or linked_fulltext placeholder. | 0 | 507 distinct nonmissing values |
| `url` | string | Source or download URL; no authentication credentials. | 0 | 572 distinct nonmissing values |
| `format` | string | Filename-derived document format; unknown when not inferred. | 8 | 15 distinct nonmissing values |
| `created_at` | string | Provider creation timestamp; does not establish public disclosure. | 0 | 572 distinct nonmissing values |
| `modified_at` | string | Provider modification timestamp; does not establish public disclosure. | 0 | 572 distinct nonmissing values |
| `date_meaning` | string | Explicit interpretation of the accompanying source timestamp. | 0 | Repository upload/modification; not established public disclosure |

## repository_queries.csv

One row: repository relationship page acquisition per catalog source. Rows: 1218. Key: source_id, url. Producer: `scripts/i4r_sources.py expand`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 378 distinct nonmissing values |
| `url` | string | Source or download URL; no authentication credentials. | 0 | 1092 distinct nonmissing values |
| `query_kind` | string | OSF relationship traversal: storage providers, files, or child components. | 0 | children; files; providers |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | failed; retrieved |
| `items` | integer | Number of objects returned by a successful repository relationship page; zero on failure is not evidence of empty contents. | 0 | 0 to 34 |
| `detail` | string | Retrieval error or diagnostic detail; empty for successful retrieval. | 1214 | HTTP Error 401: Unauthorized |

## retractions.csv

One row: retraction notice. Rows: 5. Key: record_id. Producer: `i4r_citations retractions`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `doi` | string | Normalized original-article DOI; empty if unresolved. | 0 | 10.1007/s00148-024-00984-2; 10.1016/j.euroecorev.2018.09.008; 10.1038/s41562-023-01695-6; 10.1257/aer.20210369; 10.1371/journal.pone.0255392 |
| `date` | string | Disclosure date in events/claims, retraction date in retractions; blank when exact day unknown. | 0 | 2023-07-01; 2025-04-06; 2025-06-24; 2026-01-08; 2026-05-21 |
| `source_url` | string | Public evidence or notice URL. | 0 | https://doi.org/10.1007/s00148-025-01114-2; https://doi.org/10.1016/j.euroecorev.2025.105026; https://doi.org/10.1257/aer.113.7.2053; https://doi.org/10.1371/journal.pone.0349829; https://www.nature.com/articles/s41562-025-02393-1 |
| `notice_doi` | string | Normalized DOI of the retraction notice. | 0 | 10.1007/s00148-025-01114-2; 10.1016/j.euroecorev.2025.105026; 10.1038/s41562-025-02393-1; 10.1257/aer.113.7.2053; 10.1371/journal.pone.0349829 |
| `record_id` | string | Retraction Watch database record ID. | 1 | 45874; 63183; 70777; 70932 |
| `dataset_url` | string | Public dataset supplying the dated retraction record. | 0 | 2 distinct nonmissing values |

## retrieval.csv

One row: catalog source retrieval. Rows: 714. Key: source_id. Producer: `i4r_sources fetch`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 714 distinct nonmissing values |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | failed; non_osf_landing; retrieved |
| `detail` | string | Retrieval error or diagnostic detail; empty for successful retrieval. | 708 | HTTP Error 401: Unauthorized; HTTP Error 404: Not Found; unknown url type: '' |

## risk_set_retrieval.csv

One row: event control-pool retrieval. Rows: 6. Key: event_id. Producer: `i4r_citations candidates`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `event_id` | string | Identifier for a candidate particular-error disclosure event. | 0 | dp_020_disclosure; dp_021_disclosure; dp_148_disclosure; dp_292_disclosure; dp_294_disclosure; report_2f792d86ba6c_disclosure |
| `status` | string | Stage-specific observed disposition; see values and the construction contract. | 0 | 2 distinct nonmissing values |
| `candidates` | integer | Number of raw works returned by a complete journal/type/cohort risk-set query. | 0 | 0 to 381 |
| `query_filter` | string | Exact OpenAlex risk-set filter; must agree with current treated metadata before matching. | 1 | 5 distinct nonmissing values |

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

## source_adjudications.csv

One row: independent source eligibility/classification decision. Rows: 714. Key: source_id. Producer: `source evidence adjudication`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 714 distinct nonmissing values |
| `assessment_eligibility` | string | yes/no/unresolved: whether the source is an eligible article-specific assessment for the coverage denominator. | 0 | no; unresolved; yes |
| `assessment_resolved` | string | yes/no: explicit final adjudication for the coverage gate; default no. | 0 | no; yes |
| `canonical_source_id` | string | Canonical catalog source identifying a verified same-assessment version group; otherwise source_id. | 0 | 631 distinct nonmissing values |
| `disposition` | string | Adjudicated source-assessment category; empty if unresolved. | 0 | 92 distinct nonmissing values |
| `evidence` | string | Source pointer or documented identity/link decision. | 7 | 556 distinct nonmissing values |
| `evidence_locator` | string | Public source and page/table/section identifying the error and consequence. | 0 | 542 distinct nonmissing values |
| `limitations` | string | Scope limits of the source adjudication. | 0 | 86 distinct nonmissing values |
| `adjudication_date` | string | Date the source evidence was adjudicated; not public disclosure date. | 0 | 2026-10-05; 2026-10-06 |

## source_articles.csv

One row: source–article relationship. Rows: 1010. Key: source_id, article_id. Producer: `i4r_registry build`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 654 distinct nonmissing values |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 517 distinct nonmissing values |
| `relation` | string | Meaning of a source-to-source or source-to-article relationship. | 0 | assessed_article_roster; catalog_or_review_target_hint; curated_error_evidence; document_verified_assessment_target; linked_assessment_or_reply; misdirected_catalog_attachment; roster_linked_report_or_reply; same_cohort_aggregate_roster |
| `evidence` | string | Source pointer or documented identity/link decision. | 0 | 625 distinct nonmissing values |

## source_links.csv

One row: explicit external source link. Rows: 448. Key: no unique key declared. Producer: `i4r_sources inventory`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 251 distinct nonmissing values |
| `url` | string | Source or download URL; no authentication credentials. | 0 | 258 distinct nonmissing values |
| `related_source_id` | string | Explicitly linked discussion-paper ID; empty for other external links. | 362 | 84 distinct nonmissing values |
| `relation` | string | Meaning of a source-to-source or source-to-article relationship. | 0 | explicit_link_in_OSF_description |

## source_manifest.csv

One row: cached response. Rows: 6396. Key: path. Producer: `i4r_sources manifest`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `path` | string | Repository-relative cache path; private raw contents are not redistributed. | 0 | 6396 distinct nonmissing values |
| `url` | string | Source or download URL; no authentication credentials. | 0 | 5449 distinct nonmissing values |
| `retrieved_at` | string | UTC retrieval timestamp from cached response provenance. | 0 | 5652 distinct nonmissing values |
| `sha256` | string | SHA-256 content checksum of retrieved bytes. | 0 | 5016 distinct nonmissing values |
| `bytes` | integer | Response size in bytes. | 0 | 129 to 2.92204e+09 |

## source_metadata.csv

One row: source metadata. Rows: 714. Key: source_id. Producer: `i4r_sources inventory`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `source_id` | string | Identifier for a catalog listing; not an original article or unique file. | 0 | 714 distinct nonmissing values |
| `stated_date` | string | Date recorded by source provider, with meaning in date_meaning. | 7 | 365 distinct nonmissing values |
| `date_meaning` | string | Explicit interpretation of the accompanying source timestamp. | 7 | OSF node creation; not established public disclosure; RePEc current record publication date; first disclosure unverified |
| `original_title_hint` | string | Catalog-supplied original title; an identity hint. | 338 | 376 distinct nonmissing values |

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
| `assessment_eligibility` | string | yes/no/unresolved: whether the source is an eligible article-specific assessment for the coverage denominator. | 0 | no; unresolved; yes |
| `assessment_resolved` | string | yes/no: explicit final adjudication for the coverage gate; default no. | 0 | no; yes |
| `canonical_source_id` | string | Canonical catalog source identifying a verified same-assessment version group; otherwise source_id. | 0 | 631 distinct nonmissing values |
| `adjudicated_disposition` | string | Independent source-level classification; distinct from verified exposure or paper-wide validity. | 0 | 92 distinct nonmissing values |
| `adjudication_evidence` | string | Evidence supporting source eligibility, classification and any version equivalence. | 7 | 556 distinct nonmissing values |
| `adjudication_locator` | string | Document/page/section references supporting independent source adjudication. | 0 | 542 distinct nonmissing values |
| `adjudication_limitations` | string | Unresolved evidence or limits to source-level adjudication. | 0 | 86 distinct nonmissing values |

## source_units.csv

One row: catalog source-equivalence group, not necessarily one independent article assessment. Rows: 631. Key: canonical_source_id. Producer: `i4r_registry build`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `canonical_source_id` | string | Canonical catalog source identifying a verified same-assessment version group; otherwise source_id. | 0 | 631 distinct nonmissing values |
| `source_ids` | string | Semicolon-separated source listings in a verified version group. | 0 | 631 distinct nonmissing values |
| `catalog_entries` | integer | Number of catalog listings in a source-assessment unit. | 0 | 1 to 3 |
| `assessment_eligibility` | string | yes/no/unresolved: whether the source is an eligible article-specific assessment for the coverage denominator. | 0 | no; unresolved; yes |
| `assessment_resolved` | string | yes/no: explicit final adjudication for the coverage gate; default no. | 0 | no; yes |
| `disposition` | string | Adjudicated source-assessment category; empty if unresolved. | 233 | 61 distinct nonmissing values |
| `adjudication_conflict` | string | yes if resolved reviewers assign inconsistent dispositions to purported versions. | 0 | no |

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

One row: verified bibliographic identity. Rows: 460. Key: article_id. Producer: `i4r_registry build --refresh-metadata`.

| Column | Type | Meaning | Missing | Observed range / values |
| --- | --- | --- | ---: | --- |
| `article_id` | string | Opaque original-article identity; title-derived for registry, OpenAlex ID for controls. | 0 | 460 distinct nonmissing values |
| `title` | string | Catalog or bibliographic title; candidate titles may remain unresolved. | 0 | 460 distinct nonmissing values |
| `doi` | string | Normalized original-article DOI; empty if unresolved. | 0 | 458 distinct nonmissing values |
| `openalex_id` | string | Full OpenAlex work URL for resolved identity. | 77 | 383 distinct nonmissing values |
| `journal` | string | Journal name from catalog or verified metadata. | 0 | 60 distinct nonmissing values |
| `journal_id` | string | OpenAlex journal/source URL used for exact journal matching. | 77 | 26 distinct nonmissing values |
| `publication_date` | string | Earliest publication date reported in the accepted Crossref record; may be later than online-first. Conservative age gate; no outcome-derived dates. | 0 | 315 distinct nonmissing values |
| `publication_year` | integer | Calendar year of original publication. | 0 | 2001 to 2026 |
| `indexed_publication_date` | string | OpenAlex indexed original-publication date, preserved separately from publisher metadata. | 77 | 282 distinct nonmissing values |
| `indexed_publication_year` | integer | OpenAlex publication year used symmetrically for treated/control cohort retrieval and matching. | 77 | 2001 to 2026 |
| `publication_date_source` | string | Publisher metadata URL supporting the conservative article-age date; empty when unresolved. | 0 | 458 distinct nonmissing values |
| `type` | string | OpenAlex-compatible document type; primary outcomes count article and review. | 0 | article; review |
| `abstract` | string | Original-article abstract text where supplied by OpenAlex; blank uses title-only matching. | 138 | 322 distinct nonmissing values |
| `identity_verified` | string | yes only after accepted bibliographic match; pending otherwise. | 0 | yes |
| `retracted` | string | Current indexed retraction flag: yes, no or unknown; not a historical treatment indicator. | 0 | no; unknown; yes |
| `retraction_date` | string | Earliest known retraction date from dated notice ledger. | 460 |  |
| `retraction_source` | string | Notice URL establishing retraction date. | 460 |  |
| `metadata_source` | string | URL of accepted bibliographic lookup. | 0 | 458 distinct nonmissing values |
| `metadata_sha256` | string | Checksum of the raw accepted bibliographic response. | 0 | 458 distinct nonmissing values |
| `retrieved_at` | string | UTC retrieval timestamp from cached response provenance. | 0 | 460 distinct nonmissing values |
