# Synthesis estimand and inference

The target is the equally weighted average log relative citation-growth contrast in the two completed audits. Within each audit, the contrast compares flagged and comparison papers' post/pre citation ratios. Exponentiating the average gives the geometric average of those relative ratios. It does not give a pooled-paper ratio, an arithmetic average percentage change, or the effect of the typical error in science.

Use the calendar year before and after the warning year, excluding that year: 2010 and 2012 for the neuroscience critique; 2023 and 2025 for formal publication of the IV audit. The latter had circulated earlier, so this is not a shared first-exposure estimand. Historical neuroscience counts use Web of Science, whereas IV counts use OpenAlex articles/reviews. The mixed-source summary does not wait for all additional acquisitions, but retains these differences explicitly. A separate neuroscience 2009-publication cohort removes partial publication-year baselines.

For each synthesis, include one neuroscience contrast and one IV diagnostic contrast. The effective-F and inferential-sensitivity definitions are the two primary alternatives. Their union and the three-paper AR-only classification are secondary; the latter is exploratory. Never enter those overlapping diagnostics as independent audits. Equal audit weights define the summary rather than allowing sample size or citation dispersion to decide which critique dominates. These choices are retrospective and made with the component estimates already known.

The variance of the equal-audit mean is the sum of component variances divided by four, assuming independent audit estimates. A Welch–Satterthwaite approximation combines their article-cluster degrees of freedom. This is approximate because component variances are cluster-robust. Intervals condition on the included audits and classifications; they omit between-audit generalization uncertainty, unmeasured exposure, database error and specification selection. We do not estimate a heterogeneity distribution or a random-effects prediction interval from two critiques.

The two original-paper rosters have no shared DOI. That check prevents direct double counting but does not establish independence of all scientific processes or unobserved influences across the audits. Different citation windows also prevent a single dated citing document from contributing to both main outcome windows under consistent dates.

`R/meta.R` implements the fixed-audit average, variance, transformation and interval. `scripts/synthesis.R` assembles completed contrasts and regenerates the manuscript table, macros, data and report. Tests compare inference with an independently calculated Welch contrast, verify the geometric rather than arithmetic transformation, and reject multiple rows carrying the same audit identity.

An independent calculation reproduced every synthesis row, including standard errors, degrees of freedom, transformations and interval endpoints. These checks validate the calculation conditional on its inputs, not the publicity identification assumptions.

## Retrospective three-component sensitivity

Amendment recorded October 6, 2026 before calculating this additional proportional contrast. The existing audit estimates, four I4R case histories and absolute matched contrasts are already known. This is an exploratory extension with fixed cases, matches, outcome definitions and windows; it is not a preregistration or a replacement for the primary article/review collection.

The additional I4R component compares proportional growth in two equally weighted groups' mean citations. For each of the four supported disclosures, let the affected paper's count be `T[j,t]` and the within-case weighted control count be `C[j,t]`. Define `T[t] = mean(T[j,t])` and `C[t] = mean(C[j,t])`, using the full calendar years immediately before and after first documented disclosure. The component is `log(T[post]/T[pre]) - log(C[post]/C[pre])`. This is the same descriptive ratio-of-group-means functional as the existing components. Papers with more citations contribute more to proportional growth in group means; it is not the mean proportional response of individual cases.

Use a four-case delta-method variance, preserving covariance among the affected and control counts across periods within each disclosure. With vector `Z[j] = (Tpre,Tpost,Cpre,Cpost)` and gradient `g = (-1/Tpre,1/Tpost,1/Cpre,-1/Cpost)` evaluated at the group means, the variance is `g' cov(Z) g / J`. Use `J-1` degrees of freedom. This interval is exploratory: four selected disclosures cannot provide reliable general-purpose inference, and it conditions on the selected matches. If disclosure events recur or articles are reused across matched sets, withhold this variance until their dependence is handled explicitly. Individual zero counts require no adjustment; nonpositive group-period means make the proportional contrast unavailable. Do not add pseudocounts.

Report the four case-specific log ratios, their equal-case average as a differently weighted sensitivity, the preceding-year contrast and leave-one-disclosure-out results. A weighted article-fixed-effects/common-relative-period Poisson fit must reproduce the aggregate point estimate. Event-specific period effects estimate a different quantity and are not a computational substitute for this functional.

The additional synthesis averages the three component log contrasts with weights one third. Call it an **equal-component descriptive synthesis**: I4R combines several individually publicized errors and is not one methodological audit. Retain both primary IV diagnostics, the existing alternative definitions and the 2009 neuroscience cohort. Apply the same Welch approximation with the sum of squared-weight component variances. Check original and control DOI overlap across components before combining them. Unlike the original two-audit comparison, I4R and IV windows overlap, so even without shared original papers the zero-cross-component-covariance assumption is substantive. No independent-error estimate is reported if an original or control appears in multiple components.

This sensitivity preserves the I4R all-type outcome, Lal article/review outcome and historical neuroscience measurement. It also preserves their differing warning definitions and exposure dates. These discrepancies, selected I4R coverage, pre-period differences and the small number of disclosures prevent interpreting the combined quantity as the causal effect of publicizing a typical error. The primary two-audit synthesis and absolute I4R analysis remain separately reported.


## Citation-source sensitivity

The OpenCitations sensitivity substitutes its neuroscience estimate for the
historical Web of Science estimate on the same original papers and 2010–2012
window. It retains the two audit identities, equal weights, article-clustered
component standard errors and Welch degrees of freedom. OpenCitations is not
counted as another study. This retrospective check follows examination of the
completed source comparison and does not harmonize all document types with Lal.
The primary synthesis remains the historical estimate; source substitution
quantifies sensitivity in these assembled cases, not a general database-bias effect.
