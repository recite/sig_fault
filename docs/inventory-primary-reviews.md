# First reviews of the error candidates

The complete reproduction-excerpt screen supplies candidates for primary-source
review. The [review table](../data/inventories/primary_review_summary.csv) covers
older reports, their original-paper identities and available author responses.
Some document acknowledged coding errors; others reveal specification disputes or
remain limited by inaccessible full texts. None has yet been added to the
citation-effect sample. The inventory report gives current coverage counts.

The [structured reviews](../data/inventories/primary_reviews.json) retain the error
mechanism, affected claim, exact source locations, response, date evidence,
unresolved questions and source hashes. These are readings of the reports, not
independent reruns of the original analyses. Each record states its access and
verification limits. The cases below illustrate the distinctions; the linked
table contains every completed review, including unresolved findings.

| Original paper | What the primary sources establish | What remains before estimation |
| --- | --- | --- |
| Dahl and Lochner, family income and child achievement | The authors acknowledge that their income measure omitted EITC payments after a TAXSIM variable changed meaning. Correcting income reduces the estimated effect by about 30%; the positive finding remains statistically significant. | Recover the earliest public report of the coding error. A 2016 correction predates the journal exchange, and it refers to a 2015 critique. The recovered 2015 news item discusses a separate sample-period issue. |
| Bloom, Draca and Van Reenen, trade-induced technical change | The authors acknowledge coding errors in a patent-count robustness check. The corrected coefficient is smaller and imprecise; they defend the broader conclusions using additional controls and other results. | Resolve earlier working-paper versions and isolate the affected robustness claim from the wider specification dispute. A 2020 public working paper precedes the 2021 journal comment. |
| Herring, workplace diversity and business performance | The comment finds sample-size discrepancies consistent with possible miscoding of missing values, but cannot reconstruct the original sample even when reproducing that proposed mistake. Its largest change in conclusions also requires log transformations. | Establish the mechanism and review the complete author reply. Keep the missing-data discrepancy separate from the functional-form disagreement. |
| Engel, dictator-game meta-analysis | The comment identifies SD/SE and data-entry problems. Its changed result about allowing participants to take money also incorporates changes to the treatment of negative giving. | Isolate the consequence of correcting the hard errors while holding the outcome definition fixed. The earliest identified public posting is in 2012, before the final journal publication. |

Sources: Dahl and Lochner's [correction](https://econweb.ucsd.edu/~gdahl/papers/children-and-EITC-correction-addendum.pdf)
and [reply](https://econweb.ucsd.edu/~gdahl/papers/children-and-EITC-reply.pdf);
Campbell and Mau's [comment](https://doi.org/10.1093/restud/rdab037) and
Bloom et al.'s [reply](https://wrap.warwick.ac.uk/id/eprint/150603/1/WRAP-A-reply-Campbell-Mau-Draca-2021.pdf);
Stojmenovska et al.'s [comment](https://doi.org/10.1177/0003122417714422) and
Herring's [reply record](https://doi.org/10.1177/0003122417716611);
Zhang and Ortmann's [working paper](http://research.economics.unsw.edu.au/RePEc/papers/2012-44.pdf)
and [published comment](https://doi.org/10.1007/s10683-013-9375-7).

A date printed on a manuscript does not establish when readers could access it.
The reviews therefore retain competing date evidence rather than assigning the
journal year by default. Likewise, a critique that combines a coding correction
with a new specification does not establish the effect of the correction alone.
Those distinctions determine the eventual exposure and the claim it concerns.
