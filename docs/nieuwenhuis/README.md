# Nieuwenhuis citation-source comparison

This comparison holds the original papers and years fixed while replacing the historical Web of Science exports with OpenAlex records. It measures source discrepancies; neither database is assumed to be ground truth.

The roster retains 157 classified papers; 157 identities are resolved. Complete paired histories currently cover 10 of the 153 historical analysis papers (10 flagged, 0 comparison).

A full-cohort database comparison is still pending.

## Same-paper annual counts

Web of Science retains the historical counting rules. OpenAlex's primary count includes articles and reviews; its broader count also includes preprints, book chapters and proceedings articles. The historical exports lack the document-type detail needed to make these restrictions identical.

| Year | Group | Source | Papers | Mean citations | Median citations |
| --- | --- | --- | ---: | ---: | ---: |
| 2009 | Flagged | Web of Science | 10 | 1.1 | 0.0 |
| 2009 | Flagged | OpenAlex, articles/reviews | 10 | 1.9 | 0.0 |
| 2009 | Flagged | OpenAlex, broader types | 10 | 1.9 | 0.0 |
| 2010 | Flagged | Web of Science | 10 | 8.1 | 1.5 |
| 2010 | Flagged | OpenAlex, articles/reviews | 10 | 10.2 | 2.0 |
| 2010 | Flagged | OpenAlex, broader types | 10 | 10.6 | 2.5 |
| 2011 | Flagged | Web of Science | 10 | 17.9 | 8.5 |
| 2011 | Flagged | OpenAlex, articles/reviews | 10 | 20.0 | 10.0 |
| 2011 | Flagged | OpenAlex, broader types | 10 | 21.9 | 10.0 |
| 2012 | Flagged | Web of Science | 10 | 19.2 | 9.5 |
| 2012 | Flagged | OpenAlex, articles/reviews | 10 | 20.0 | 11.5 |
| 2012 | Flagged | OpenAlex, broader types | 10 | 21.6 | 11.5 |
| 2013 | Flagged | Web of Science | 10 | 23.9 | 14.0 |
| 2013 | Flagged | OpenAlex, articles/reviews | 10 | 25.3 | 14.5 |
| 2013 | Flagged | OpenAlex, broader types | 10 | 27.9 | 14.5 |
| 2014 | Flagged | Web of Science | 10 | 22.7 | 11.5 |
| 2014 | Flagged | OpenAlex, articles/reviews | 10 | 23.1 | 11.0 |
| 2014 | Flagged | OpenAlex, broader types | 10 | 26.8 | 14.0 |
| 2015 | Flagged | Web of Science | 10 | 23.4 | 12.0 |
| 2015 | Flagged | OpenAlex, articles/reviews | 10 | 24.4 | 12.5 |
| 2015 | Flagged | OpenAlex, broader types | 10 | 27.9 | 14.0 |

The table includes only papers with complete histories in both sources. Missing histories are not zero. These are descriptive counts for the available paired sample, not an estimate of publicity's effect.

## Citation links and publication years

Among DOI-bearing relationships dated 2009–2015 in at least one source, 1,128 occur in both, 10 occur only in the historical frame, and 294 occur only in OpenAlex. Of the shared relationships, 219 have different publication years. This link diagnostic includes all retrieved OpenAlex types and preserves links dated before the target paper; those records can be excluded from annual counts without being called missing links.

The DOI crosswalk retains both years and the OpenAlex document type. Non-DOI records remain in citation counts but cannot enter this exact-DOI crosswalk. A link absent from one frame can reflect a metadata typo, index coverage, publication/version dating or a reference error; absence alone does not establish which.

## Reproduce and resume

```sh
make nieuwenhuis
make nieuwenhuis-test
make nieuwenhuis-fetch
```

The first two commands run offline from frozen public inputs. The fetch target resumes publisher identity checks and incoming OpenAlex citations, retaining completed pilot histories and respecting the shared rate-limit checkpoint. Set OPENALEX_API_KEY in the environment for authenticated requests. No key is stored in the data.

See [design](design.md), [construction and dictionary](data.md), [status JSON](../../data/nieuwenhuis/status.json), and [paired records](../../data/nieuwenhuis/paired_panel.csv).
