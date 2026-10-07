# Nieuwenhuis citation-source comparison

This comparison holds the original papers and years fixed while replacing the historical Web of Science exports with OpenAlex records. It measures source discrepancies; neither database is assumed to be ground truth.

The roster retains 157 classified papers; 157 identities are resolved. Complete paired histories currently cover 153 of the 153 historical analysis papers (76 flagged, 77 comparison).

The historical cohort has complete paired histories.
These counts measure download progress, not OpenAlex's coverage of the literature. An uncollected history says nothing about how many citations the database contains for that paper.

[OpenAlex citation paths through 2025](long-citation-paths.md) extend Figure 1 using the same 153 papers and counting rules.

## Same-paper annual counts

Web of Science retains the historical counting rules. OpenAlex's primary count includes articles and reviews; its broader count also includes preprints, book chapters and proceedings articles. The historical exports lack the document-type detail needed to make these restrictions identical.

| Year | Group | Source | Papers | Mean citations | Median citations |
| --- | --- | --- | ---: | ---: | ---: |
| 2009 | Comparison | Web of Science | 77 | 1.1 | 0.0 |
| 2009 | Comparison | OpenAlex, articles/reviews | 77 | 2.2 | 0.0 |
| 2009 | Comparison | OpenAlex, broader types | 77 | 2.3 | 0.0 |
| 2009 | Flagged | Web of Science | 76 | 1.5 | 0.0 |
| 2009 | Flagged | OpenAlex, articles/reviews | 76 | 2.6 | 0.0 |
| 2009 | Flagged | OpenAlex, broader types | 76 | 2.6 | 0.0 |
| 2010 | Comparison | Web of Science | 77 | 6.5 | 4.0 |
| 2010 | Comparison | OpenAlex, articles/reviews | 77 | 9.1 | 7.0 |
| 2010 | Comparison | OpenAlex, broader types | 77 | 9.5 | 7.0 |
| 2010 | Flagged | Web of Science | 76 | 9.4 | 5.0 |
| 2010 | Flagged | OpenAlex, articles/reviews | 76 | 12.5 | 6.5 |
| 2010 | Flagged | OpenAlex, broader types | 76 | 13.2 | 7.5 |
| 2011 | Comparison | Web of Science | 77 | 14.3 | 11.0 |
| 2011 | Comparison | OpenAlex, articles/reviews | 77 | 16.6 | 12.0 |
| 2011 | Comparison | OpenAlex, broader types | 77 | 17.9 | 13.0 |
| 2011 | Flagged | Web of Science | 76 | 18.3 | 13.0 |
| 2011 | Flagged | OpenAlex, articles/reviews | 76 | 20.8 | 15.0 |
| 2011 | Flagged | OpenAlex, broader types | 76 | 22.6 | 15.5 |
| 2012 | Comparison | Web of Science | 77 | 16.2 | 11.0 |
| 2012 | Comparison | OpenAlex, articles/reviews | 77 | 17.7 | 12.0 |
| 2012 | Comparison | OpenAlex, broader types | 77 | 19.2 | 14.0 |
| 2012 | Flagged | Web of Science | 76 | 20.2 | 16.0 |
| 2012 | Flagged | OpenAlex, articles/reviews | 76 | 20.7 | 16.0 |
| 2012 | Flagged | OpenAlex, broader types | 76 | 22.8 | 18.0 |
| 2013 | Comparison | Web of Science | 77 | 17.1 | 10.0 |
| 2013 | Comparison | OpenAlex, articles/reviews | 77 | 18.7 | 13.0 |
| 2013 | Comparison | OpenAlex, broader types | 77 | 20.9 | 13.0 |
| 2013 | Flagged | Web of Science | 76 | 22.6 | 17.0 |
| 2013 | Flagged | OpenAlex, articles/reviews | 76 | 24.7 | 19.0 |
| 2013 | Flagged | OpenAlex, broader types | 76 | 26.9 | 20.5 |
| 2014 | Comparison | Web of Science | 77 | 16.8 | 11.0 |
| 2014 | Comparison | OpenAlex, articles/reviews | 77 | 18.4 | 13.0 |
| 2014 | Comparison | OpenAlex, broader types | 77 | 20.4 | 14.0 |
| 2014 | Flagged | Web of Science | 76 | 22.4 | 16.0 |
| 2014 | Flagged | OpenAlex, articles/reviews | 76 | 23.1 | 15.0 |
| 2014 | Flagged | OpenAlex, broader types | 76 | 26.3 | 18.0 |
| 2015 | Comparison | Web of Science | 77 | 16.5 | 11.0 |
| 2015 | Comparison | OpenAlex, articles/reviews | 77 | 18.3 | 13.0 |
| 2015 | Comparison | OpenAlex, broader types | 77 | 20.2 | 14.0 |
| 2015 | Flagged | Web of Science | 76 | 20.2 | 13.0 |
| 2015 | Flagged | OpenAlex, articles/reviews | 76 | 21.6 | 14.0 |
| 2015 | Flagged | OpenAlex, broader types | 76 | 24.0 | 15.0 |

The table includes only papers with complete histories in both sources. Missing histories are not zero. These are descriptive counts for the available paired sample, not an estimate of publicity's effect.

## Source-specific growth estimates

Each model uses article and year fixed effects, with article-clustered uncertainty. The table uses the historical cohort, a 2010 baseline and 2012–2015 post period. These intervals concern each source's growth contrast; the paired intervals below concern the change from switching sources.

