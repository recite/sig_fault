# Citation changes after adverse scientific assessments

Across five studies, the inverse-variance weighted contrast is
**-14.4% [-22.5, -5.5]**:
papers receiving adverse assessments had lower post/pre citation ratios than
comparison papers. Brackets contain 95% intervals. This combines four methodological
audits with the psychology replication project. It summarizes the included studies;
it is not an average effect for all scientific errors.

## Studies and weights

The main specification uses the weak-instrument diagnostic in the political-science
audit. Its five components contain 465 contributing original papers.
The animal-study Poisson fit omits papers with zero citations in both selected years;
those papers remain in the descriptive summaries.

| Study | Adverse / comparison | Change (%) [95% interval] | Weight (%) |
| --- | ---: | ---: | ---: |
| Neuroscience | 76 / 77 | -14.1 [-32.8, 9.7] | 16.8 |
| Instrumental variables | 8 / 59 | -14.5 [-36.0, 14.2] | 12.3 |
| Animal studies | 82 / 45 | -7.2 [-29.4, 21.9] | 13.5 |
| Psychology replications | 59 / 39 | -15.9 [-27.1, -3.4] | 50.0 |
| Interaction models | 13 / 7 | -17.3 [-43.9, 22.0] | 7.5 |

The psychology component compares 59 unsuccessful with 39
successful replication judgments, standardized to the full cohort's journal shares.
Its estimate is -15.9% [-27.1, -3.4]; its share of the primary
pool is 50.0%. Nonreplication is not classified as a statistical error.
Favorable replication publicity may raise comparison citations, so this contrast
cannot separate that benefit from an unsuccessful-replication penalty.

The interaction component compares severe-extrapolation labels around the audit's
2018 journal publication. It omits Vernby (2013), already in the IV component, and
its Poisson model omits one paper with zero citations in both selected years.
The source audit circulated earlier, so this is an additional-publication contrast.

## Scope and weighting comparisons

| IV definition | Three audits (%) [95% interval] | Five studies (%) [95% interval] | Five, random effects (%) [95% interval] |
| --- | ---: | ---: | ---: |
| Effective F below 10 | -12.1 [-24.5, 2.4] | -14.4 [-22.5, -5.5] | -14.4 [-25.7, -1.5] |
| Inferential sensitivity | -2.1 [-15.9, 14.0] | -10.4 [-18.8, -1.0] | -8.7 [-24.7, 10.8] |

The alternative IV definition substitutes sensitivity of statistical significance
for instrument strength. It never contributes a second independent study. The
three-audit column preserves the narrower methodological-assessment comparison.
The random-effects column uses REML and modified Knapp–Hartung intervals with four
degrees of freedom. Both pooling methods summarize study-level contrasts;
neither makes the exposure or comparison populations identical.

## Estimand and timing

Within each study, the outcome is the ratio of adverse-group post/pre mean citations
to comparison-group post/pre mean citations. Psychology averages journal-specific
log ratios with fixed journal shares. Pooling then averages study log ratios with
inverse estimated sampling-variance weights. Percentages are obtained by
exponentiating the pooled log ratio. They are not annualized growth rates or
percentage-point differences.

The established windows are 2010 versus 2012 for neuroscience, 2023 versus 2025 for
the IV audit, 2016 versus 2018 for animal studies, and 2012–2014 versus 2016–2018 for
psychology, and 2017 versus 2019 for the interaction audit. All omit the announcement year. The psychology, IV and interaction announcements
can amplify earlier reports. A causal interpretation requires comparable untreated
proportional trajectories within each study; the data do not measure individual
readers' exposure to criticism.

## Timing and citation-source sensitivity

| IV definition | Psychology window | Neuroscience source | Five studies (%) [95% interval] |
| --- | --- | --- | ---: |
| Effective F below 10 | primary | historical | -14.4 [-22.5, -5.5] |
| Effective F below 10 | primary | openalex | -14.6 [-22.6, -5.9] |
| Effective F below 10 | adjacent_years | historical | -12.3 [-21.6, -1.9] |
| Effective F below 10 | adjacent_years | openalex | -12.7 [-21.8, -2.6] |
| Inferential sensitivity | primary | historical | -10.4 [-18.8, -1.0] |
| Inferential sensitivity | primary | openalex | -10.8 [-19.1, -1.6] |
| Inferential sensitivity | adjacent_years | historical | -7.0 [-16.9, 4.0] |
| Inferential sensitivity | adjacent_years | openalex | -7.7 [-17.2, 3.0] |

`adjacent_years` uses 2014 versus 2016 for psychology. `primary` uses the established
three-year windows. OpenAlex replaces the historical neuroscience source on exactly
the same papers and years, with newly calculated precision weights. It is never
counted as another study. [Paired source comparisons](../nieuwenhuis/README.md)
measure database discrepancies, not bias against a verified citation census.

## Reproduction

Run `make synthesis` to rebuild component analyses and this report from public
frozen data. It requires no API key or private download cache. The
[numbered synthesis script](../../scripts/meta/01_synthesize.py) records actual
input, code and output hashes in its [receipt](../../data/meta/receipts/01_synthesize.json).
The psychology component is recomputed from its public annual panel and checked
against the study's estimates. Acquisition and full source-chain verification remain
in the [study pipeline](../../scripts/rpp/README.md).

The [design](assessment-design.md), [component estimates and weights](../../data/meta/assessment_components.csv),
[leave-one-study-out results](../../data/meta/assessment_leave_one_out.csv), and
[original-paper identities](../../data/meta/assessment_identities.csv) document scope
and checks. Vernby (2013) appears in both the IV and interaction audits. The interaction
component excludes it; no known original DOI overlaps the resulting five components. This does not rule
out shared citing papers or correlated field shocks. These analyses are retrospective.
