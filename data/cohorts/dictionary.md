# Cohort inventory dictionary and join rules

These files preserve source assessments for finding additional citation-study cohorts.
They do not yet contain treatment-effect estimates or a common error indicator.
Each study folder has the same derived files and its own original-column projections,
source manifest and interpretation notes. Exact downloaded files are preserved in
`private-data/cohorts/<study>/source/`, outside the public Git release.

## Paper roster

`papers.csv` has one row per `(cohort, paper_id)`. IDs are source-specific strings.
A source's candidate roster is preserved even when some papers were never assessed.

| Column | Meaning |
| --- | --- |
| cohort | Stable study-folder name; not an independent observation count |
| paper_id | Source paper ID, or numbered bibliographic label for PDF tables |
| title | Original title when available; blank when only a bibliographic label is resolved |
| doi | Original DOI from source metadata or the documented exact-title crosswalk; blank is unresolved |
| source_link | Original source project or report URL, not necessarily the original article URL |
| source_reference | Author-year-journal identity for PDF-based rosters |
| identity_status | `identified`, `bibliographic_reference`, or `crosswalk_pending` |
| assessments | Number of preserved assessment rows linked to this paper; zero means no assessment row, not failure |

`identity_links.csv` records added DOI links from the existing FLoRA inventory.
Only exact normalized title matches with one distinct DOI are used. Conflicting
DOIs are left unresolved. Multi100 additionally uses a SCORE identifier suffix
only when normalized titles agree. These are metadata links, not independent
validation of the original paper. The source projection preserves the pre-link DOI.

## Assessments

`assessments.csv` has one row per `(cohort, assessment_id)`. Rows may be claims,
individual interaction diagnostics, panel diagnostics, experimental effects or
analyst reports. Do not treat multiple rows for a paper as independent citation histories.

| Column | Meaning |
| --- | --- |
| paper_id | Many-to-one foreign key to the study's paper roster |
| assessment_id | Unique source report/effect/diagnostic identifier |
| assessment_type | The specific construct assessed; definitions remain study-specific |
| source_outcome | Original label, or the explicit source-table translation documented in the study README |
| source_file | Original filename and table locator when relevant; resolves through that study's manifest |
| p_value | Source-reported p value as text; may contain inequalities or missing values |

Blank outcomes remain missing. `not_applicable`, `not attemptable` and
incomplete-source labels are preserved rather than converted to success/failure.
HMX blank diagnostic cells remain unassessed. In the panel table, a blank is explicitly
an unmarked Boolean condition, whereas `n.a.` is inapplicable; this differs from HMX.
The row-level records must be aggregated under a stated paper-level rule before
citation matching or effect estimation.

## Provenance and source projections

`sources.csv` records the URL, retrieval timestamp, SHA-256, byte count, study and
local source path for each exact download. `source_records/` contains selected
scientific columns with original names, or a table extraction with named columns.
Whitespace within source fields is retained. The full original remains in the
matching private source folder. Contacts and
analyst personal details are not needed in the public projection.

SCORE joins are many-to-one: report ID into outcome data, then paper ID into metadata.
Duplicate right-hand keys and unmatched left records stop the build. Source-derived
subset rules reproduce the published row counts. The public root files are exact
concatenations of study files; offline validation checks keys, joins and content.
`overlap.csv` identifies repeated known DOIs across cohorts. Unresolved DOIs mean
that it is not a complete independence check. Existing FLoRA/FReD entries are
indexes of many of these same studies, not additional independent audits.

## Disclosure dates and eligibility

`study.json` distinguishes journal publication, documented announcement and the
remaining first-disclosure work. A journal date, submission date, analysis-completion
date or archive download date is not automatically the paper's treatment date.
The 2026 SCORE summaries are after the current 2025 citation cutoff. Earlier
individual reports require verification. No newly inventoried study enters the
current meta-analysis until identities, assessment definitions, timing and citation
comparisons are ready.

## Reproduction

- `make cohorts`: validate public tables and regenerate study indexes offline.
- `make cohorts-import`: reconstruct tables from the preserved original sources.
- `make cohorts-fetch`: retrieve sources at recorded URLs, require matching hashes,
  and reconstruct. If a living archive changes, the build stops instead of quietly
  accepting a new version.

R dependencies are recorded in `renv.lock`; PDF extraction uses Poppler's `pdftotext`.
