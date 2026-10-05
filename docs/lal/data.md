# Data and reproduction

The source is the frozen Lal et al. replication workspace already recorded in `data/pilot/source_manifest.csv`. `make lal` regenerates paper classifications, annual citation counts, models, tables, and figures without network access. `make lal-test` verifies both publication counting and the estimators against independent calculations.

| File in `data/lal/` | Unit and content |
| --- | --- |
| `papers.csv` | One of 67 original papers; source title/authors/journal/year, all design IDs, any-design diagnostic flags. |
| `diagnostic_checks.csv` | One of 70 designs; archived and used AR values, instrument dimensionality and verification source, tF applicability. |
| `identities.csv` | One original paper; checked journal-article DOI and OpenAlex ID, online date, title/author/journal evidence. |
| `source_manifest.csv` | One privately cached API response; public URL, retrieval time, byte count and SHA-256. |
| `coverage.csv` | One target paper; expected incoming-link total, page count and successful completion. |
| `citation_edges.csv` | One target–citing-work relationship; raw metadata, graph-verified reference, same-DOI duplicate disposition. |
| `citation_identity_decisions.csv` | Publisher-verified decisions overriding or confirming the default earliest-date DOI deduplication. |
| `edge_exclusions.csv` | Raw relationships omitted from the primary outcome and their reasons; some remain in broader sensitivities. |
| `oxford_book_records.csv` | Eligible incoming records sharing an Oxford ISBN-based DOI family, for the book-count sensitivity. |
| `panel.csv` | Original paper × citing publication year; covered zeros, article/review counts, broader counts, Oxford-book-collapsed counts and all-document counts. |
| `summary.csv` | Diagnostic × group; equal-paper means, medians and within-paper changes for 2023 and 2025. |
| `annual_summary.csv` | Diagnostic × fixed publication cohort × group × year; means and medians. |
| `estimates.csv` | Diagnostic × PPML specification; coefficient, uncertainty, group sizes, model exclusions and percent transformation. |
| `absolute_changes.csv` | Diagnostic-specific absolute difference in mean changes, with HC3 uncertainty. |
| `paper_changes.csv` | One paper per applicable contrast; 2023/2025 values and changes. |
| `leave_one_out.csv` | Each main PPML contrast with one flagged paper omitted. |

## Identity and join checks

Seventy source designs collapse to 67 paper titles. Identities join 1:1 by paper ID; DOIs and target OpenAlex IDs must also be unique. Incoming works join many:1 to targets. A citing work may legitimately cite several targets, so target–citing-work ID is the relationship key. Full pagination must match the API's reported count and each incoming record must reference its target. All 67 histories must be complete before panel construction. Missing histories are never filled with zeros.

Searches are only candidate generation. The final identities were checked on title, authors, journal and online-versus-issue dates. Dataset and SSRN records with identical titles were rejected in favor of the audited journal article. Four title searches required publisher/author DOI lookup, and Dower's journal article was resolved separately from its SSRN version. Repeating `python3 scripts/lal_citations.py resolve` writes candidates privately; it does not overwrite the reviewed identities.

## Counts and dates

The frame includes citing works dated through December 31, 2025. It is a current-graph extraction, not a sequence of historical database snapshots. Citation-free years become zeros only after complete retrieval. The panel starts in the target's online-publication year; models use complete subsequent years. A 2022 baseline therefore excludes the four targets first published online in 2022, and uses 63 papers before diagnostic restrictions. The older trajectory plot uses a fixed cohort first published by 2016.

Repeated DOIs count once per target, keeping the earliest dated record, with work ID as tie-breaker unless publisher-verified adjudication establishes a different identity. The Rueda citation decision restores a 2020 journal article whose DOI was also misassigned to a 2014 dissertation. The Coppock decision confirms a 2021 online date despite a 2023 issue record. The raw frame remains unchanged; panel construction applies the explicit decision table. Different-DOI versions can still duplicate a paper; they are not fuzzy-merged. Records predating the target's online-publication year are retained in the exclusion ledger. They may refer to circulating drafts or reflect changing preprint bibliographies; they are not labeled false citations. None enters the main 2023/2025 comparison.

The primary citation count includes OpenAlex types `article` and `review`. It is a document-type restriction, not a guarantee that every item was peer-reviewed. The broader sensitivity also includes preprints, book chapters and proceedings articles. The Oxford-book sensitivity identifies DOI families beginning `10.1093/` followed by an ISBN (also allowing `oso/`), counting one eligible work per book–target relationship at its earliest observed eligible date. It does not resolve every publisher's book structure. All-document counts include other types after duplicate, target-self and prepublication-year dispositions.

## Classification and uncertainty

`weak` means any assessed design has effective F below 10. `sensitive` means any conventionally significant design loses significance under the used AR or applicable archived tF procedure. `screen` is their union. `ar_loss` uses AR only. `analytic_positive` uses any assessed design, so Dower remains eligible even though its first design is not significant. For Alt, use the independently reproduced seven-indicator AR result and exclude its inapplicable single-instrument tF procedure; its AR-loss status remains unchanged. Instrument dimensions are independently checked for ten replicated designs and source-based for the remainder. The public table makes that distinction explicit.

Article/year PPML uses one observation per original paper-year, explicit `fixest` finite-sample corrections, one-way article clustering, and t(G−1) critical values. Article-clustered intervals assume the paper is the independent unit; topic or citing-source dependence across papers may violate that assumption. With few flagged papers, asymptotic coverage is uncertain. Absolute changes use `lm` with HC3 covariance and residual t critical values. There is no random assignment and no randomization-inference claim. Broad and narrow diagnostics are a reported exploratory family.
