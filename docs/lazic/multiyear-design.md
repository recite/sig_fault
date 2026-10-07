# Longer citation histories around the 2017 disclosure

This retrospective extension asks whether the citation change around the September
2017 public release persists when annual fluctuations are averaged over several
years. Existing annual summaries and earlier estimates have already been seen.
This is not a preregistered or blinded analysis. The current pooled estimate is
retained, and this extension will not replace it based on its sign or precision.

## Population and timing

Use original articles classified as pseudoreplicated or correctly analyzed in the
Lazic audit, excluding the already documented 2013 warning. Require original
publication before 2014 so every paper has three complete baseline calendar years
(2014–2016). Retain the same articles for every main comparison. Exclude 2017,
which contains the preprint and dataset release. Use 2018–2020 as three complete
follow-up years. The paper's journal publication in 2018 is additional publicity;
this window cannot separate its effect from that of the 2017 release.

Retain original identities and classifications; require complete citation histories
and unique article/year keys. Never interpret missing histories as zero citations.
The source inventory identifies 50 flagged and 26 comparison articles eligible by
publication year. These counts were inspected before estimating this extension.
Citations come from the existing OpenCitations histories, all indexed document types.
Publication year uses the inventory's earliest recovered publication date.

## Quantities to estimate

1. The difference between groups in the change in mean annual citations from
   2014–2016 to 2018–2020. Each article has equal weight within its group. Report
   mean and median levels, the difference, and a Welch interval computed from
   article-level changes. This targets the average change among eligible flagged
   papers only if comparison papers represent their absent-publicity trajectory.
2. The proportional contrast from a Poisson model with article and calendar-year
   fixed effects, an indicator for flagged × follow-up, and article-clustered
   uncertainty. Report the existing finite-sample adjustment and t reference with
   contributing articles minus one degrees of freedom. This is a model-based
   common proportional contrast, not an equal-weight average of heterogeneous
   percentage effects. All-zero papers remain in descriptions and are reported
   separately when dropped from estimation.
3. A publication-cohort-by-calendar-year fixed-effect version of the proportional
   model. It permits each publication cohort to age differently. Report group
   support by cohort; this does not adjust for different topic trends within a cohort.

For comparison with the current synthesis, estimate 2016 versus 2018 on the same
eligible papers. This separates a window change from a sample change. The full
original sample's existing adjacent-year estimate remains separately reported.

## Earlier trajectories and sensitivity

On the same eligible set, compare 2014 with 2016, both before known disclosure,
using additive and proportional contrasts. Also tabulate annual group means and
medians for every year from 2014 through 2020. Report year-specific proportional
contrasts versus 2014 for 2015, 2016, 2018, 2019 and 2020. These intervals are
pointwise descriptions, not a family of independent confirmatory tests.

Report 2018–2019 as a shorter-follow-up sensitivity that omits 2020. Assess whether
results depend on follow-up duration; do not choose the most precise window.
No matching, synthetic controls, trend extrapolation or new exclusions will be
added after inspecting these results in this stage.

## Interpretation and dependence

A causal interpretation requires comparable absent-publicity trajectories on the
chosen additive or proportional scale. Earlier trajectory checks can contradict
that assumption but cannot validate it. All articles share one audit release;
article-level inference describes cross-paper variation conditional on that event,
not uncertainty over a population of independent publicity events. Shared citing
papers can also correlate outcomes across originals. The intervals do not include
bias from confounding or uncertainty about exposure to the critique.

Each numbered stage records input/code/output hashes and checks. Report every
specified comparison, sample disposition, window and uncertainty convention.
