# Three-audit synthesis

The synthesis gives equal weight to the Nieuwenhuis, Lal and Lazic audit contrasts on the log ratio-of-ratios scale. It summarizes these assembled audits, not a random sample of publicized errors. I4R remains a separate four-component sensitivity.

| IV definition | Lazic follow-up | Three audits, % [95% interval] | With I4R, % [95% interval] |
| --- | ---: | ---: | ---: |
| Effective F below 10 | 2018 | -12.0 [-24.6, 2.7] | -4.5 [-23.6, 19.5] |
| Inferential sensitivity | 2018 | -0.4 [-14.7, 16.1] | 4.8 [-16.2, 31.2] |
| Effective F below 10 | 2019 | -10.9 [-23.4, 3.7] | -3.5 [-22.9, 20.7] |
| Inferential sensitivity | 2019 | 0.9 [-13.3, 17.3] | 5.9 [-15.4, 32.5] |

Nieuwenhuis uses 2010 and 2012; Lal uses 2023 and 2025; Lazic uses 2016 and 2018 for the common before/after-warning contrast, with its main 2019 follow-up shown separately. The two IV definitions are alternatives from one audit, not independent studies. The I4R component summarizes only three selected matched disclosures.

Neither three-audit definition establishes a common citation penalty. The intervals are conditional on these audits and assume independent component errors; they omit audit-selection and generalization uncertainty. Citation databases, document types, publicity clocks and error definitions remain different. An imprecise synthesis is not evidence that publicity had no effect.

No known Lazic DOI overlaps the existing original/control DOI inventory; one included Lazic paper has no DOI. See the [component ledger](../../data/meta/lazic_components.csv), [identity ledger](../../data/meta/lazic_component_identities.csv), and [cohort results](../lazic/results.md). Run `make synthesis` to reproduce.

See [methods and sample definitions](design.md) and [current status](../../data/meta/status.json). The [two-audit comparisons](two-audit.md) retain additional IV definitions and neuroscience source/cohort sensitivities; the [I4R extension without Lazic](secondary.md) is also available. These are alternative summaries of overlapping evidence, not additional independent studies.

## Replacing the neuroscience citation source

The following comparisons replace the historical neuroscience counts with OpenAlex on the same papers and years. Each still contains three audits; different databases do not create independent studies. The main synthesis retains the historical source. These are source sensitivities, not estimates of database bias relative to a known truth.

| IV definition | Lazic follow-up | OpenAlex types | Three audits, % [95% interval] |
| --- | ---: | --- | ---: |
| Effective F below 10 | 2018 | Articles/reviews | -12.4 [-24.7, 1.8] |
| Effective F below 10 | 2018 | Broader types | -12.0 [-24.3, 2.3] |
| Inferential sensitivity | 2018 | Articles/reviews | -0.9 [-14.7, 15.2] |
| Inferential sensitivity | 2018 | Broader types | -0.5 [-14.4, 15.7] |
| Effective F below 10 | 2019 | Articles/reviews | -11.3 [-23.4, 2.8] |
| Effective F below 10 | 2019 | Broader types | -10.9 [-23.1, 3.3] |
| Inferential sensitivity | 2019 | Articles/reviews | 0.4 [-13.3, 16.3] |
| Inferential sensitivity | 2019 | Broader types | 0.8 [-12.9, 16.8] |

See the [paired citation-source comparison](../nieuwenhuis/README.md), [source-specific model estimates](../../data/nieuwenhuis/source_models.csv), and [synthesis data](../../data/meta/openalex_synthesis.csv).
