# Comparing papers from the same journal and publication year

The neuroscience comparison uses papers from the same source audit, published in
five journals in 2009–2010. The audit classified whether their comparison of
statistical effects used the erroneous argument. All ten journal/publication-year
groups contain both flagged and comparison papers. This extension uses those
comparisons directly, rather than controlling separately for journal and age.

The target is the proportional change in citations attributable to the 2011
publicity among the covered audited papers. We estimate a common proportional
contrast with article fixed effects and journal × original-publication-year ×
citation-year fixed effects. Each journal/publication-year group can have its own
citation trajectory. Identification requires flagged and comparison papers in the
same group to have followed comparable proportional trajectories without publicity.
Article fixed effects account for their different baseline levels. The comparison
is differential exposure to the critique: unflagged audited papers are not assumed
to be wholly unaffected by the methodological discussion.

Use the established 153-paper sample and complete 2010 baseline versus annual
2012–2015 follow-up observations, excluding the 2011 transition year. Here
"complete baseline" means complete citation collection for the calendar year;
2010 originals are not available throughout that year. Report the 2009-original
cohort separately, with a full calendar year after original publication. Report
2010 versus 2012 for comparability with the existing synthesis, without substituting
it for the longer-follow-up estimate based on results.

Estimate both the proportional model (Poisson pseudo-maximum likelihood) and the
additive model (linear fixed effects). The latter compares changes in citation
counts, not proportional changes. Both impose a common coefficient; neither is
an equal-weight average of heterogeneous effects across papers. Use article-clustered
standard errors, the existing nonnested finite-sample adjustment and t(G−1)
reference. This describes cross-article uncertainty conditional on the one critique.

Run the same specifications on the paired Web of Science and OpenAlex counts.
The paired source panel is a public analytical input. Require unchanged identities,
classifications and windows across sources. Record every dropped all-zero paper.
The original historical exclusion decisions remain fixed.

Keep Figure 1's raw mean and median trajectories. Add mean and median trajectories
standardized to the flagged papers' journal/publication-year distribution: each
flagged paper receives weight one; each comparison paper in a group receives
n_flagged/n_comparison. Compute the weighted median as the first count at which
cumulative normalized weight reaches one half. These are descriptive distributions,
not regression-adjusted potential outcomes. Their weights use no citation outcomes.

Report annual within-group proportional contrasts for 2011–2015 versus 2010,
including 2011 as a transition-year diagnostic only. Intervals are pointwise.
A 2009 versus 2010 diagnostic on 2009 originals compares a partial publication
year with a full year; report it with that interpretation, not as a decisive
parallel-trends test. There is no long unexposed history for papers published
in 2009–2010. The design instead relies on substantive comparability within the
same journal/publication year and transparent sensitivity checks.

This extension is retrospective. Figure 1, original estimates and source comparisons
were already inspected. No matching thresholds or samples will be chosen from the
new estimates. The separate Lazic multiyear design is recorded but has not been
estimated; the user's instruction prioritizes this journal/year comparison.

Implementation follows the official fixest documentation for
[fixed-effect combinations](https://lrberge.github.io/fixest/reference/feglm.html) and [small-sample corrections](https://lrberge.github.io/fixest/reference/ssc.html).
