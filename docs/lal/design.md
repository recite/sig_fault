# Citation trajectories after the Lal et al. IV audit

This extends the Nieuwenhuis citation study to a second methodological critique. The population is all 67 papers (70 assessed designs) in Lal, Lockhart, Xu, and Zu's deposited replication file. The question is whether papers with adverse diagnostics subsequently receive fewer citations, relative to other papers assessed by the same audit. Citation-context coding is a separate extension and is not required to estimate citation trajectories.

## Status and prior exposure

This retrospective design was recorded on October 5, 2026 UTC before collecting the expanded cohort's citation histories or estimating its models. Ten papers' incoming citation records and sampled passages were already examined in the context pilot: Acharya2016, Alt2015, Carnegie2017, Gelbach2012, Grossman2017, Hager2022, Pianzola2019, Schleiter2016, Sexton2019, and Urpelainen2022. This is not a preregistration or a blinded analysis. An independent read-only design review identified the three-paper AR-loss subgroup, citation-aging and timing problems, and the need to separate absolute and proportional changes; these are incorporated below.

## Comparisons

Retain one citation history per paper. A paper satisfies a diagnostic if any assessed design does. Preserve the underlying design records and any mixed assessments.

1. Weak-instrument screen: effective F below 10 (8 papers), compared with the other assessed papers. This is a diagnostic threshold, not proof of a false conclusion or a universal weak-instrument criterion.
2. Inferential sensitivity: at least one analytically significant estimate (p<.05) becomes nonsignificant under archived AR or applicable tF inference. Restrict the comparison to papers with at least one analytically significant estimate. Report AR-only separately: only three papers meet that narrower definition, so display their individual paths and leave-one-flagged-paper-out estimates.
3. Secondary broad screen: either weak F or inferential sensitivity, compared with other assessed papers. This reproduces the context pilot's recruitment rule (17 versus 50 papers).

These labels describe recorded diagnostics, not error-free and erroneous papers. The corrected Alt AR p-value (.1747 instead of .9671) leaves its AR-loss category unchanged. Its eight-level instrument has seven excluded indicators; its archived single-instrument tF calculation is inapplicable. Remove that tF component from classification. Other unverified audit diagnostics remain explicitly source-based; the ten selected point-estimate replications do not validate all 70 designs. Report analyses excluding Alt and Carnegie (whose reproduced covariance has a numerical warning), and Hager (which has a published corrigendum), as a sensitivity rather than silently discarding them.

## Dates and citation histories

The first author manuscript is dated July 10, 2021; the identifiable replication archive was released February 17, 2024; the journal article appeared online May 3, 2024. The 2024 analysis therefore describes evolution around formal publication, not exposure to a previously unknown warning. Papers and drafts may have circulated earlier, and the audit itself changed over time.

Resolve every target identity before collection. Retrieve all incoming OpenAlex records dated through December 31, 2025, require complete pagination and reference membership, and preserve source responses. No failed retrieval becomes a zero. Deduplicate same-DOI incoming records by earliest date and then work ID; retain raw duplicates and their dispositions. Different-DOI versions remain a documented limitation. The primary outcome includes articles, reviews, preprints, proceedings articles, and book chapters; all database document types are a sensitivity. Match the DOI-specific target version; inspect any prepublication citations and do not assume they are errors merely because they predate journal publication.

Create post-publication paper-year counts with covered zero years included. The main balanced comparison uses 2023 and 2025 for papers published by 2022; exclude the 2024 transition year and the incomplete 2026 calendar year. For trajectories, show a fixed cohort published by 2016 over 2017–2025, alongside a full-cohort 2023–2025 summary. Never fill prepublication years with zeros.

## Estimation and checks

Lead with equal-paper means, medians, and distributions of within-paper citation changes. The principal model is PPML with article and calendar-year fixed effects and the diagnostic-by-post interaction. Its exponentiated coefficient describes the groups' relative post/pre citation ratios, not an absolute citation loss. Use explicit `fixest` small-sample conventions and article-clustered covariance; report the number of flagged papers and model-specific exclusions. Approximate clustered intervals are particularly fragile with only three AR-loss papers. Do not interpret failure to reject zero as evidence that publicity has no effect.

Report absolute-change OLS with HC3 uncertainty alongside PPML. Sensitivities: 2022 rather than 2023 baseline; 2025 versus a 2022–2023 mean baseline; journal-by-year effects; publication-year-by-year effects where supported; all document types; exclusion of the three audit/correction concerns above; and leave-one-flagged-paper-out estimates. Display pre-period trajectories and an adjacent 2022–2023 placebo contrast; neither a nonsignificant pretrend nor fixed effects establish parallel counterfactual paths. Describe a separate early-circulation comparison using a cohort published by 2019, 2020 baseline, and 2022–2023 follow-up; it is not a substitute for verified article-specific exposure dates.

Expected direction under citation penalties is negative relative growth. Large declines, increases, or no discernible pattern will all be reported. No model or cohort is chosen based on the sign. These estimates are descriptive associations unless a stronger exposure design becomes available. Alternative diagnostics and windows are an exploratory family, not independent confirmatory tests.

## Multiple critiques

Use one common data and reporting structure across audits, while retaining each critique's specific allegation and assessed comparison group. Estimate each audit separately before summarizing across them. Report equal-audit and equal-paper weighting as different quantities, track papers appearing in several audits, and preserve uncertainty in warning dates. A broader set of critiques improves scope but is not automatically representative of all scientific errors. Avoid a pooled staggered two-way-fixed-effects coefficient that obscures incompatible definitions and comparisons.

The next candidate is Hainmueller, Mummolo, and Xu's interaction-model audit. Before inclusion it needs an identifiable assessed-paper roster, article-specific diagnostic classifications, a defensible comparison group, and a documented public-warning timeline. These are inclusion requirements established before examining citation effects, not a search for more null findings.

## Deviations

Any changes required by unresolved identities, source diagnostics, complete-year coverage, or estimator failures will be recorded here with their reason.
