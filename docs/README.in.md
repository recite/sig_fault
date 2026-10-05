# Significant Error: Citations to Research With Publicized Statistical Errors

Ken Cor and Gaurav Sood

[Read the paper](ms/main.pdf) · [Analysis results](tabs/results.json) · [Data and measurement](docs/data.md)

## What we learn

Does drawing attention to a statistical mistake change how researchers use papers containing it? A 2011 *Nature Neuroscience* article explained the mistake of treating a statistically significant result and a nonsignificant result as evidence that the two effects differ. Using the authors’ paper-level classifications, we compare subsequent citations to papers that made this mistake with citations to papers that used the relevant test correctly.

**Flagged papers continued to attract citations, and recorded acknowledgment of concerns was rare.** Annual citations rose from {{FlaggedBefore}} in 2010 to {{FlaggedAfter}} on average during 2012–2015 for flagged papers, and from {{ComparisonBefore}} to {{ComparisonAfter}} for comparison papers. The difference in those increases was {{MainEstimate}} citations per paper per year (95% interval {{MainInterval}}). That estimate does not show the predicted relative decline, but its uncertainty and the groups’ different earlier trajectories prevent a confident claim that the critique had no effect.

In the separate citation-context sample, {{Nonack}} of {{Rated}} completed ratings of valid citation relationships recorded no acknowledgment of concerns. This describes what citing papers said; it does not establish whether their authors noticed the mistake or whether the finding they cited depended on it.

## Research design

- **Source papers:** the supplied classification covers {{Classified}} papers published in five neuroscience and general-science journals in 2009–2010. Citation exports cover {{Covered}}. The main analysis uses {{Flagged}} flagged and {{Comparison}} comparison papers after excluding two unreliable citation histories; the inclusive result is also reported.
- **Comparison:** each paper’s mean annual citations in 2012–2015 minus its citations in 2010, followed by flagged minus comparison. The critique appeared in August 2011, so 2011 is a transition year. All covered paper-years, including citation-free years, enter the calculation.
- **Interpretation:** a relative decline would be consistent with researchers changing their use of affected papers. A causal interpretation additionally requires comparable citation trajectories without the critique. Among the 2009 papers, flagged papers’ citations were already growing faster before it appeared. Neither error status nor awareness of the critique was randomized.
- **Citation context:** the archived sample contains {{CodingN}} citation relationships from 2012 through the partial 2016 export: {{Rated}} completed ratings of valid citation relationships, {{CodingFalse}} false links, {{Unavailable}} unavailable article, and {{Uncoded}} uncoded record. The historical sample and original ratings are preserved.

The main estimate uses a Welch interval over paper-level changes. The paper reports journal and publication-year adjustment, publication-cohort comparisons, later citation windows, potentially serious errors, data-cleaning sensitivities, and influence checks. These are retrospective analyses, not preregistered tests.

## Reproduce

Install R 4.6.0, GNU Make, and a TeX distribution providing XeLaTeX and `latexmk`. From the repository root:

```sh
make restore
make check
```

`make restore` installs the packages pinned in `renv.lock`. `make check` reads the original local data, regenerates results, figures, tables, this README, and the PDF, and runs linting and tests. After dependency installation, the analysis requires no network access. No Docker is needed.

For individual steps, use `make analysis`, `make figures`, `make tables`, `make manuscript`, `make lint`, or `make test`. Edit the README’s prose in `docs/README.in.md`; numerical values come from the analysis. Edit the paper in `ms/main.tex`.

## Files

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
