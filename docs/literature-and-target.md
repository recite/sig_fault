# Journal target and literature review

Working target: **Quantitative Science Studies**, subject to author preference.
The paper concerns scholarly communication and bibliometric evidence about uptake
of methodological criticism. QSS has published closely related work that combines
citation counts with citation-context evidence. Scientometrics is a reasonable
alternative. The contribution is a comparison across methodological audits;
failed-replication citations are pursued as a separate project.

## Format and comparable articles

Consulted the [QSS journal](https://direct.mit.edu/qss) and
[submission guidelines](https://direct.mit.edu/qss/pages/submission-guidelines).
The indexed official guidance specifies an abstract of at most 200 words,
up to six keywords, numbered sections, author–year references, and separate
contributions, conflicts, funding, and data-availability statements. Direct
publisher requests returned HTTP 403; indexed guidance may lag current policy.
Recheck before submission. Funding, conflicts, and author contributions require
the authors' factual input and have not been invented. A permanent archived release
identifier will be needed for the eventual submission; none is fabricated here.

Hsiao and Schneider, *Continued use of retracted papers* (QSS, 2021), and Woo and
Walsh, *On the shoulders of fallen giants* (QSS, 2024), provide the closest
structural models: motivate why citation behavior matters, explain the source
population and the meaning of citation measures, and separate citation counts
from interpretation of citation contexts. Neither establishes that continued
citation always endorses a criticized result.

## Claim-to-source review

| Reference | Appropriate use | Boundary |
| --- | --- | --- |
| Hsiao and Schneider, 10.1162/qss_a_00155 | Continued citations and acknowledgment of retractions in biomedical citation contexts | Retractions differ from the methodological audits analyzed here. |
| Woo and Walsh, 10.1162/qss_a_00303 | Citation behavior after retraction and variation in its diffusion | Does not identify the mechanism behind our audit contrasts. |
| Bordignon, 10.1007/s11192-020-03536-z | Distinguishes negative citations from criticism in post-publication review | Abstract and publisher metadata checked; no detailed full-text numerical claim used. |
| Serra-Garcia and Gneezy, 10.1126/sciadv.abd1705 | Citation levels and changes around replication outcomes | Includes a before/after Poisson comparison; must not be characterized as only cross-sectional. |
| Schafmeister, 10.1177/09567976211005767 | Citation-response design with external comparison articles | Its replication cohort overlaps other psychology replication analyses. |
| von Hippel, 10.1177/17456916211072525 | Citation response in the 98-paper psychology cohort | Same originals as our separate RPP analysis, not independent corroboration. |
| Clark, Connor, and Isch, 10.1073/pnas.2304862120 | Model-based citation declines after unsuccessful replications | All originals had unsuccessful replications; no successful-replication control group. Original code/data reproduction belongs to the separate replication-citations project. |
| Gelman and Stern, 10.1198/000313006X152649 | A difference in significance need not be a significant difference | Not a paper-level audit inventory. |
| Nieuwenhuis et al., 10.1038/nn.2886 | Interaction-testing error and source audit | Public article reports aggregate audit; supplied classifications identify originals, with permission. |
| Lal et al., 10.1017/pan.2024.2 | Instrument-strength and inferential-sensitivity diagnostics | Different diagnostics are not interchangeable and do not prove every flagged claim false. |
| Lazic et al., 10.1371/journal.pbio.2005282 | Experimental-unit/pseudoreplication assessment | Unclear classifications are not silently treated as correct. |
| Hainmueller et al., 10.1017/pan.2018.46 | Assessments of interaction-model assumptions | Severe diagnostic concerns are not a demonstration that every substantive conclusion is wrong. |
| Santos Silva and Tenreyro, 10.1162/003465306775565269 | Multiplicative conditional-mean modeling with PPML | The estimator does not establish a counterfactual by itself. |
| Open Science Collaboration, 10.1126/science.aac4716 | Distinguishing replication judgments from statistical-error audits | Not included in the methodological-audit synthesis. |

Primary full texts were checked for the main replication comparators and audit
sources. The earlier RPP analysis is a reanalysis/extension of overlapping prior
work, not a new independent replication cohort. It is excluded from the four-audit
paper's synthesis.

## Bibliographic validation

`scripts/references/01_get.py` retrieves DOI-specific Crossref records into
`data/references/crossref.json`, retaining raw responses and acquisition receipts.
`02_validate.py` parses BibTeX with Pybtex and checks ordered authors, title,
journal, print/publication year, volume, issue, pages/article number, DOI,
resolved citation keys, and unused entries against those frozen records.
The build uses the frozen records and does not require network access.

Hsiao and Schneider has a date discrepancy: one publisher-formatted citation
uses 2022, whereas the volume-2 record and Crossref print/online/issued dates
use 2021. The bibliography consistently uses the Crossref print year, 2021.
Metadata checks validate identity and bibliographic fields; the table above
records the separate semantic check of what the references support.
