# Assessing comparability and estimation weights

The main design compares papers from the same journal and original-publication
year. This second stage examines the assumption that flagged and comparison papers
would have had comparable citation changes absent the critique. It does not treat
error status as randomized. Balance is evidence about observed comparability, not
a randomization test or proof about unobserved characteristics.

## Predetermined characteristics

Read the supplied audit classifications directly, preserving the original labels.
Normalize human/humans, mice, rat/rats, and monkey/monkeys into human, mouse, rat
and nonhuman-primate groups. Other observed species remain other; blank species
remains unknown. Use the supplied within/between-subject classification. Define a
US-author-country indicator from the normalized source label US. Retain original
country, species and design labels in the public analytical file.

Compare these characteristics and 2010 citation counts in the unweighted sample
and after standardizing comparison papers to the flagged papers' journal/year
composition. Report means, differences and standardized mean differences using
the original full-sample pooled within-group standard deviation as a fixed
reference. Also report log(1 + baseline citations). No p-value is interpreted as
showing balance. Different baseline levels are permitted by the fixed-effects
models; the baseline citation measures assess whether that assumption is doing
substantial work.

The initial diagnostic found that 25% of flagged papers study humans, versus about
55% of journal/year-standardized comparison papers. As a prespecified response to
this observed imbalance, estimate a sensitivity comparison within journal ×
publication year × human/nonhuman/unknown × within/between-subject groups. This
choice uses source characteristics and the observed balance diagnostic, not the
new post-publicity estimate. Keep cells containing both classifications and
report every inclusion decision. No citation-based matching threshold is chosen.
The resulting estimand concerns supported papers; it is not silently extrapolated
to excluded originals. The main journal/year design remains reported. On the retained sample, first
repeat the journal/year-only model and then add the study-type groups. This
separates the change in population from the additional adjustment.

## Weighting and estimands

With one common publicity date and a balanced panel, the linear article and
group-by-year fixed-effect coefficient is a convex combination of group-specific
additive differences in changes. Group weights are proportional to
n_flagged × n_comparison / (n_flagged + n_comparison). Publish the weights and
verify the identity. There are no staggered treatment dates in this design.

For Poisson estimation, report each group's share of working-model information:
residualize flagged × post on the fixed effects using fitted-mean weights and
sum fitted_mean × residualized_treatment² within each group. These are local
information weights describe curvature of the Poisson objective, not the robust
sampling variance or an exact representation of a heterogeneous causal average. Do not label them article probabilities or treatment-assignment weights.

Also report an explicitly equal-flagged-paper additive contrast: weight each
group-specific difference in mean changes by its share of flagged papers. Every
flagged paper has outcome weight 1/N_flagged; comparison papers share their
group's counterfactual weight equally. Verify the point estimate both directly
and through weighted least squares on article changes, with group fixed effects
and computational weights (n_flagged+n_comparison)/n_comparison. The WLS weights
are a way to compute that contrast, not the displayed outcome weights.

Use HC3 uncertainty for the article-level weighted regression, with residual
degrees of freedom. This is a model-based small-sample approximation conditional
on the observed groups and weights; no random assignment is claimed. Report
single-observation cells and influential control weights. Keep the common-effect
PPML and linear models alongside the equal-flagged-paper additive estimate.

Run both citation sources on identical classification-based samples. The
characteristic construction, exclusions, weights, balance, estimates and receipts
are reproducible. This is retrospective design improvement; the original
citation trajectories and journal/year estimates were already seen.

For the equal-flagged additive contrast, the identifying restriction is
E[change in citations without the critique | flagged, cell] =
E[change in citations without the critique | comparison, cell], along with no
anticipation in the baseline. Under this restriction, fixed classification-based
weights identify the average differential response among supported flagged papers.
Interpreting it as the critique's total effect on those papers additionally requires
that comparison papers did not themselves gain or lose citations because of the
critique. The proportional model instead requires the corresponding multiplicative
mean restriction. Neither restriction follows automatically from balance.

The first balance table also shows that matching human/nonhuman status leaves a
mouse-study imbalance (standardized difference about 0.61). Before estimating a
species-specific contrast, add exact species to the group definition, retaining
within/between-subject design. This retains 49 flagged and 46 comparison papers
in 19 supported cells. Report both the original journal/year adjustment on these
same 95 papers and the species/design adjustment. Keep the broader estimates;
the stricter comparison has a narrower target population. No further covariates
or cutoffs are added in this diagnostic stage.
