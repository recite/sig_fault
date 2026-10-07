# Significant Error: Citations After Statistical Criticism and Replication

Ken Cor and Gaurav Sood

[Read the paper](ms/main.pdf) · [Analysis results](tabs/results.json) · [Data and measurement](docs/data.md)

## What we learn

**Adverse assessments are followed by modestly slower relative citation growth, while affected papers remain widely cited.** Across three methodological audits and a psychology replication project, the precision-weighted estimate is **-14.2%** (95% interval [-22.6, -4.8]%). Substituting the alternative instrumental-variable diagnostic gives -9.8% [-18.6, 0.0]%. This summarizes the included studies; it is not an average effect across all scientific errors. The [four-study synthesis](docs/meta/assessments.md) shows the component weights, narrower three-audit result, and timing, citation-source and random-effects checks.

The new [psychology replication analysis](data/cohorts/rpp/pipeline/README.md) covers **98 original papers**: 59 with unsuccessful and 39 with successful replication judgments. Following the project's 2015 announcement, the unsuccessful group had a **15.9% smaller post/pre citation ratio** (95% interval [-27.1, -3.4]%), standardizing journal composition. Their mean annual citations changed from 9.8 to 9.2; the successful group's changed from 9.3 to 9.7. An unsuccessful replication is not classified as a statistical error. This comparison includes both possible penalties for unsuccessful replications and benefits from successful ones.

The neuroscience evidence also shows why continued citation and a citation penalty can coexist. Flagged papers' median annual citations rose from 5 in 2010 to 13–17 during 2012–2015, even though their proportional growth lagged behind comparison papers. In a separate citation-context sample, **94 of 95 valid completed ratings recorded no acknowledgment of concerns**. These codes concern citations to the neuroscience papers, not the other cohorts.

The 2011 critique explained the mistake of treating a significant result and a nonsignificant result as evidence that two effects differ. Its authors supplied the paper-level classifications. Researchers could recognize the mistake in an original paper after reading the critique. [Replacing the original citation exports with OpenAlex](docs/nieuwenhuis/README.md) produces a similar growth estimate on the same papers: -11.5% using Web of Science and -10.9% using OpenAlex. This checks source sensitivity; neither database is assumed to be a complete citation census.

## What has been collected and analyzed

The four-study synthesis uses 445 contributing original papers in its main specification. The [animal-study audit](docs/lazic/README.md) preserves all 200 source assessments, including unclear cases excluded from its contrast. The [study inventory](data/cohorts/README.md) and [larger FORRT/statcheck inventories](docs/inventories.md) preserve additional sources; collecting an inventory does not mean its citation effect has been estimated. [Expansion status](docs/meta/expansion-status.md) distinguishes completed analyses from remaining identity, timing and citation work.

The I4R extension has only **3 selected matched cases** and remains outside the meta-analysis. Its [case comparisons](docs/i4r/aggregate-results.md) and [synthetic-control checks](docs/i4r/synthetic-results.md) remain available.

## Research design

- **Neuroscience papers and timing:** 76 flagged and 77 comparison papers, with 2010 as the baseline and 2012–2015 as the post period. The critique appeared in August 2011; that transition year is excluded from the main model. Citation-free years within covered histories remain zero.
- **Comparison:** proportional citation changes, estimated by Poisson pseudo-maximum likelihood with article and calendar-year fixed effects and article-clustered uncertainty. The percentage compares the groups’ post/pre citation ratios, not the number of additional citations gained.
- **Citation context:** the historical post-publicity sample contains 95 valid completed ratings, 3 false links, 1 unavailable article, and 1 uncoded record. It measures recorded qualifications after publicity, not their change from before publicity or the authors’ awareness.
- **Interpretation:** a causal reading requires comparable citation trajectories without the critique. Different earlier growth, unobserved awareness, and citations to unaffected findings limit that interpretation.

The appendix reports journal-by-year and publication-cohort-by-year effects, absolute-change models, later windows, restricted samples, data-inclusion checks, and whole-paper bootstrap uncertainty. All analyses are retrospective. The manuscript reports citation levels alongside relative-growth comparisons and preserves the difference between statistical errors, adverse diagnostics and unsuccessful replications.

## Reproduce

Install R 4.6.0, Python 3.11 or newer, GNU Make, and a TeX distribution providing XeLaTeX and `latexmk`. From the repository root:

```sh
make restore
python3 -m pip install -r requirements-i4r.txt
make check
```

