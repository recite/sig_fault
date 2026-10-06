# Secondary synthesis including the matched I4R cases

Mean citations rose 58.0% in the affected I4R group and 29.1% in its matched controls. The affected group's post/pre citation ratio was 22.3% higher than the controls' (exploratory interval [-63.0, 304.9]%).

This ratio of group means gives more influence to highly cited papers. A different summary, the equal-case average log ratio, corresponds to 3.9%.

In the preceding year, the affected group's post/pre ratio was already 25.5% higher than controls'. Omitting the inventor-clusters disclosure changes the post-disclosure contrast to -25.6%. These checks prevent interpreting the positive contrast as an increase caused by publicity.

Neither summary makes the selected disclosures representative of the I4R collection.

| Neuroscience sample | IV diagnostic | Neuroscience (%) | IV (%) | I4R (%) | Combined (%) | Exploratory 95% interval |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Historical cohort | Effective F below 10 | -14.1 | -14.5 | 22.3 | -3.5 | [-28.8, 30.7] |
| Historical cohort | Inferential sensitivity | -14.1 | 23.9 | 22.3 | 9.2 | [-19.4, 47.9] |
| Historical cohort | Either diagnostic | -14.1 | 11.8 | 22.3 | 5.5 | [-22.3, 43.2] |
| Historical cohort | AR-only sensitivity | -14.1 | -44.0 | 22.3 | -16.2 | [-37.9, 13.1] |
| 2009 publication cohort | Effective F below 10 | -8.5 | -14.5 | 22.3 | -1.4 | [-27.5, 34.0] |
| 2009 publication cohort | Inferential sensitivity | -8.5 | 23.9 | 22.3 | 11.5 | [-18.0, 51.7] |
| 2009 publication cohort | Either diagnostic | -8.5 | 11.8 | 22.3 | 7.8 | [-20.9, 46.9] |
| 2009 publication cohort | AR-only sensitivity | -8.5 | -44.0 | 22.3 | -14.4 | [-36.5, 15.5] |

Each component receives one third of the log-scale weight. I4R combines several
individual disclosures, so this is an equal-component summary, not three independent audits.
The source and document-type differences remain: historical Web of Science,
OpenAlex articles/reviews for the IV audit, and OpenAlex all-type totals for I4R.
The absence of shared original/control DOIs prevents direct double counting but does not
establish independence: citing papers and calendar-year shocks can overlap.
The intervals assume zero cross-component covariance and omit generalization uncertainty.
These are descriptive sensitivity estimates, not a common causal effect of publicity.

See [the retrospective amendment](design.md#retrospective-three-component-sensitivity),
[I4R case contrasts](../../data/i4r/aggregate/proportional_cases.csv),
[pre-period and leave-one-out checks](../../data/i4r/aggregate/proportional_sensitivity.csv),
[component identities](../../data/meta/component_identities.csv), and
[status](../../data/meta/three_component_status.json).
Run `make synthesis` to rebuild.
