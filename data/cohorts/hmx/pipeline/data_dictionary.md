# Interaction-audit data dictionary

All CSV files use UTF-8, a header row and empty cells for unavailable values.
`paper_id` links originals throughout the study. DOI values are lowercase, without
a resolver prefix. An assessment row is an interaction/test record, not a separate
original paper.

| File | Unit and key | Important fields |
| --- | --- | --- |
| `reference_crosswalk.csv` | One original; `paper_id` | Audit-publisher reference key, first author, publication year, journal and ISSN used for identity verification |
| `identities.csv` | One original; `paper_id`, unique `doi` | Verified DOI and title, source reference, verification status |
| `paper_assessments.csv` | One original; `paper_id` | Separate severe-extrapolation, linearity and low/high labels: `flagged`, `comparison`, or `unknown`; `meta_eligible` and `earlier_critique` are explicit `True`/`False` strings |
| `overlap.csv` | One shared original and other study | Matched DOI and other study's original-paper identifier |
| `citation_targets.csv` | One original; `paper_id` | Acquisition identity, primary `role`, and audit DOI |
| `citation_coverage.csv` | One original; `paper_id` | `complete`, reported API records, pages fetched, target work ID, target type and retraction indicator |
| `citation_edges.csv` | One original–citing work pair | Citing ID, DOI, title, date, year, document type, audit-self-citation indicator, exclusion reason and duplicate decision |
| `citation_identity_decisions.csv` | One target and conflicting citing DOI | Canonical work ID, competing IDs/years, resolution basis |
| `panel.csv` | One original and calendar year; `paper_id`, `year` | `citations`: eligible distinct article/review citations; `all_types`: eligible distinct citations of any type; `status`: completed history or missing history |
| `specifications.csv` | One fitted specification | Baseline year, final follow-up year, diagnostic, sample selection and outcome. Follow-up begins two calendar years after baseline |
| `paper_periods.csv` | One specification and original | `before`, `after`: mean annual citations in each window; `change`: after minus before; `flag`: adverse diagnostic indicator |
| `estimates.csv` | One proportional model | Log ratio and clustered standard error, contributing group counts, exclusions, degrees of freedom, ratio and percentage-scale estimates/intervals |
| `absolute_estimates.csv` | One unadjusted absolute contrast | Difference in changes, Welch standard error, degrees of freedom and interval |
| `bootstrap.csv` | One unadjusted proportional specification | Paired article draws, seed, undefined draws, log standard error and percentile intervals |
| `period_summary.csv` | One primary diagnostic group | Counts, mean/median levels, mean/median individual changes and totals |
| `annual_summary.csv` | One year and primary diagnostic group | Count, total, mean, median, zero count and maximum |
| `journal_support.csv` | One journal and primary diagnostic group | Number of originals, including zero-history originals |
| `leave_one_out.csv` | One omitted original | Primary proportional and absolute contrasts after omission |

Panel years before an original's publication are structural zeros. Citation-growth
models use only the specified later windows; they do not treat those structural
zeros as observed exposure. Zero citations require a completed acquisition. An
all-zero selected window is omitted from Poisson estimation and explicitly listed;
it remains in descriptive statistics. Records beyond the December 31, 2025 cutoff,
prepublication citations, unverifiable links and DOI duplicates remain in the edge
ledger with exclusion information.

`timing.json` separates formal publication from earlier circulation. Source bodies,
checksums, retrieval URLs and dates are recorded by the acquisition receipts.
Model intervals and resampling procedures are described in the [design](design.md)
and generated [report](README.md).
