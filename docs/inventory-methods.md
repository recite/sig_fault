# Inventory dictionary and construction

These files inventory assessments. They are not an analysis-ready treatment panel.
The exposure of interest remains the first public disclosure of a consequential
error in an identified paper. Neither an audit label nor a journal publication year
establishes that exposure.

## Sources and attribution

- **FLoRA:** FORRT's original–assessment reference pairs, from `output/flora.csv` at
  the immutable Git commit recorded in `data/inventories/sources.json`.
- **FReD:** FORRT's complete effect records exported by the official explorer, from
  `data/explorer-data.json` at a separate recorded commit. This snapshot need not
  have the same coverage as the FLoRA snapshot. Both datasets are CC BY 4.0; credit
  FORRT and the FReD/FLoRA contributors. Their [data repository](https://github.com/forrtproject/fred-data)
  and [applications repository](https://github.com/forrtproject/fred-apps) document
  the data and licensing. Upstream fields are preserved in compressed source files.
- **Statcheck:** Chris H. J. Hartgerink, *688,112 Statistical Results: Content Mining
  Psychology Articles for Statistical Test Results* (2016),
  [data description](https://doi.org/10.3390/data1030014),
  [archived source release](https://doi.org/10.5281/zenodo.59818), CC0 1.0.
  The original articles are not redistributed. All 50,845 individual result CSVs
  are concatenated under the archived header. The combined CSV in the release is
  only a Git LFS pointer. Our reconstruction agrees with its recorded byte size
  and with the published test and paper counts, but its hash differs from the
  unavailable combined object. The original concatenation order is unknown;
  we make no claim of byte identity with that object. The source archive and our
  deterministic reconstruction each have a recorded SHA-256.

`data/inventories/sources/` contains gzip-compressed original FLoRA CSV and FReD
JSON bytes, and the reconstructed statcheck CSV. Compression uses a fixed zero
timestamp; decompression is lossless. The build checks compressed and decompressed
hashes before parsing. These are public offline inputs, not caches required from a
private directory. Supporting source instructions are retained with attribution.

To reconstruct statcheck from the archived release:

```sh
curl -L --fail https://zenodo.org/api/records/59818/files/2016statcheck_data-v1.0.0.zip/content -o /tmp/statcheck-2016.zip
python3 scripts/audit_inventories.py import-statcheck /tmp/statcheck-2016.zip
make inventories
```

The archive is preserved under `private-data/inventories/` locally; its fixed hash
is checked before import. Import never executes upstream scripts or extracts
arbitrary archive paths. The archived report-generation code documents the meaning
of its source flags, but running that code is not part of this build.

## Tables and keys

| File in `data/inventories/` | Row unit and key | Relevant columns |
| --- | --- | --- |
| `flora_inventory.csv` | One source row; `record_id` | Original/report DOI and supplied identifiers, alternative identifiers, titles, years, assessment type, source outcome, source collection, evidence quote and location |
| `fred_inventory.csv` | One effect source row; `record_id` | Original/report DOI, references, effect description, full JSON of upstream outcomes under each replication criterion |
| `statcheck_inventory.csv` | One normalized original DOI | Original title, publication year, journal, number of extracted tests, inconsistency/decision-inconsistency flags, missing-label counts and metadata-conflict flag |
| `article_crosswalk.csv` | One distinct valid original DOI across the three inventories | Counts of records from each inventory and exact normalized DOI membership in the existing I4R article registry |
| `reproduction_review_queue.csv` | One FLoRA reproduction source row | All FLoRA inventory fields, review priority, and I4R DOI membership; no rows excluded on assessment outcome |
| `repeated_assessment_keys.csv` | Repeated valid original DOI × report DOI × assessment type | Source row IDs and outcomes, including conflicts; these are review candidates, not automatically duplicate assessments |
| `status.json` | Source-specific inventory counts | Counts of records, distinct valid DOI strings, missing identities and review candidates; distinct from eligible error events |
| `sources.json` | One frozen input | Source URL/version, retrieval time, hashes, license and attribution |
| `primary_reviews.json` | One manually reviewed reproduction report | Error mechanism, consequence, author response, primary-source locations and hashes, competing date evidence and unresolved eligibility |

`record_id` combines the source and its one-based data-row index in this frozen
snapshot. It is a row locator, not a stable scholarly identity across source
updates. `source_row` provides that index; FReD also retains its supplied `source_id`.
All identifiers and publication years are read as strings. Empty strings represent
missing or invalid normalized fields. Raw values remain available separately.

`original_year` and `report_year` are supplied bibliographic years, not verified
first-publication years. `first_public_disclosure` is blank throughout these new
inventories. `material_error_status=not_adjudicated` and
`citation_analysis_eligible=not_assessed` prevent source labels from silently
becoming verified error treatments.

Statcheck's `inconsistent_tests` counts source `Error=TRUE` labels;
`decision_inconsistent_tests` counts `DecisionError=TRUE`. The latter concerns
possible changes across the significance threshold, not substantive materiality.
`missing_error_labels` and `missing_decision_labels` retain `NA`; missing labels
are never counted as clean results. Counts are integers, while `metadata_conflict`
flags inconsistent article metadata across result rows. The full test-level
statistics, quoted expressions and one-tail flags remain in the compressed source.

## Recodes and joins

1. Decode FLoRA as UTF-8 with its byte-order mark removed. Preserve every data row.
2. Lowercase DOI strings and remove explicit DOI URL/`doi:` prefixes. Accept only
   `^10\.\d{4,9}/\S+$` as syntactically valid; this is not external verification.
   Do not guess repairs or turn thesis URLs into DOIs. For example,
   `0.1162/0033553053327524` remains unresolved.
3. Convert literal `NA`, empty strings and JSON null to empty derived fields;
   preserve original bytes. Do not coerce missing numerical values to zero.
4. Group statcheck tests by normalized DOI. Sum explicit TRUE flags and missing
   labels separately, checking published full-cohort counts. Do not infer absence
   of mistakes elsewhere in an unflagged paper.
5. Left-preserve every FLoRA/FReD source row. Map valid DOI strings many-to-one to
   the crosswalk. Rows without valid DOIs remain in their source inventories and
   are excluded only from DOI-based counts. No title-based or fuzzy alias merges.
6. Mark I4R overlap by exact normalized DOI membership; queue rows without a valid
   original DOI receive `unknown`, not `no`. This cannot detect different
   DOIs for preprint/published versions and therefore does not prove non-overlap.
7. Rank all same-data reproduction rows for review: computational issues first,
   robustness challenges next, remaining outcomes third. These are workload
   priorities, not error classifications. No citation outcomes enter the ranking.

The five repeated fully specified FLoRA keys retain separate rows. One gives both
mixed and failed outcomes. Another references different individual OSF attempts
under the same umbrella article. Generic references such as “Withdrawn. (2024).”
can refer to different DOIs and must not serve as automatic alias keys.

FReD's application export hardcodes `source=null`; its `validated` indicator is
constructed from contributor availability. Neither field is used to infer the
presence or absence of substantive validation. Replication success criteria remain
source measurements, not competing definitions of a consequential error.

## What remains before estimation

The first review pass should cover the reproduction inventory, retaining favorable,
minor-error and unresolved dispositions as well as material errors. Verify original
and report identities, isolate the error from specification disagreements, record
its consequence for a claim, and recover the earliest public version containing
that criticism. Repeated reports and preprint/journal versions share one exposure
when they publicize the same error. Later I4R listings do not reset the clock.

For statcheck, first acquire the actual public posting roster and dates and verify
that archived flags match posted reports. A scan or archive date is not a posting
date. Source-text review must address one-sided tests, adjusted p-values and parser
mistakes before classifying significant errors. Papers with no detected flags may
also have public assessment reports and are not automatically unexposed controls.

For unsuccessful replications, define a separate estimand about publicity of
replication results; do not mix those events with verified errors. FORRT's FAQ
includes failed manipulation checks among failed replications and uses assessors'
reported conclusions. Such records do not establish that the original result was
incorrect.

Freeze exposure and comparison definitions before collecting or examining new
citation outcomes. Report denominators at each stage: source records, original
papers, assessed claims, verified material errors, dated first disclosures and
complete matched histories. Keep treatment-effect estimation and synthesis pending
until those requirements are met.

## Validation of this import

An independent review reproduced the source record counts, DOI overlaps and
statcheck flag counts. It identified six reproduction records without usable
original DOIs; those records now retain unknown I4R membership. A temporary build
containing only public source snapshots, the excerpt-screen annotations, the import
script and the I4R article roster reproduced all ten inventory/report outputs byte
for byte, without private files or network access. Local checks cover malformed identifiers, conflicting
assessments, missing flags and repeated papers across sources. The full repository
lint, tests and manuscript build also pass.

## Complete reproduction-excerpt screening

`reproduction_screens.json` records a first reading of every supplied reproduction
excerpt, with an alleged mechanism, stated consequence, reason and scope.
`reproduction_screening.csv` joins these annotations one-to-one to all reproduction
records. The join rejects missing or repeated IDs, changed identities, changed
excerpt hashes and unknown categories. `error_review_queue.csv` contains the
explicit-error candidates for full-report review; it is not an eligible treatment
sample. Source outcomes and unresolved records remain intact.

The categories distinguish an explicit error candidate, a minor/nonmaterial issue,
a specification dispute, a reproduction failure with no stated mechanism, no
adverse claim in the excerpt, and insufficient information. These describe what
the excerpt supports; even an explicit error candidate may turn out to be disputed,
nonmaterial or incorrectly linked. The screen does not infer the earliest public
disclosure date from the source's report year.

Two assistant reviewers read disjoint slices covering all 365 reproduction records;
source IDs, identities and evidence hashes were checked centrally. Full-report
verification and author-response review follow this screen. The complete screen
also catches possible identity mismatches and consequential corrections hidden
under favorable source labels. No screen category automatically adds an event to
the I4R registry or changes a citation estimate.

The [first primary-report reviews](inventory-primary-reviews.md) retain four
case assessments separately from the excerpt screen. The central review checked
the numerical claims and key passages in the downloaded documents. Original
analyses were not rerun. Source files are cached with hashes; the public review
includes source URLs and locations. No reviewed case is yet assigned an eligible
treatment date or added to matching. The inventory status field
`imported_verified_material_errors` counts automatic classifications by the import
(always zero), not findings from these separate manual reviews.
