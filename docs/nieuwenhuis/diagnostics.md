# Why the citation counts differ

The paired comparison covers 10 original papers. The decomposition holds those identities fixed and exactly reconstructs OpenAlex article/review counts minus the historical Web of Science counts for every included paper-year. It does not estimate the publicity effect.

## Annual count decomposition

Entries are total citing relationships across the paired papers, not per-paper means. Positive entries raise OpenAlex relative to Web of Science.

Flagged papers

| Component | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Web of Science counts | 11 | 81 | 179 | 192 | 239 | 227 | 234 |
| OpenAlex article/review counts | 19 | 102 | 200 | 200 | 253 | 231 | 244 |
| Difference (OpenAlex minus WoS) | 8 | 21 | 21 | 8 | 14 | 4 | 10 |
| Shared-link publication years | 6 | 15 | 12 | 10 | 4 | -8 | -20 |
| Shared-link type exclusions | -1 | -1 | -4 | -12 | -6 | -12 | -18 |
| Shared-link predating exclusions | 0 | -1 | 0 | 0 | 0 | 0 | 0 |
| OpenAlex-only DOI | 3 | 11 | 17 | 20 | 20 | 26 | 52 |
| Web of Science-only DOI | 0 | -2 | -1 | -2 | -1 | -1 | -1 |
| OpenAlex without DOI | 0 | 4 | 4 | 4 | 7 | 3 | 4 |
| Web of Science without DOI | 0 | -5 | -7 | -12 | -10 | -4 | -7 |


Shared-link dating moves an eligible citation between years while keeping the citing DOI fixed. A shared link excluded by OpenAlex's article/review rule is assigned to type exclusions at its historical year; a remaining shared link dated before the original is assigned to predating exclusions. Only shared links eligible for the primary OpenAlex count enter the dating component. This ordering prevents double counting but is one accounting convention.

DOI-only terms are unmatched identifiers, not verified missing or erroneous references. Malformed DOIs, books versus chapters and different publication versions can create unmatched records. Non-DOI records are also unresolved across sources. The historical source lacks the document-type detail needed for an identical restriction.

## Publisher-date check

Among 219 shared links with different years, OpenAlex assigns 218 an earlier year. Publisher-deposited Crossref metadata supplies a separate check of online and print dates.

| Date evidence | Citation relationships |
| --- | ---: |
| Both dates available but do not explain the difference | 11 |
| Online or print date is missing | 111 |
| OpenAlex matches online year; WoS matches print year | 97 |

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

After verified identifier corrections, matched-DOI relationships number 1130. The [original exact-DOI crosswalk](../../data/nieuwenhuis/doi_overlap.csv) retains the source identifiers for comparison.
