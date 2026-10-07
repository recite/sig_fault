# Why the citation counts differ

The paired comparison covers 153 original papers. The decomposition holds those identities fixed and exactly reconstructs OpenAlex article/review counts minus the historical Web of Science counts for every included paper-year. It does not estimate the publicity effect.

## Annual count decomposition

Entries are total citing relationships across the paired papers, not per-paper means. Positive entries raise OpenAlex relative to Web of Science.

Comparison papers

| Component | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Web of Science counts | 87 | 501 | 1,104 | 1,250 | 1,315 | 1,297 | 1,268 |
| OpenAlex article/review counts | 168 | 697 | 1,278 | 1,362 | 1,437 | 1,417 | 1,406 |
| Difference (OpenAlex minus WoS) | 81 | 196 | 174 | 112 | 122 | 120 | 138 |
| Shared-link publication years | 56 | 109 | 100 | 19 | 28 | -37 | -133 |
| Shared-link type exclusions | -7 | -15 | -38 | -31 | -74 | -31 | -37 |
| Shared-link predating exclusions | -5 | -4 | 0 | 0 | 0 | 0 | 0 |
| OpenAlex-only DOI | 47 | 126 | 172 | 170 | 205 | 205 | 352 |
| Web of Science-only DOI | -1 | -11 | -17 | -19 | -24 | -21 | -40 |
| OpenAlex without DOI | 0 | 29 | 37 | 56 | 59 | 57 | 46 |
| Web of Science without DOI | -9 | -38 | -80 | -83 | -72 | -53 | -50 |

Flagged papers

| Component | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Web of Science counts | 113 | 717 | 1,390 | 1,536 | 1,717 | 1,706 | 1,536 |
| OpenAlex article/review counts | 198 | 952 | 1,582 | 1,575 | 1,879 | 1,752 | 1,639 |
| Difference (OpenAlex minus WoS) | 85 | 235 | 192 | 39 | 162 | 46 | 103 |
| Shared-link publication years | 60 | 133 | 136 | -27 | 51 | -37 | -134 |
| Shared-link type exclusions | -2 | -21 | -55 | -66 | -62 | -74 | -46 |
| Shared-link predating exclusions | -7 | -7 | 0 | 0 | 0 | 0 | 0 |
| OpenAlex-only DOI | 46 | 158 | 171 | 220 | 229 | 211 | 325 |
| Web of Science-only DOI | -7 | -20 | -35 | -43 | -39 | -37 | -39 |
| OpenAlex without DOI | 1 | 40 | 39 | 46 | 56 | 47 | 40 |
| Web of Science without DOI | -6 | -48 | -64 | -91 | -73 | -64 | -43 |


Shared-link dating moves an eligible citation between years while keeping the citing DOI fixed. A shared link excluded by OpenAlex's article/review rule is assigned to type exclusions at its historical year; a remaining shared link dated before the original is assigned to predating exclusions. Only shared links eligible for the primary OpenAlex count enter the dating component. This ordering prevents double counting but is one accounting convention.

DOI-only terms are unmatched identifiers, not verified missing or erroneous references. Malformed DOIs, books versus chapters and different publication versions can create unmatched records. Non-DOI records are also unresolved across sources. The historical source lacks the document-type detail needed for an identical restriction.

## Publisher-date check

Among 3,223 shared links with different years, OpenAlex assigns 3,219 an earlier year. Publisher-deposited Crossref metadata supplies a separate check of online and print dates.

| Date evidence | Citation relationships |
| --- | ---: |
| Both dates available but do not explain the difference | 18 |
| Online or print date is missing | 168 |
| Publisher metadata unavailable | 2,886 |
| OpenAlex matches online year; WoS matches print year | 151 |

Date agreement supports a dating-convention explanation for those specific records. It does not prove that every date is correct, establish when authors became aware of the critique, or determine which date best measures that response. Records counted here are original–citing DOI relationships; the same citing paper may link to more than one original.

`python3 scripts/nieuwenhuis_diagnostics.py build` rebuilds these results offline. The `fetch-dates` command retrieves metadata only for shared links with conflicting years and retains cached responses. The date check is diagnostic-selected, not a representative audit of all citations. Original counts and citation dates remain unchanged.

See [paired counts](README.md), [record-level decomposition](../../data/nieuwenhuis/count_decomposition.csv), [date records](../../data/nieuwenhuis/date_disagreements.csv), and [metadata](../../data/nieuwenhuis/date_metadata.csv).

## Review of unmatched historical identifiers

The decomposition reconciles documented DOI transcription errors. Both original and corrected identifiers remain in the reconciled crosswalk. Translations and book components remain separate records. The [review ledger](../../data/nieuwenhuis/link_review.csv) records evidence and unresolved cases; no case is called a false citation merely because it lacks an exact match.

| Review finding | Historical relationships |
| --- | ---: |
| book reference component | 1 |
| doi transcription error | 2 |
| translation | 1 |
| unresolved | 6 |

After verified identifier corrections, matched-DOI relationships number 14744. The [original exact-DOI crosswalk](../../data/nieuwenhuis/doi_overlap.csv) retains the source identifiers for comparison.
