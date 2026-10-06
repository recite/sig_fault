# Significant Error: Citations to Research With Publicized Statistical Errors

Ken Cor and Gaurav Sood

[Read the paper](ms/main.pdf) · [Analysis results](tabs/results.json) · [Data and measurement](docs/data.md)

## What we learn

**Papers containing a publicized statistical mistake continued to receive citations, and recorded qualifications were rare.** The pattern holds for the typical paper: flagged papers’ median annual citations rose from {{MedianFlaggedBefore}} in 2010 to {{MedianFlaggedMin}}–{{MedianFlaggedMax}} during 2012–2015. Comparison papers’ medians rose from {{MedianComparisonBefore}} to {{MedianComparisonMin}}–{{MedianComparisonMax}}. For {{IncreasedPercent}}% of flagged papers, average annual citations after publicity exceeded the baseline. In a separate sample of citations to flagged papers, {{Nonack}} of {{Rated}} valid completed ratings recorded no acknowledgment of concerns.

The 2011 *Nature Neuroscience* critique explained the mistake of treating a significant result and a nonsignificant result as evidence that two effects differ. Its authors supplied the paper-level classifications used here. Researchers could recognize the mistake in an original paper after reading the critique.

Continued use is clear; how much publicity changed citation growth is less certain. A Poisson model with article and year fixed effects estimates a {{ProportionalReduction}}% smaller post/pre citation ratio for flagged papers (95% interval [{{ProportionalLower}}, {{ProportionalUpper}}]%). Their absolute citation gain was slightly larger because they started from a higher level. The appendix reports alternative specifications and magnitude bounds. Neither continued citation nor an imprecise comparison establishes that publicity had no effect.

In a secondary analysis of individually publicized errors, citations increased for {{IfrIncreased}} of {{IfrCases}} affected papers. Their median annual citations rose from {{IfrMedianBefore}} to {{IfrMedianAfter}}; matched controls’ median rose from {{IfrControlMedianBefore}} to {{IfrControlMedianAfter}}. The average difference in changes is +{{IfrChange}} citations, but becomes {{IfrOmitInventors}} when the inventor-clusters paper is omitted. Earlier growth also differed. These cases do not establish a stable causal response to disclosure. See the [individual comparisons](docs/i4r/aggregate-results.md).

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

The [Lal et al. extension](docs/lal/README.md) applies the citation-trajectory analysis to all 67 papers in a political-science IV audit. It reports mean and median paths, article fixed-effects estimates, and sensitivity to diagnostic definitions, timing, and the unit counted as a citing publication. The manuscript now includes this extension: its conclusions depend on the diagnostic and baseline year, so it does not establish a consistent citation penalty. The [multi-audit strategy](docs/multiple-audits.md) sets out how to extend these comparisons across critiques.

The [Nieuwenhuis source comparison](docs/nieuwenhuis/README.md) links every original assessment to a verified article DOI and compares historical Web of Science counts with available OpenAlex histories for the same papers. The current paired sample contains only flagged papers; it can reveal source discrepancies but cannot yet compare the databases’ estimates of the publicity effect.

`make synthesis` generates [comparable one-year contrasts](data/meta/audit_contrasts.csv) for the completed cohorts and the manuscript’s IV-audit table. Alternative diagnostic definitions from the same audit are dependent comparisons. The [provisional equal-audit synthesis](docs/meta/README.md) combines one contrast from each completed audit and shows how the result changes with the IV diagnostic. It summarizes these cases, with differences in timing, citation measurement, and error definitions still present; it is not a general causal effect of publicizing errors. The [synthesis status](data/meta/status.json) records the remaining collection work.

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
