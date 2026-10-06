# What the second audit adds

Papers flagged for statistical problems continued to receive citations after the Lal et al. audit appeared. The comparisons with other assessed papers leave uncertain how much, if at all, the audit reduced citation growth. The two main estimates are imprecise and change substantially with the starting year. Their opposite signs do not establish that researchers responded differently to different statistical problems.

## What the citation counts show

Under the two main definitions, flagged papers' mean annual citations rose from 7.0 to 7.2 and from 7.1 to 10.3 between 2023 and 2025. Their medians changed little: 7.0 to 7.5 and 5.0 to 5.0. These counts document continued citation. They do not show how many citations the papers would have received without the critique.

The estimated relative changes are -14.5% (95% interval [-36.0, 14.2]) for the instrument-strength screen and 23.9% ([-7.1, 65.3]) for inferential sensitivity. Both intervals include reductions and increases. The definitions overlap and use different comparison populations, so the rows are alternative comparisons within one audit, not independent evidence of different responses.

The narrower Anderson–Rubin definition flags only three papers. Their total article/review citations fell from 16 to 11, and the relative point estimate remains negative under the reported baseline and leave-one-out checks. Those checks do not establish reliable inference with only three flagged papers or show that publicity caused the decline. We retain the comparison as exploratory; it does not support a separate account of how readers respond to this particular statistical problem.

## Baseline dependence

The inferential-sensitivity estimate depends strongly on the baseline year. The estimate changes from +23.9% to −17.0% with 2022, and to −2.6% with the two-year average baseline. The group had relatively weak growth in 2022–2023, which makes the subsequent comparison sensitive to starting in that year. The weak-F contrast changes from −14.5% to approximately zero with the earlier baseline.

The earlier baseline also excludes four recently published target papers. A common-cohort check separates those issues: retaining the same eligible papers, the sensitivity estimate is +15.7% from 2023 but −17.0% from 2022. Thus sample changes do not explain the reversal. A single before/after coefficient would overstate the stability of these results. The generated tables report all windows and the fixed older-cohort trajectories make the earlier evolution visible.

## Why the counting correction matters

The initial broad count included preprints and book chapters. It showed a much larger increase for the weak-instrument group. Inspection revealed that the index records many parts of a single Oxford book as separate citing works, including chapters and front matter. All nine components of one book citing Carnegie, all fourteen components of another citing Gehlbach, and all thirteen components of a third citing Hager have identical OpenAlex reference lists within their respective books. A book can be scientifically consequential, but it should not silently count as many independent publications simply because its bibliography is attached to multiple components.

The main analysis therefore counts articles and reviews. The original broader specification, an Oxford-book-collapsed version, and all-document counts remain reported. The switch was made after inspecting the first estimates and is documented in the design's deviation log. Broader counts still give different answers even after collapsing these books: publication type and the treatment of versions are substantively important. The article/review analysis is the closest current analogue to the original journal-citation study; it is not a comprehensive measure of all downstream scholarly use.

## What this does and does not identify

The measured outcome is annual citations recorded in OpenAlex's current graph, dated by the citing work's publication date. It is not a historical snapshot of the graph in each year. Changing preprint bibliographies, unmerged versions, and index coverage can affect the timing and number of observed links. Bibliographic reference verification also does not establish use of the challenged finding.

The 2024 article and replication archive were preceded by a circulating manuscript in 2021. In addition, the audit raises concerns about IV practice that extend to both comparison groups. The contrasts consequently describe how citation histories diverge across diagnostic categories; they do not isolate an unexpected treatment administered in 2024. Publication aging, research topics, later substantive developments, and corrections are possible explanations.

The reason to add further audits is to discover which of these patterns recur across different problems and fields. The inclusion rule should depend on having a recoverable assessed-paper set, interpretable diagnostics, a comparison, and a warning timeline—not on producing another finding of unchanged citations.
