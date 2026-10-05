# Pilot data dictionary and join contract

All CSV files use UTF-8, headers, quoted fields when required, and empty strings for unavailable values. IDs are text; dates use ISO `YYYY-MM-DD`. Blank coding cells are missing judgments. No missing judgment is converted to zero.

| File | Row unit / key | Content and provenance |
| --- | --- | --- |
| `sources/iv_replicate.rds` | Deposited R workspace | Byte-identical CC0 archive file 7527252. Despite its extension, read with `load()`, not `readRDS()`. Object `d` contains 70 designs / 67 papers. |
| `sources/iv_archive.json` | Dataverse version 1 metadata | File IDs, original filenames, checksums, license, release date. |
| `sources/iv_raw/` | Ten selected replication input files | Byte-identical datasets checked against archive MD5 hashes. |
| `source_manifest.csv` | Relative source path | Retrieval URLs, SHA-256 hashes, byte counts, license/provenance. |
| `registry.csv` | `claim_id` | 157 neuroscience article assessments plus 70 IV design assessments. `paper_id` repeats only for multiple IV designs. |
| `iv_diagnostics.csv` | `name` | Deposited diagnostic columns plus explicit screening indicators; produced by `pilot_registry.R`. |
| `identities.csv` | `paper_id` | Twenty checked DOI/title/date/journal/page matches, stable identifiers, decision evidence and discrepancies. |
| `audits.csv` | `audit_id` | Earliest possible and latest verified public-warning dates, journal date, source URL, uncertainty. |
| `claims.csv` | `claim_id` | Claim paraphrase, source locator, assessment, qualifications, assistant check status, independent-reader fields, final status, correction DOI. |
| `iv_specs.json` | `paper_id` | Audited specification transcribed from deposited Rmd: Y, D, Z, controls, clusters, fixed effects, weights and source filename. |
| `iv_verification.csv` | `paper_id` | Independent IV coefficients, sample sizes, excluded-column counts, AR test, joint first-stage F, source comparators and numerical warnings. |
| `iv_encoding_check.csv` | `specification` | Factor-expanded and numeric-code AR calculations for the instrument-encoding discrepancy. |
| `citation_edges.csv` | `paper_id`, `citing_work_id` | Frozen OpenAlex incoming links, article metadata, OA locations, and inclusion dispositions. |
| `coverage.csv` | `paper_id` | API total, fetched pages, completed-frame indicator. A covered zero is distinct from an unfinished request. |
| `duplicate_date_checks.csv` | `paper_id`, `duplicate_work_id` | Same-DOI records with inconsistent dates, retained explicitly for version review. Sampling stops if the dates imply different periods. |
| `sample.csv` | `pair_id` | Frozen sampled relationships, period, stratum size, sample size, conditional inclusion probability and deterministic rank. |
| `retrieval.csv` | `pair_id` | Retrieval status, successful URL, ignored local cache path, hash, failed attempts, check date. |
| `context_index.csv` | `pair_id` | DOI-matched XML reference IDs, passage counts, extraction status, and private passage-file path; no outcome codes. |
| `availability.csv` | `audit`, `period` | Generated retrieval counts by cohort and timing stratum. |
| `coding_template.csv` | `pair_id`, `reader_id` | Blank two-reader forms; copy before editing. |
| `status.json` | One document | Generated counts and explicit pending status; no fabricated outcome estimates. |

`registry.csv` preserves source journal/year labels. `source_locator` is a source page/link for neuroscience and the audited model for IV. `claim_description` is a source-based starting description, not a completed claim verification. `source_assessment` retains source seriousness language or named diagnostic values. `assessment_type` separates reported interaction errors, comparisons not flagged, and diagnostic sensitivity. `selected` is an R logical serialized as `TRUE`/`FALSE`. `screen_positive` determines the IV paper sampling universe; `paper_inclusion_probability` is 10/79 for eligible neuroscience papers and 10/17 for eligible IV papers, zero outside those pools.

`citation_edges.csv` has the following fields: target and citing OpenAlex IDs; normalized citing DOI; title; database publication date and year; OpenAlex document type; `reference_verified=yes` when the API reference list contains the target; JSON list of OA URLs; PMCID when represented in an identifiable URL; `before_original_date`; `duplicate_of`; and `eligible_type`. Here `reference_verified` means graph verification only. `duplicate_of` names the canonical citing OpenAlex ID for the same DOI within a target. Different-DOI versions need human review. DOI normalization strips the DOI resolver prefix and lowercases; it does not perform fuzzy identity matching.

`conditional_inclusion_probability` in the sample equals the sampled count divided by eligible records in that paper-period stratum. Overall relationship inclusion probability also includes the paper selection probability. Treat the two audit populations separately. Sampling equal counts per paper does not itself yield a citation-weighted population estimate. `sample_rank` is the rank of the SHA-256 ordering, not a citation count or assessment of relevance.

Retrieval statuses are `retrieved_xml` (article body present and article-level DOI checked), `downloaded_pdf_unchecked` (PDF bytes retrieved; identity and readability pending), and `unavailable` (not obtained through attempted automated routes; not proof that no copy exists). `attempts` is a JSON array of failures. PDF counts do not automatically satisfy the 80% verified-full-text threshold. Private files may contain complete copyrighted texts; public outputs contain metadata and annotations only.

## Join contract

The selected registry has twenty distinct paper IDs. Joining checked identities is **1:1 at the paper level** and must preserve all twenty, with no unmatched IDs. Claims join **many:1** to identities. A citing work may cite several target papers: expansion to citation relationships is intentional and keyed by the two IDs, never by citing ID alone. API pagination must reproduce the reported total for every target and contain no repeated citing IDs across pages. A duplicate DOI is retained with a disposition, not silently removed from the raw frame. The context sample excludes disposed records and records its denominator before drawing.

Ratings join **many:1** to the frozen sample; each reader may supply only one rating per pair. The validation command rejects unknown pairs, duplicate reader-pair keys, missing evidence for a reliance judgment, and negative qualification codes without full-text review. Full-text and claim availability are reported separately from outcome completion. No join drops inaccessible papers.

## Recodes and limits

The IV weak-F and inferential-sensitivity screens are recruitment rules applied to deposited values. They do not override source data or certify conclusions. Corrections found after sampling are logged in claim records; the draw stays fixed. Article dates come from bibliographic records and need version/submission review before any publicity-effect analysis. Original neuroscience exclusions for broken 2016 citation exports do not automatically exclude those original articles from this new, independently collected frame. Our selected ten happen not to include those records.

The general warning/article-specific exposure distinction, low retrieval coverage, incomplete claim mapping, and absent independent coding are measurable limits of the pilot. The current package cannot support a causal effect of publicity or an estimate of the prevalence of reliance until those tasks are completed.
