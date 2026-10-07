# Synthesis of methodological audits

The manuscript combines four methodological audits: Nieuwenhuis, Lal, Lazic,
and Hainmueller–Mummolo–Xu. Psychology replication outcomes are a separate question
and do not enter this synthesis. This is a retrospective collection and analysis;
the source assessments and component estimates were inspected before synthesis.

The estimand is the inverse-variance mean of four study-specific log contrasts
between flagged and comparison papers' proportional citation growth. Each contrast
uses the calendar year before and after the selected publicity year, excluding
the event year. The windows are 2010/2012, 2023/2025, 2016/2018, and 2017/2019,
respectively. Formal journal publication is additional publicity for critiques
that circulated earlier. We do not claim these dates always identify the first
public disclosure or first time a reader could recognize a problem.

Use weak-instrument screening as the primary Lal diagnostic; substitute inferential
sensitivity in a separate estimate. Never count overlapping definitions as
independent audits. Exclude Vernby (2013) from the interaction-audit component
because it is already in Lal. Within each chosen window, all-zero papers remain
in source and descriptive records but do not identify the PPML contrast.

The main inverse-variance interval uses a normal reference distribution. A REML
random-effects sensitivity uses modified Knapp–Hartung uncertainty. With only four
selected audits, neither is a population estimate across all methodological
errors. Retain leave-one-audit-out results and substitute OpenAlex for the
historical neuroscience source on identical papers and years. Prior three-audit
estimates remain a component comparison; I4R's selected small pilot is excluded.

Components use article-clustered uncertainty. Within-audit citation levels,
medians, pre-trends, influential originals, comparison definitions and
measurement differences remain relevant; pooling cannot establish parallel
counterfactual trends or remove shared-topic dependence.

`scripts/meta/01_synthesize.py` reads the public components, reconstructs the
nonoverlapping interaction estimate, verifies DOI overlap, and records hashes
of source files, code and outputs. `methodological.R` generates all manuscript
values and the four-audit table. No replication citation data are inputs.