`make restore` installs the packages pinned in `renv.lock`. `make check` reads the original local data, regenerates results, figures, tables, this README, and the PDF, and runs linting and tests. After dependency installation, the analysis requires no network access. No Docker is needed.

For individual steps, use `make analysis`, `make figures`, `make tables`, `make manuscript`, `make nieuwenhuis`, `make synthesis`, `make lint`, or `make test`. Edit the README’s prose in `docs/README.in.md`; numerical values come from the analysis. Edit the paper in `ms/main.tex`.

## Files

The [I4R extension](docs/i4r/README.md) builds a sourced registry of significant errors and their earliest public disclosures, followed by separate control matching and citation-effect analysis. It inventories both full discovered catalogs, keeps unresolved assessments visible, and reports a separately matched [secondary analysis of annual citation totals](docs/i4r/aggregate-results.md). The primary analysis of deduplicated article/review links remains pending. See the [coverage report](docs/i4r/coverage.md) and [evidence catalog](docs/i4r/catalog.html).

The [extension pilot](docs/pilot/README.md) follows specific challenged findings into later research. It contains a reproducible article and citation sample, source checks, and independent-reader materials. Claim verification and citation coding are still in progress; it does not yet provide estimates of continued reliance.

The [Lal et al. extension](docs/lal/README.md) follows all 67 political-science papers examined in an audit of instrumental-variable methods. Papers flagged for statistical problems continued to receive citations after the audit appeared. The comparisons leave uncertain how much, if at all, the audit reduced citation growth: the main estimates are imprecise and change substantially when measured from an earlier year. The critique also circulated before its formal publication in 2024, so that publication does not mark researchers’ first opportunity to learn about the problems. The [multi-audit strategy](docs/multiple-audits.md) sets out how to extend these comparisons across critiques.

The [Nieuwenhuis source comparison](docs/nieuwenhuis/README.md) now compares all 153 historical analysis papers using the same years in Web of Science and OpenAlex. The main relative-growth estimate changes little: -10.9% with OpenAlex articles/reviews, compared with -11.5% in the historical exports. The paired source-induced change in the estimated growth ratio is 0.8% (95% interval [-8.9, 12.4]%). This measures how the estimate changes with the recorded citation source; it does not establish which database is correct. The [link and date diagnostics](docs/nieuwenhuis/diagnostics.md) distinguish coverage from dating differences. A [third-source link check](docs/nieuwenhuis/validation.md) and [full-cohort OpenCitations comparison](docs/nieuwenhuis/opencitations.md) supply additional measurement checks.

`make synthesis` rebuilds the complete three-audit synthesis, its components, and the manuscript tables. Alternative diagnostic definitions from the same audit are dependent comparisons. The [two-audit reference synthesis](docs/meta/two-audit.md) combines the Nieuwenhuis and Lal contrasts and shows how the result changes with the IV diagnostic. It summarizes these cases, with differences in timing, citation measurement, and error definitions still present; it is not a general causal effect of publicizing errors. The [three-audit synthesis](docs/meta/README.md) adds the animal-study audit. The [four-study synthesis](docs/meta/assessments.md) also includes the psychology replication contrast, with its own [estimand and status](data/meta/assessment_status.json).

The I4R [standalone proportional checks](docs/i4r/proportional.md) retain case-specific evidence without adding the small pilot to the meta-analysis.

| Path | Contents |
| --- | --- |
| `data/01_nieuwenhuis/` | Original citation workbooks and supplied classifications |
| `data/02_are_nw_citations_approving/` | Original citation-context coding |
| `R/` | Import, validation, construction, and estimation functions |
| `scripts/` | Analysis and exhibit generation |
| `data/derived/` | Rebuilt article-year panel, citation records, and diagnostics; ignored by Git |
| `tabs/` | Generated estimates, machine-readable results, tables, and manuscript macros |
| `figs/` | Generated publication figures |
| `ms/` | LaTeX source, bibliography, and compiled paper |
| `tests/testthat/` | Data integrity and statistical checks |

[Measurement details](docs/data.md) explain coverage, duplicate records, questionable links, coding, and uncertainty. [The analysis guide](docs/analysis.md) maps research claims to computations and checks. The original source files remain intact; redistribution of the supplied classification was authorized by its provider.

Please use [CITATION.cff](CITATION.cff) to cite the research note. The source critique is Nieuwenhuis, Forstmann, and Wagenmakers (2011), [“Erroneous analyses of interactions in neuroscience: a problem of significance”](https://doi.org/10.1038/nn.2886).
