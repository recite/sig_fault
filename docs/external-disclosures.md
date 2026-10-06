# External error disclosures

Of 47 primary-source reviews, 9 have an adjudicated material error and 7 have a supported public disclosure year. 5 pass both these checks and the article-age/follow-up restrictions for citation collection. None yet contributes a new matched effect estimate.

| Original paper | Public year | Material error | Collection status |
| --- | ---: | --- | --- |
| The Dynamic Effects of Personal and Corporate Income Tax Changes in the United States | 2016 | yes | Ready |
| Testing Efficient Risk Sharing with Heterogeneous Risk Preferences | Unresolved | yes | Disclosure year unresolved |
| Heterogeneity and Aggregation: Implications for Labor-Market Fluctuations | Unresolved | yes | Disclosure year unresolved |
| Risk Matters: The Real Effects of Volatility Shocks | 2014 | yes | Ready |
| Growth in a Time of Debt | 2013 | yes | Ready |
| Stationary Concepts for Experimental 2x2-Games | 2009 | yes | Insufficient pre-disclosure history |
| Antidumping Investigations and the Pass-Through of Antidumping Duties and Exchange Rates | 2010 | yes | Ready |
| The Impact of Legalized Abortion on Crime | 2005 | yes | Ready |
| The Effects of Canvassing, Telephone Calls, and Direct Mail on Voter Turnout: A Field Experiment | 2002 | yes | Insufficient pre-disclosure history |

## Definition and evidence

The exposure is the earliest substantiated public disclosure of a demonstrated material error in the original article. A correction can qualify when it changes a substantive magnitude without reversing the conclusion. The registry separates correcting a mistake from changing the specification or recalibrating a model.

Year precision supports annual analysis when that public year is established. An earlier manuscript or degree date alone does not. Dates are the earliest supported versions found, not proof that no earlier public warning existed. Search scope and uncertainty remain attached to each decision.

The original journal article must predate January 1 of disclosure year minus two. The first full post-disclosure year must be complete through 2025. Readiness for citation collection does not establish retraction eligibility, complete control acquisition, a usable match or parallel counterfactual citation trends. Those remain separate requirements under the [analysis design](i4r/design.md).

The [decisions](../data/inventories/disclosure_adjudications.json) record numerical consequences and hashed date sources. The [complete candidate table](../data/inventories/disclosure_candidates.csv) retains every reviewed case, including pending decisions and age exclusions. [Original metadata](../data/inventories/original_metadata.json) preserve inventory and journal DOIs separately. The underlying [primary reviews](../data/inventories/primary_reviews.json) contain error mechanisms and author responses; original analyses were not rerun.

Run `make inventories-test` for an offline rebuild and eligibility tests. `python3 scripts/inventory_events.py fetch-metadata` separately refreshes publication metadata from Crossref, checking DOI and title agreement. Error and disclosure decisions require source review and are never inferred from citation outcomes.
