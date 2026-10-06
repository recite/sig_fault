# I4R coverage and analysis readiness

The inventory covers both discovered catalogs. Assessment coverage remains incomplete; the 90% completion gate has not been met. Review dispositions include unresolved cases and limited screens, not just verified findings.

| Stage | Count |
| --- | ---: |
| Catalog entries | 714 |
| Discussion papers | 331 |
| Report listings | 383 |
| Retrieved documents (including separate replies and repeated files) | 1514 |
| Distinct retrieved document URLs | 770 |
| Retrieved listing metadata records | 707 |
| Candidate article identities (not a final distinct-paper count) | 517 |
| Publisher/OpenAlex-verified article identities | 458 |
| Source review/disposition records | 714 |
| Assessment records explicitly enumerated | 500 |
| Assessment records with unresolved reviewer-team equivalence | 37 |
| Articles in those enumerated assessments | 478 |
| Catalog entries with assessment scope accounted for | 584 |
| ZIP archives inventoried | 62 |
| Root ZIP files listed | 62 |
| Archive members, including code/data/plots | 3952 |
| OSF sources checked for components/providers | 378 |
| Distinct candidate control articles | 1022 |
| Controls with verified publisher dates | 1000 |
| Complete affected/control citation histories | 426 |
| Deduplicated article–citing-work relationships | 32069 |
| Source units after verified duplicate links | 634 |
| Verified duplicate listings collapsed | 80 |
| Source units containing article-specific assessments | 523 |
| Source units with resolved target classification | 382 |
| Units whose assessment eligibility remains unresolved | 26 |
| Curated material-error candidate records | 40 |
| Source-verified material-error disclosures with verified public year | 27 |
| Disclosures satisfying the primary date/age window | 6 |
| Events with selected controls | 0 |
| Complete matched article-period observations | 0 |

The source-level resolution fraction among confirmed assessment listings is 73.0%. Including unresolved-eligibility source units in the denominator gives 69.6%.

These are source-listing progress measures, not coverage of all independent article assessments. Shared projects can contain several assessment teams or articles. The 90% gate remains blocked until those units are enumerated and reviewed. Explicitly enumerated assessments are not yet a census of the total assessment population. The source-by-source enumeration ledger is `data/i4r/assessment_scope.csv`. See `data/i4r/coverage_scope.json` for resolved and unresolved scope.

## Current scope review

This review asks how many assessments each source contains and which versions belong together. An unresolved source has been examined but still lacks sufficient evidence to close that question.

| Status | Catalog entries |
| --- | ---: |
| fully enumerated | 513 |
| non assessment | 45 |
| supporting document | 26 |
| unresolved | 130 |

## Initial screening depth

| Status | Catalog entries |
| --- | ---: |
| abstract introduction screen only | 23 |
| author reply only reviewed | 1 |
| explicitly linked discussion paper reviewed | 14 |
| fulltext evidence sections reviewed | 33 |
| fulltext frontmatter screened | 78 |
| identity verified from aggregate roster; individual assessment unresolved | 15 |
| invalid catalog link | 1 |
| linked previous review | 95 |
| linked previous reviews with pending attachments | 1 |
| opening screen with reply where available | 50 |
| pending | 20 |
| same article discussion paper identified; OSF report unverified | 39 |
| targeted body review | 99 |
| targeted fulltext screened | 174 |
| unresolved document unavailable | 13 |
| unresolved fulltext unavailable | 58 |

## What is and is not established

The 714 entries are documents/listings, not distinct original articles. Reports, replies, aggregate rosters and repeated assessments overlap. The article table still contains unresolved identities; DOI aliases are merged only when supported.

Source review means the recorded passages were read. It does not mean the original analysis was rerun. Full-text availability, screening, a material-error assessment and a verified disclosure date are separate fields.

Anonymous OSF and OpenAlex access was rate-limited during acquisition. The cached sources are retained and retrieval resumes from checkpoints. Crossref verifies source-supplied DOIs and unique exact-title matches. Missing article metadata, citations or control pools are never filled with zeros.

The aggregate economics/political-science package anonymizes article identities; it cannot supply the missing crosswalk. Its Appendix B roster identifies articles separately. The registry retains the 110 roster rows (109 distinct titles) rather than assuming 110 distinct papers. The psychology roster has 67 report rows and 64 distinct DOIs.

The strict primary window requires two complete calendar years after publication before disclosure and one complete year afterward. Recent errors remain in the registry but cannot enter that comparison. Do not substitute a later I4R report date to obtain a longer baseline.

The primary article/review analysis remains pending until verified identities, complete risk sets and complete citation retrieval produce supported matched panels. The separately matched [annual-total analysis](aggregate-results.md) reports secondary contrasts from cached all-type totals.

See [the evidence catalog](catalog.html), [design](design.md), [data dictionary](codebook.md), and [analysis status](results.md).
