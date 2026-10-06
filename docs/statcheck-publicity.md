# Establishing the statcheck exposure

Statcheck offers a large, identified paper roster, but the archived flags alone
do not establish the content and date of each public warning. Reports were also
posted for papers without detected inconsistencies. A comparison between the two
groups would therefore concern adverse versus clean audit reports, rather than
publication of a warning versus no assessment.

The project author's [October 2016 response](https://retractionwatch.com/wp-content/uploads/2016/10/20161026dgps.pdf)
announced a rescan and replacement reports after identifying parser problems.
Original and revised reports need separate records. The
[source-readiness record](../data/inventories/statcheck_publicity.json) preserves
URLs, retrieval times, hashes, an inspected example and unresolved acquisition.

## An inspected report history

The [PubPeer discussion of Lai et al.](https://pubpeer.com/publications/DCE07BC7DD0BA211BC5B41365F4BB5)
contains an initial report, an author response and a rescan. The platform's
acceptance timestamps distinguish these events from the scan date printed inside
the original report.

| Report | Platform date | Extracted tests | Inconsistencies | Threshold-crossing inconsistencies |
| --- | --- | ---: | ---: | ---: |
| Original, statcheck 1.0.1 | September 3, 2016 | 62 | 6 | 4 |
| Revised, statcheck 1.2.2 | November 7, 2016 | 60 | 4 | 2 |

The frozen inventory agrees with the original report. The authors' September 10
response attributes the discrepancies to misreported test statistics and degrees
of freedom; they state that effect sizes, reported p-values and interpretations
are unchanged. We read that response but have not rerun their analyses. This
example therefore does not establish a consequential error merely because the
automated report flagged threshold crossings.

The response letter links this discussion but prints a different DOI. The PubPeer
page and archived inventory agree on `10.1037/a0036260`; that verified linkage
anchors the example. No DOI is repaired by guessing.

## Remaining acquisition

The public discussion page exposes its comment history, but the complete posting
roster has not been acquired. PubPeer's [official FAQ](https://pubpeer.com/static/faq)
says API access requires requesting a key. A credential-free query of the endpoint
used by its official browser extension returned a missing-key error; no
authenticated collection has been performed. A direct public DOI-search request
also returned HTTP 403. These are acquisition limits, not absent reports.

Before estimation, link each paper to its report, preserve original and revised
versions, verify dates and classify the alleged inconsistency against the original
text and any response. The inspected example establishes that this linkage is
possible, not the completeness or validity of the entire exposure roster. The
statcheck records do not yet enter the material-error synthesis.