| Source | Relative growth difference, % | 95% interval |
| --- | ---: | ---: |
| Web of Science | -11.5 | [-31.6, 14.4] |
| OpenAlex, articles/reviews | -10.9 | [-29.0, 11.9] |
| OpenAlex, broader types | -10.7 | [-28.9, 12.2] |

## Does the source change the growth comparison?

The paired estimator compares the flagged-minus-comparison change in each database, then subtracts the Web of Science contrast from the OpenAlex contrast. It uses the same papers, a 2010 baseline, and either 2012 or the annual average over 2012–2015. The 2009 publication cohort is also reported separately.

The absolute contrast uses citations per paper per year. The proportional contrast is the ratio of flagged post/pre growth to comparison post/pre growth. Its source discrepancy below is the percentage change in that ratio when switching to OpenAlex, not a percentage-point difference between effect estimates.

| Cohort | Post years | OpenAlex types | Contrast | Flagged / comparison | Source discrepancy [95% interval] | Status |
| --- | --- | --- | --- | ---: | ---: | --- |
| Historical cohort | 2012 | OpenAlex, articles/reviews | Absolute change | 76 / 77 | -1.49 [-3.12, 0.10] | complete |
| Historical cohort | 2012 | OpenAlex, articles/reviews | Growth ratio | 76 / 77 | -1.4% [-12.4%, 11.4%] | complete |
| Historical cohort | 2012 | OpenAlex, broader types | Absolute change | 76 / 77 | -1.08 [-2.70, 0.55] | complete |
| Historical cohort | 2012 | OpenAlex, broader types | Growth ratio | 76 / 77 | -0.1% [-11.0%, 12.9%] | complete |
| Historical cohort | 2012-2015 | OpenAlex, articles/reviews | Absolute change | 76 / 77 | -0.99 [-2.15, 0.09] | complete |
| Historical cohort | 2012-2015 | OpenAlex, articles/reviews | Growth ratio | 76 / 77 | 0.8% [-8.9%, 12.4%] | complete |
| Historical cohort | 2012-2015 | OpenAlex, broader types | Absolute change | 76 / 77 | -0.63 [-1.76, 0.52] | complete |
| Historical cohort | 2012-2015 | OpenAlex, broader types | Growth ratio | 76 / 77 | 1.0% [-8.8%, 12.7%] | complete |
| 2009 publication cohort | 2012 | OpenAlex, articles/reviews | Absolute change | 44 / 47 | -1.84 [-4.12, 0.41] | complete |
| 2009 publication cohort | 2012 | OpenAlex, articles/reviews | Growth ratio | 44 / 47 | -2.1% [-14.1%, 12.1%] | complete |
| 2009 publication cohort | 2012 | OpenAlex, broader types | Absolute change | 44 / 47 | -1.37 [-3.59, 0.84] | complete |
| 2009 publication cohort | 2012 | OpenAlex, broader types | Growth ratio | 44 / 47 | -1.3% [-13.6%, 12.7%] | complete |
| 2009 publication cohort | 2012-2015 | OpenAlex, articles/reviews | Absolute change | 44 / 47 | -1.64 [-3.33, -0.05] | complete |
| 2009 publication cohort | 2012-2015 | OpenAlex, articles/reviews | Growth ratio | 44 / 47 | -2.1% [-11.9%, 9.4%] | complete |
| 2009 publication cohort | 2012-2015 | OpenAlex, broader types | Absolute change | 44 / 47 | -1.06 [-2.52, 0.39] | complete |
| 2009 publication cohort | 2012-2015 | OpenAlex, broader types | Growth ratio | 44 / 47 | -1.6% [-11.7%, 10.2%] | complete |

Intervals use 9,999 paired paper resamples within flag groups. Each draw retains the same paper's counts in both databases. Missing groups produce no contrast; undefined proportional draws are counted and withhold that interval rather than being silently discarded. These intervals describe variation across observed papers, not uncertainty about missing citations or the causal effect of publicizing errors.

See [source contrasts](../../data/nieuwenhuis/source_contrasts.csv) and [period means and medians](../../data/nieuwenhuis/period_summary.csv).

## Citation links and publication years

Among DOI-bearing relationships dated 2009–2015 in at least one source, 14,742 occur in both, 355 occur only in the historical frame, and 4,721 occur only in OpenAlex. Of the shared relationships, 3,223 have different publication years. This link diagnostic includes all retrieved OpenAlex types and preserves links dated before the target paper; those records can be excluded from annual counts without being called missing links.

The DOI crosswalk retains both years and the OpenAlex document type. Non-DOI records remain in citation counts but cannot enter this exact-DOI crosswalk. A link absent from one frame can reflect a metadata typo, index coverage, publication/version dating or a reference error; absence alone does not establish which.

## Reproduce and resume

```sh
make nieuwenhuis
make nieuwenhuis-test
make nieuwenhuis-fetch
```

The first two commands run offline from frozen public inputs. The fetch target resumes publisher identity checks and incoming OpenAlex citations, retaining completed pilot histories and respecting the shared rate-limit checkpoint. Authenticated requests use OPENALEX_API_KEY, or the key in `$XDG_CONFIG_HOME/openalex/api_key` (default `~/.config/openalex/api_key`). The environment takes precedence. Credentials are sent in headers and are not stored in the data or manifests.

See [design](design.md), [construction and dictionary](data.md), [source-discrepancy diagnostics](diagnostics.md), [OpenCitations link check](validation.md), [full-cohort OpenCitations comparison](opencitations.md), [status JSON](../../data/nieuwenhuis/status.json), and [paired records](../../data/nieuwenhuis/paired_panel.csv).
