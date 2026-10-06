# Larger assessment inventories

The four matched I4R papers remain a pilot. The next expansion starts from complete
external inventories, before selecting papers with verified consequential errors.
No citation outcomes were used to choose or classify these new records.

| Frozen source | Records retained | Distinct syntactically valid original DOIs | Unit |
| --- | ---: | ---: | --- |
| FLoRA | 3,056 | 2,772 | Original–assessment reference pair as supplied |
| FReD | 2,164 | 780 | Effect nested within original and replication papers |
| Statcheck 2016 | 688,112 | 50,845 | Extracted statistical result |

These are full snapshots of the named sources, not a census of scientific errors.
The source files, permanent version URLs, retrieval times and checksums are in
[`data/inventories/sources.json`](../data/inventories/sources.json).
The combined inventory contains 53,351 distinct valid
original DOI strings. Syntactic validity does not establish a correct bibliographic
match; aliases and publication versions still require review.

## First priority: same-data reproduction reports

FLoRA contains 365 reproduction records covering
352 valid original DOIs. Of these,
209 records concerning
200 original DOIs describe computational
issues or robustness challenges. Among those originals,
156 do not occur in the current I4R
DOI registry. This is a larger and more relevant starting pool than repeatedly
changing the specification on four papers.

The [review queue](../data/inventories/reproduction_review_queue.csv) retains **all**
reproduction records, including favorable and technical-failure assessments.
Computational issues receive first review, followed by robustness challenges.
The outcome label alone cannot establish material error: minor rounding differences
can receive an adverse label, while a reproducible computation can contain a
consequential coding mistake. Record the actual mistake, affected claim, numerical
consequence, source passage, author response and earliest public disclosure.

## Second priority: the large statistical-reporting audit

The archived statcheck release supplies all 50,845
per-paper result files. Together they contain 688,112 tests,
matching the published inventory. At least one statistical inconsistency is flagged
in 23,523 papers;
6,008 have a flag that could change
statistical significance. These are automated flags, not verified consequential
errors. The [paper inventory](../data/inventories/statcheck_inventory.csv) retains
unflagged papers and counts of unresolved labels as well as flagged papers.

Before effect estimation, establish which reports were actually posted publicly,
their dates and their contents. The archive's report-generation script states a
scan date; that is not evidence of public posting. Public reports also existed for
papers without flagged inconsistencies, so flagged-versus-unflagged comparisons
would concern the content of the assessment, not publicity versus no publicity.
Inspect source text for extraction errors, one-sided tests, multiplicity corrections
and whether a flagged result supports a substantive claim.

## Replication evidence remains a separate question

FReD and FLoRA also identify failed and successful replications. A failed replication
can reflect sampling variation, a failed manipulation or different study conditions;
it does not by itself establish a mistake in the original paper. These records can
support a later study of the effect of publicizing unsuccessful replications, with
its own estimand. They do not enter the verified-error analysis automatically.

## Build and checks

Run `make inventories` to rebuild the inventories and this report offline, and
`make inventories-test` for the parser and identity checks. All source rows survive.
There are 5 repeated fully specified FLoRA
original/report/type keys, retained in a
[review ledger](../data/inventories/repeated_assessment_keys.csv).
An umbrella report can contain separate attempts, and one repeated key has conflicting
outcomes. No automatic deduplication or majority vote resolves those cases.

The [dictionary and construction notes](inventory-methods.md) define fields, joins,
missing values, attribution and the remaining eligibility checks. The newly imported
records contribute **zero newly adjudicated material errors and zero new eligible
citation comparisons** at this stage. The existing citation estimates are unchanged.
