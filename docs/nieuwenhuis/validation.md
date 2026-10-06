# Checking citation links against OpenCitations

OpenCitations also records 118 of the 149 OpenAlex-only links eligible for our primary article/review count. Across all document types in the comparison frame, it records 194 of 292 OpenAlex-only links.

The frame consists of DOI-bearing relationships dated 2009–2015 in at least one of the two original sources, after documented DOI transcription repairs. This is the same selected, flagged-only paired sample used in the source comparison; it cannot estimate coverage for comparison papers or the full cohort.
Headline fractions include only targets with complete OpenCitations retrieval. The table also identifies any links whose target's third-source retrieval is incomplete.

| Original sources | Links | Also in OpenCitations | Not found | Collection incomplete |
| --- | ---: | ---: | ---: | ---: |
| Both | 1130 | 1129 | 1 | 0 |
| OpenAlex only | 292 | 194 | 98 | 0 |
| Web of Science only | 8 | 3 | 5 | 0 |

OpenCitations and OpenAlex can share upstream records. Agreement corroborates a recorded link but does not independently verify the citing bibliography, establish a common publication year, or show that the citation endorses the affected claim. A link not found in this index is not thereby false. These records do not replace either database's annual citation counts.

The complete OpenCitations responses include 36 undated relationships across all years. They remain in the link data with empty dates. Every accepted response matches the separate count endpoint, has unique citation identifiers, and identifies the queried target DOI in every record. Completeness refers to the API response, not all citations that exist in the literature.

## Reproduce

```sh
make nieuwenhuis-validation
```

This offline target rebuilds the crosswalk, summary, report and manuscript macros from frozen public inputs. To collect links for the complete paired-paper sample, run `python3 scripts/nieuwenhuis_validation.py fetch`. Successful responses retain source URLs, retrieval dates and SHA-256 hashes.

See the [record-level crosswalk](../../data/nieuwenhuis/link_validation.csv), [retrieval status](../../data/nieuwenhuis/validation_coverage.csv), [source manifest](../../data/nieuwenhuis/validation_sources.csv), and [OpenCitations API documentation](https://api.opencitations.net/index/v2).
