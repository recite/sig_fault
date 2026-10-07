# Significant Error: Citations to Research With Publicized Statistical Errors

Ken Cor and Gaurav Sood

[Read the paper](ms/main.pdf) · [Analysis results](tabs/results.json) · [Data and measurement](docs/data.md)

## What we learn

**Papers containing a publicized statistical mistake continued to receive citations, and recorded qualifications were rare.** The pattern holds for the typical paper: flagged papers’ median annual citations rose from {{MedianFlaggedBefore}} in 2010 to {{MedianFlaggedMin}}–{{MedianFlaggedMax}} during 2012–2015. Comparison papers’ medians rose from {{MedianComparisonBefore}} to {{MedianComparisonMin}}–{{MedianComparisonMax}}. For {{IncreasedPercent}}% of flagged papers, average annual citations after publicity exceeded the baseline. In a separate sample of citations to flagged papers, {{Nonack}} of {{Rated}} valid completed ratings recorded no acknowledgment of concerns.

The 2011 *Nature Neuroscience* critique explained the mistake of treating a significant result and a nonsignificant result as evidence that two effects differ. Its authors supplied the paper-level classifications used here. Researchers could recognize the mistake in an original paper after reading the critique.

Continued use is clear; how much publicity changed citation growth is less certain. A Poisson model with article and year fixed effects estimates a {{ProportionalReduction}}% smaller post/pre citation ratio for flagged papers (95% interval [{{ProportionalLower}}, {{ProportionalUpper}}]%). Their absolute citation gain was slightly larger because they started from a higher level. The appendix reports alternative specifications and magnitude bounds. Neither continued citation nor an imprecise comparison establishes that publicity had no effect.

The I4R extension currently supports matched comparisons for only **{{IfrCases}} affected papers**. This is a pilot, too small and selected to support a general conclusion about the effect of publicizing errors. The [case comparisons](docs/i4r/aggregate-results.md) and [synthetic-control checks](docs/i4r/synthetic-results.md) remain available. Complete [FORRT and statcheck inventories](docs/inventories.md) now provide larger pools for expansion. The reproduction excerpts have been screened; [primary-report reviews](docs/inventory-primary-reviews.md) and a separate [dated-disclosure registry](docs/external-disclosures.md) now distinguish verified errors from cases ready for citation collection. The [external collection workflow](docs/external/README.md) applies the shared control matcher to these disclosures. Identified papers, verified errors and usable citation comparisons remain distinct counts.

The [animal-study audit](docs/lazic/results.md) adds complete citation histories for **200 papers**: 91 flagged for treating dependent observations as independent, 45 classified as correctly analyzed, and 64 unclear. After excluding one paper with an earlier warning, the comparison contains {{LazicFlagged}} flagged and {{LazicComparison}} comparison papers. From 2016 to 2019, mean annual citations changed from {{LazicFlaggedBefore}} to {{LazicFlaggedAfter}} in the flagged group and from {{LazicComparisonBefore}} to {{LazicComparisonAfter}} in the comparison group. The difference in changes is {{LazicAbsolute}} citations per paper (95% interval [{{LazicAbsoluteLower}}, {{LazicAbsoluteUpper}}]). **Citation levels changed little on average in both groups; this audit supplies no clear evidence of an additional decline among flagged papers.**

The [study-by-study inventory](data/cohorts/README.md) now preserves complete source cohorts for interaction and panel-method audits, mediation, psychology and cancer replication, and SCORE. Each study has its own roster, assessments, original-source provenance and next-step notes. These inventories expand the collection pipeline; they do not yet add citation-effect estimates.

The [expanded synthesis](docs/meta/README.md) weights the three audit estimates by inverse sampling variance. The small I4R pilot is excluded from pooling. Audit weights, leave-one-audit-out estimates, and equal-audit and random-effects sensitivities are reported. A causal interpretation requires comparable untreated citation trajectories within each audit.

## Research design

- **Papers and timing:** {{Flagged}} flagged and {{Comparison}} comparison papers, with 2010 as the baseline and 2012–2015 as the post period. The critique appeared in August 2011; that transition year is excluded from the main model. Citation-free years within covered histories remain zero.
- **Comparison:** proportional citation changes, estimated by Poisson pseudo-maximum likelihood with article and calendar-year fixed effects and article-clustered uncertainty. The percentage compares the groups’ post/pre citation ratios, not the number of additional citations gained.
- **Citation context:** the historical post-publicity sample contains {{Rated}} valid completed ratings, {{CodingFalse}} false links, {{Unavailable}} unavailable article, and {{Uncoded}} uncoded record. It measures recorded qualifications after publicity, not their change from before publicity or the authors’ awareness.
- **Interpretation:** a causal reading requires comparable citation trajectories without the critique. Different earlier growth, unobserved awareness, and citations to unaffected findings limit that interpretation.

The appendix reports journal-by-year and publication-cohort-by-year effects, absolute-change models, later windows, restricted samples, data-inclusion checks, and whole-paper bootstrap uncertainty. All analyses are retrospective. The main text leads with median and mean trajectories and the citation-context evidence.

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

The [Nieuwenhuis source comparison](docs/nieuwenhuis/README.md) now compares all 153 historical analysis papers using the same years in Web of Science and OpenAlex. The main relative-growth estimate changes little: {{NwOaPercent}}% with OpenAlex articles/reviews, compared with {{NwOaWosPercent}}% in the historical exports. The paired source-induced change in the estimated growth ratio is {{NwOaDifference}}% (95% interval [{{NwOaDifferenceLower}}, {{NwOaDifferenceUpper}}]%). This measures how the estimate changes with the recorded citation source; it does not establish which database is correct. The [link and date diagnostics](docs/nieuwenhuis/diagnostics.md) distinguish coverage from dating differences. A [third-source link check](docs/nieuwenhuis/validation.md) and [full-cohort OpenCitations comparison](docs/nieuwenhuis/opencitations.md) supply additional measurement checks.

`make synthesis` rebuilds the complete three-audit synthesis, its components, and the manuscript tables. Alternative diagnostic definitions from the same audit are dependent comparisons. The [two-audit reference synthesis](docs/meta/two-audit.md) combines the Nieuwenhuis and Lal contrasts and shows how the result changes with the IV diagnostic. It summarizes these cases, with differences in timing, citation measurement, and error definitions still present; it is not a general causal effect of publicizing errors. The [expanded synthesis](docs/meta/README.md) adds the complete animal-study audit; its [status](data/meta/status.json) records the estimand and limits.

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
