# Verification of the RPP citation analysis

The completed offline build verifies 98 original identities, 374 candidate control
papers, 472 completed citation histories, 95,223 citation links and 8,496
paper-year records. Four currently retracted control papers are excluded before
matching, leaving 370 eligible donors. Every original receives external controls.
The [stage receipts](receipts/) record the inputs, executed checks and outputs.

An independent reconstruction reproduced the four journal-standardized level and
proportional contrasts, the Welch standard errors and degrees of freedom, and the
annual standardized means. A separate 100,000-draw bootstrap gave a primary
proportional interval of −26.92% to −3.25%, consistent with the pipeline's fixed
9,999-draw interval of −27.06% to −3.38%.

The nearest-neighbor coefficients and two-way clustered standard errors were
reproduced with reused control identities and the stated finite-sample correction.
Independent raw-count synthetic fits reproduced the final annual contrasts:
−1.879875674 for unsuccessful replications and −0.872788763 for successful
replications. These synthetic estimates have no reported confidence intervals.

Dropping all citation links with conflicting records for the same citing DOI
changed the primary contrast from −1.18659 to −1.18375 annual citations and from
−15.8920% to −15.8828%. Canonical OpenAlex resolution reconciles provider records;
it does not independently verify publisher dates.

Local validation passed the repository's `make check`, final `make lint`, the
13 Python pipeline tests and five R assertions, followed by the full offline
`make rpp` build. Tests include upstream receipt invalidation, failed-stage
rejection, independence of matching from post-period counts, and a regression
check that synthetic fitting and prediction use the same raw-count scale.

The analysis concerns additional project publicity in August 2015. Earlier report
filenames and upload logs are retained as timing candidates; their contents and
historical visibility do not yet establish the first disclosure date for each
paper. This timing limitation is separate from successful execution of the
pipeline. The [design record](design.md) explains source corrections and analysis
changes made during implementation and review.
