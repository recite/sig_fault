# Checking citation links against OpenCitations

OpenCitations also records 2141 of the 2637 OpenAlex-only links eligible for our primary article/review count. Across all document types in the comparison frame, it records 3451 of 4719 OpenAlex-only links.

The frame consists of DOI-bearing relationships dated 2009–2015 in at least one of the two original sources, after documented DOI transcription repairs. It uses the available paired-paper sample from the source comparison; the coverage counts below distinguish complete third-source acquisition from an absent citation link.
Headline fractions include only targets with complete OpenCitations retrieval. The table also identifies any links whose target's third-source retrieval is incomplete.

| Original sources | Links | Also in OpenCitations | Not found | Collection incomplete |
| --- | ---: | ---: | ---: | ---: |
| Both | 14744 | 14710 | 34 | 0 |
| OpenAlex only | 4719 | 3451 | 1268 | 0 |
| Web of Science only | 353 | 63 | 290 | 0 |

OpenCitations and OpenAlex can share upstream records. Agreement corroborates a recorded link but does not independently verify the citing bibliography, establish a common publication year, or show that the citation endorses the affected claim. A link not found in this index is not thereby false. These records do not replace either database's annual citation counts.

The responses for these paired papers include 310 undated relationships across all years. They remain in the link data with empty dates. Every accepted response matches the separate count endpoint, has unique citation identifiers, and identifies the queried target DOI in every record. Completeness refers to the API response, not all citations that exist in the literature.

The separate [full-cohort source comparison](opencitations.md) collects both flagged and comparison papers from the historical frame.

## Reproduce

```sh
make nieuwenhuis-validation
```

This offline target rebuilds the crosswalk, summary, report and manuscript macros from frozen public inputs. To collect links for the complete paired-paper sample, run `python3 scripts/nieuwenhuis_validation.py fetch`. Successful responses retain source URLs, retrieval dates and SHA-256 hashes.

See the [record-level crosswalk](../../data/nieuwenhuis/link_validation.csv), [retrieval status](../../data/nieuwenhuis/validation_coverage.csv), [source manifest](../../data/nieuwenhuis/validation_sources.csv), and [OpenCitations API documentation](https://api.opencitations.net/index/v2).
