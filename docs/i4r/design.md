# Effect of publicizing significant errors

Design frozen on 2026-10-05 before collecting I4R citation outcomes. Existing Nieuwenhuis and Lal citation results, I4R abstracts, and some source reports have been examined. This is a dated analysis plan, not an external preregistration.

The primary estimand is the average effect, among supported affected articles, of publicly disclosing a demonstrated material error on citations in the first full calendar year after disclosure, compared with no disclosure. The unit is the original article; the exposure is the first documented public disclosure of the particular error. An error existing and an error becoming public are different events. The registry covers the full discoverable I4R collection; estimation eligibility is a separate, reported restriction.

## Classification

A main-cohort error must be a demonstrated coding, data, or statistical mistake that materially affects a substantive finding. Evidence must identify the erroneous operation, affected claim, and consequence. A material correction can strengthen as well as weaken an estimate; affected papers are not automatically refuted papers. Record the direction and scope in the affected claim and evidence summary. Author acknowledgment is not required; replies and disputes remain attached. A robustness failure, nonsignificant replication, incomplete package, or numerical mistake with negligible consequences alone does not qualify. These receive separate categories. No classification is inferred solely from the old abstract scores, a keyword, or a model-generated probability.

Adjudication clarification (2026-10-06): a demonstrated change to a substantively interpreted magnitude can qualify even when the direction and broad conclusion survive. This applies symmetrically to strengthening and weakening corrections. Record the actual original and corrected values, whether the affected claim is central or secondary, and whether the comparison isolates an error repair or also changes analytical choices. No percentage-change cutoff is introduced. A rounding discrepancy or significance-label change alone is insufficient; judgments about borderline substantive importance remain explicit. These decisions were made before any I4R matched effects were estimated.

The public article registry, source documents, source–article links, claim assessments, and disclosure events have separate keys. Multiple critiques do not multiply the original article. Preserve revisions and replies as related evidence, not independent treated papers. Source URLs, precise locations, and document hashes support every verified assessment. Ambiguous identities, materiality, and timing remain unresolved rather than becoming negative labels.

Use the earliest substantiated public version containing the particular error disclosure, including preprints and linked earlier critiques. A repository creation or file-upload date does not establish public availability. Record date precision and search scope. Unknown day/month can support calendar-year estimation only when the public year is substantiated. A publication-year field on a current revision alone does not establish the first disclosure year.

## Coverage

Reconcile I4R's reports and discussion-paper catalogs with both RePEc series pages as of 2026-10-05. Count catalog entries, distinct documents, original articles, assessed findings, and disclosure events separately. Keep retrieval failures and unresolved records. Account for every catalog entry; at least 90% of eligible article-specific assessments must be resolved before labeling coverage substantially complete. Coverage is not demonstrated by downloading 90% of files. Newer studies with insufficient follow-up remain in the registry.

## Controls

The primary risk set comprises same-journal, same-type articles indexed as published within one year of the affected article. Use OpenAlex years for both sides of that retrieval/matching restriction; use separately verified publisher dates for the full-pre-year age restriction on both sides. Preserve both clocks rather than comparing a treated publisher year to a control indexing year. Articles already publicly assessed are excluded; later public assessments terminate their eligibility for subsequent horizons. Unknown error status is not evidence of error-free research. Screens cover the assembled I4R registry and known retraction/update records, and their incompleteness is reported.

Match with replacement, up to three controls per affected article, using only pre-disclosure information. Standardized Euclidean distance uses log(1 + citations) in the two complete pre-years, their change, and cosine distance of original title/abstract text. Each component receives equal weight after scaling over the eligible risk set plus treated article. Each citation component must lie within one pooled standard deviation; zero-variance components require equality and contribute zero distance. Stable article IDs break ties. No automatic journal expansion. Missing abstracts use titles, with this limitation flagged. Retain candidate distances, selected weights, exclusions, and unmatched affected articles. Each treated article has total weight one and its controls combined weight one.

## Outcomes and estimation

Count deduplicated incoming journal-article/review citation relationships using complete calendar years through 2025. Missing or incomplete retrieval is not zero. The primary contrast is the equal-treated-weight average of (treated year +1 minus year -1) minus the same weighted control change. Exclude disclosure year 0. Require two complete pre-years and one complete post-year, with original publication before the first pre-year starts. Collect at least three pre-years when the article age permits.

Implement using first differences and stack fixed effects, algebraically equivalent to stacked two-period fixed effects: article-within-stack and stack-by-period effects; treated × post coefficient; treated weight 1 and each control weight 1/k. Two-way cluster by original article and shared disclosure event, with original IDs retained when controls recur. Use explicit finite-sample adjustment, reporting both cluster counts, influential events, and conditional-on-match inference. No already-exposed article serves as an unexposed control. Verify the coefficient against direct matched differences.

Report means, medians, absolute estimates and two-sided 95% intervals. Report +2/+3 horizons for complete fixed cohorts and show +1 on those same cohorts. Secondary checks: +1/+2 average, year -2 to -1 placebo (matching makes this a weak diagnostic), earlier pretrends where available, disclosure-month timing, alternative baseline averaging, one versus three controls, and leave-one-disclosure-event-out estimates. Broad adverse assessments and favorable-assessment comparisons are secondary and never relabeled demonstrated-error effects.

Exclude articles already retracted when the error was publicized. Later retractions remain in the total-effect estimate, because they may result from publicity; mark their contribution and report a restricted descriptive sensitivity without claiming it estimates the same total effect.

Parallel counterfactual trends and absence of anticipatory citation changes/differential contemporaneous shocks are identifying assumptions. Selection for replication, prior private awareness, and endogenous publicity may violate them. Matching and fixed effects do not establish causality. Short-run citations may come from manuscripts written before disclosure. Total citations do not identify reliance on the erroneous claim. A nonsignificant result does not establish no effect. If few independent warnings or poor support prevent reliable inference, report the observed contrasts and limitations without a confident causal headline.

## Deliverables and deviations

Source-complete inventory first; verified article/assessment/event tables second; standalone matching and analysis third. Keep every eligibility loss visible. No effect is reported from unverified classifications. Log changes to this specification with reasons and label resulting analyses appropriately.

Implementation note: estimate the two-period model in first differences to avoid redundant fixed-effect rank counting in disconnected matched stacks. Tests require exact equality with the direct matched change. This changes the computation, not the estimand.

Acquisition-completeness clarification (2026-10-05): matching waits for pre-disclosure citation histories for every otherwise eligible control in a retrieved risk set. A partly downloaded pool must not change candidate rankings or the scaling/calipers. Candidate metadata and age exclusions remain explicit. This gate was tightened before estimating the I4R matched contrasts.
