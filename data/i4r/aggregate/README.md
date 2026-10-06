# Annual-total secondary analysis

This directory contains an independently reproducible secondary measurement and matched analysis. OpenAlex's `counts_by_year` includes all citing document types; it is not the primary deduplicated article/review edge count. The source responses were retrieved October 5–6, 2026. The supported annual window is 2017–2025, including observed zero years. Missing fields, unresolved identities, stale snapshots and years outside that window are not converted to zero.

Run `make i4r-aggregate` from the repository root. Re-extracting inputs requires the ignored source cache and `python3 scripts/i4r_aggregate.py extract`. No API request is made by either command. The main registry and `data/i4r/control_exclusions.csv` supply article identities, disclosure evidence and control eligibility.

| File | Row unit and purpose |
| --- | --- |
| `citations.csv` | One original/control article and completed calendar year; nonnegative integer `citations`, with `status=complete` only for a supported precomputed history. Key: article/year. |
| `provenance.csv` | One inventory article; exact DOI/OpenAlex identity, availability status, supported first/last year, raw-response path/URL/hash, retrieval timestamp and work update timestamp. Missing source fields indicate unavailable data. |
| `measurement_comparison.csv` | One article/year observed in both measurements; all-type total, deduplicated article/review edge count and their difference. Different type coverage and precomputation prevent treating a difference as an error by itself. |
| `match_candidates.csv` | One event/control/horizon candidate and explicit eligibility reason or pre-period distance. |
| `matches.csv` | One selected event/control/horizon; rank, distance and within-set weight summing to one. |
| `match_balance.csv` | Selected controls' standardized pre-count and change differences, and title/abstract cosine distance. |
| `match_exclusions.csv`, `panel_exclusions.csv` | Event/horizon exclusions before matching or because a selected set lacks outcomes. |
| `analysis_panel.csv` | One stack/article/period; treated article weight one and controls combined weight one. Original article IDs survive reused controls. |
| `case_contrasts.csv` | One event/horizon; observed treated and weighted-control counts before/after and their difference in changes. |
| `estimates.csv`, `descriptive.csv` | Horizon-level equal-treated-weight contrasts and group-period citation summaries. Median averages adjacent values when cumulative weight is exactly one half. |
| `sensitivity_panel.csv`, `sensitivity_estimates.csv` | Declared alternative baselines, fixed cohorts, one-control comparisons and leave-one-disclosure-out contrasts. |
| `figure_paths.csv` | One event/group/relative year; affected-paper count or weighted control mean displayed in the manuscript. |
| `event_trajectories.csv` | One event/article/relative year, with missing and partial-publication-year statuses explicit. |

Matching uses only pre-disclosure counts and text. It waits until every otherwise eligible control has a complete history; the realized selected subset does not determine acquisition completeness. This outcome produces its own matches and is not a same-match comparison with the pending primary measure. See the [design](../../../docs/i4r/aggregate-design.md) and [results](../../../docs/i4r/aggregate-results.md).
