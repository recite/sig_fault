# Precision-weighted synthesis across three audits

The [four-study synthesis](assessments.md) adds psychology replication evidence and retains these three-audit estimates as a separately reported comparison.

The synthesis combines the Nieuwenhuis, Lal and Lazic contrasts on the log relative-growth scale, weighting each by the inverse of its estimated sampling variance. The I4R pilot is excluded from pooling; its three matched cases remain available as [standalone comparisons](../i4r/aggregate-results.md).

| IV definition | Lazic follow-up | Change, % | 95% interval | One-sided 95% lower bound, % |
| --- | ---: | ---: | ---: | ---: |
| Effective F below 10 | 2018 | -12.1 | [-24.5, 2.4] | -22.7 |
| Inferential sensitivity | 2018 | -2.1 | [-15.9, 14.0] | -13.8 |
| Effective F below 10 | 2019 | -10.7 | [-23.1, 3.7] | -21.2 |
| Inferential sensitivity | 2019 | -1.0 | [-14.7, 14.9] | -12.6 |

Nieuwenhuis uses 2010 and 2012; Lal uses 2023 and 2025; Lazic uses 2016 and 2018, with its later 2019 follow-up shown separately. Each row includes one contrast per audit. The IV definitions are alternative analyses of overlapping evidence. The weights and timing choices are retrospective, after inspection of component results.

The main fixed-effect interval uses the standard normal inverse-variance method and treats component variances as estimated inputs. It concerns the weighted mean of these included audit effects, not a prediction for a new audit. A causal interpretation additionally requires comparable untreated citation trajectories within the component designs.

## Weighting and heterogeneity

| IV definition | Lazic follow-up | Method | Change, % [95% interval] |
| --- | ---: | --- | ---: |
| Effective F below 10 | 2018 | Equal audit | -12.0 [-24.6, 2.7] |
| Effective F below 10 | 2018 | REML, modified Knapp-Hartung | -12.1 [-37.1, 22.8] |
| Inferential sensitivity | 2018 | Equal audit | -0.4 [-14.7, 16.1] |
| Inferential sensitivity | 2018 | REML, modified Knapp-Hartung | -1.3 [-38.6, 58.8] |
| Effective F below 10 | 2019 | Equal audit | -10.9 [-23.4, 3.7] |
| Effective F below 10 | 2019 | REML, modified Knapp-Hartung | -10.7 [-35.7, 23.9] |
| Inferential sensitivity | 2019 | Equal audit | 0.9 [-13.3, 17.3] |
| Inferential sensitivity | 2019 | REML, modified Knapp-Hartung | -0.1 [-36.8, 57.9] |

The random-effects sensitivity estimates between-audit heterogeneity by REML and uses modified Knapp-Hartung intervals with two degrees of freedom. The adjustment cannot shrink the standard error below its unadjusted value. Three audits supply little information about the distribution of effects across critiques.

See the [audit weights](../../data/meta/weights.csv), [leave-one-audit-out results](../../data/meta/leave_one_audit_out.csv), [component ledger](../../data/meta/lazic_components.csv), and [identity ledger](../../data/meta/lazic_component_identities.csv). No known Lazic DOI overlaps the other audit papers; one included Lazic paper has no DOI. [Methods](design.md) and [status](../../data/meta/status.json) document scope and assumptions. Run `make synthesis` to reproduce.

## Replacing the neuroscience citation source

The following comparisons replace the historical neuroscience counts with OpenAlex on the same papers and years. Each still contains three audits; different databases do not create independent studies. The main synthesis retains the historical source. These are source sensitivities, not estimates of database bias relative to a known truth.

| IV definition | Lazic follow-up | OpenAlex types | Three audits, % [95% interval] |
| --- | ---: | --- | ---: |
| Effective F below 10 | 2018 | Articles/reviews | -12.8 [-24.7, 0.9] |
| Effective F below 10 | 2018 | Broader types | -12.3 [-24.2, 1.5] |
| Inferential sensitivity | 2018 | Articles/reviews | -3.7 [-16.8, 11.4] |
| Inferential sensitivity | 2018 | Broader types | -3.1 [-16.3, 12.1] |
| Effective F below 10 | 2019 | Articles/reviews | -11.5 [-23.3, 2.1] |
| Effective F below 10 | 2019 | Broader types | -11.0 [-22.9, 2.7] |
| Inferential sensitivity | 2019 | Articles/reviews | -2.6 [-15.6, 12.4] |
| Inferential sensitivity | 2019 | Broader types | -2.1 [-15.1, 13.0] |

See the [paired citation-source comparison](../nieuwenhuis/README.md), [source-specific model estimates](../../data/nieuwenhuis/source_models.csv), and [synthesis data](../../data/meta/openalex_synthesis.csv).
