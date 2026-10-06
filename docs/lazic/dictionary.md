# Lazic registry dictionary and recodes

One row in `articles.csv` is one assessed paper. `article_id` and `pmid` are unique
text keys. CSV readers must preserve identifiers as strings. Empty cells represent
unavailable metadata or an undefined classification; they never mean zero citations.
The public registry contains no citation outcomes.

| Field | Definition, source and transformation |
| --- | --- |
| `article_id` | Text `lazic_` followed by the source PMID; complete. |
| `pmid` | Unmodified source identifier joined to PubMed; complete. |
| `doi` | Lowercase, normalized PubMed ArticleId DOI; blank for two papers. |
| `title`, `journal` | PubMed article title and journal title; complete; nested title markup flattened. |
| `publication_date` | PubMed electronic publication date when available, otherwise issue date; retaining year/month/day precision. No imputed January 1. This is a metadata rule, not independently verified first availability. |
| `electronic_date` | PubMed ArticleDate with DateType Electronic; blank when absent. |
| `issue_date` | PubMed JournalIssue/PubDate at its reported precision, retained separately even when electronic publication date is known. |
| `publication_year` | Integer year from `publication_date`; complete. |
| `issue_year` | Integer year of PubMed JournalIssue/PubDate, kept separately from online publication; complete. |
| `pmc_id` | PubMed Central identifier(s), semicolon-separated; blank if absent. |
| `publication_types` | PubMed publication-type labels, semicolon-separated; no inferred article/review classification. |
| `source_path`, `source_sha256` | Raw PubMed response path and checksum. |
| `source_correct_analysis` | Original `Correct_analyis`: `n` (91), `y` (45), `u` (64). |
| `classification` | `n` → `pseudoreplication`; `y` → `correct_analysis`; `u` → `unclear`. |
| `flagged` | `n` → 1; `y` → 0; `u` → blank, because the direction is unknown. |
| `randomisation` | Source `Randomisation`: whether randomisation was reported (`y`/`n`). |
| `blinding` | Source `Blinding`: whether blinding was reported (`y`/`n`). |
| `litter_count_reported` | Source `N_litters`: whether litter counts were reported (`y`/`n`), not the actual count. |
| `offspring_count_reported` | Source `N_offspring`: `y`/`n`/`mixed`; not an offspring count. |
| `split_unit` | Source `Split_unit`: whether a split-unit design was used (`y`/`n`). |
| `audit_year` | 2017, based on the repository publication year; exact earliest day remains under review. |
| `full_baseline_year` | `yes` when publication year < 2016, allowing all of 2016 to serve as baseline; otherwise `no`. |
| `two_full_preyears` | `yes` when publication year < 2015, allowing full 2015 and 2016 observations; otherwise `no`. |

Source study-design codes contain no missing cells. A reported `n` records the
auditors' assessment, not a missing value; absent reporting does not prove a
procedure was not performed. The unclear analysis group remains separate throughout.
`profile.json` tabulates all codes and publication years by classification, including
empty values. The source-to-derived category counts reconcile exactly.

`notice_links.csv` has one row per PubMed comment/correction relation; multiple
relations per paper are legitimate. Fields are source `pmid`, `relation` (e.g.
`ErratumIn`), `related_pmid` when available, `citation`, optional `note`, and
`source_path`. Blank related IDs do not mean no notice exists. Metadata relations
are discovery evidence and require notice-text review before assigning an error type.
