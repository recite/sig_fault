# Methodological Criticism and Continued Citation

Ken Cor and Gaurav Sood

[Read the paper](ms/main.pdf) · [Analysis results](tabs/results.json) · [Data and measurement](docs/data.md)

Finding an error can improve later research only if researchers learn about it and reconsider their use of the affected work. We study what happens to citations after methodological audits identify problems in published research. The question is whether publicizing those problems changes subsequent citation, and whether citing papers acknowledge the concerns.

## What we learn

**Flagged neuroscience papers continued to attract citations, including the typical paper. Comparing papers published in the same journal and year suggests somewhat slower proportional growth after the critique.** OpenAlex histories through 2025 show flagged papers' median annual citations rising from 6.5 in 2010 to 14–19 during 2012–2015 and standing at 7 in 2025. A separate sample of citing passages recorded no acknowledgment of concerns in **94 of 95 valid completed ratings**.

The neuroscience design compares flagged and unflagged papers within **the same journal and publication year**, with article fixed effects and a separate annual citation path for each journal/year group. All 153 originals have comparison support. The estimate is **-8.5%** (95% interval [-24.7, 11.2]%) in historical Web of Science counts and **-7.3%** [-22.6, 10.9]% using OpenAlex for the same papers and years. The design accounts for stable article differences and different citation paths across journals and publication cohorts. Its causal interpretation requires comparable absent-critique growth within those groups.

Continued citation and a penalty can coexist: a criticized paper may receive many citations while receiving fewer than it otherwise would have. Citations also need not endorse the disputed inference; a later paper may use an unaffected result, a method, or background information. The context sample measures recorded acknowledgment after the neuroscience critique, not authors' awareness or the change in acknowledgment from before publication.

## Data and research design

The paper examines four audits with recoverable original papers, methodological assessments, and publicity dates:

| Audit | Assessment and comparison | Years used in synthesis |
| --- | --- | --- |
| [Neuroscience](docs/data.md) | Invalid comparisons of significant and nonsignificant effects; 76 flagged and 77 comparison papers | 2010 and 2012, around the 2011 critique |
| [Animal experiments](docs/lazic/README.md) | Pseudoreplication; 90 flagged and 45 comparison papers after excluding unclear assessments and an earlier-warning paper | 2016 and 2018, around the 2017 public release |
| [Instrumental variables](docs/lal/README.md) | Weak-instrument screening or sensitivity of inference in 67 assessed political-science papers | 2023 and 2025, around formal publication in 2024 |
| [Interaction models](data/cohorts/hmx/pipeline/README.md) | Severe extrapolation; 14 flagged and 8 comparison papers | 2017 and 2019, around online publication in 2018 |

The assessments range from identifiable errors in reasoning to diagnostic concerns about an estimate. A flagged diagnostic need not establish that a substantive conclusion is false. An unflagged paper may have other problems. Failed-replication citation research is a separate project and is excluded from this paper and its four-audit synthesis.

We count distinct citing documents per original paper and year. Zero counts require a completed citation history; missing histories remain missing. Poisson models with article and calendar-year fixed effects compare proportional citation changes, with uncertainty clustered by article. The synthesis combines one log relative-growth estimate per audit using inverse estimated sampling variances. Papers with no citations in either selected year remain in descriptive summaries but do not identify the Poisson coefficient. The interaction component excludes an original already included in the instrumental-variable audit.

[Figure 1](figs/citation_paths_openalex.pdf) shows OpenAlex means and medians through 2025 for the same 153 neuroscience papers. The [historical Web of Science figure](figs/citation_paths.pdf) appears in the manuscript appendix as a citation-source robustness check over 2009–2015. The [journal/year analysis](data/nieuwenhuis/design/README.md) estimates relative citation changes over 2010 versus 2012–2015 and adds [standardized mean and median trajectories](figs/journal_cohort_paths.pdf), using the same journal/publication-year composition for both groups. It also reports a restriction to 2009 originals, whose baseline covers a full year after publication, additive citation changes, and both citation sources. The remaining audits and the pooled summary retain their original specifications.

The [balance and weighting checks](data/nieuwenhuis/design/diagnostics.md) compare the original study characteristics and pre-critique citations. Journal/year standardization leaves a human-study imbalance. Comparing studies of the same species and within/between-subject design retains 49 flagged and 46 comparison papers; the historical-data proportional estimate is -7.2%. A same-sample comparison separates the additional adjustment from sample selection. The repository also reports an additive estimate giving every flagged paper equal weight: 0.6 citations per year [-3.8, 5.0]. Fixed-effects, equal-article and Poisson information weights are documented separately.

The causal interpretation requires comparable proportional citation paths without the publicity episode. The audits were not randomized, and earlier growth sometimes differs. The instrumental-variable and interaction critiques circulated before formal publication, so their comparisons concern additional publicity. The neuroscience regression follow-up covers 2012–2015, and the animal-study follow-up also examines 2019 and later years. Those comparisons are reported alongside the adjacent-year synthesis.

The [manuscript appendix](ms/main.pdf) reports journal and publication-cohort adjustments, alternative diagnostics, earlier trends, longer windows, whole-paper bootstraps and influential-paper checks. All analyses are retrospective. In the interaction audit, omitting one highly cited comparison paper changes the proportional estimate from -16.9% to 1.6%; medians and means also move differently. Pooling does not remove that sensitivity or establish the counterfactual.

A [synthetic difference-in-differences comparison for the pseudoreplication audit](data/lazic/sdid/README.md) estimates **-0.89 citations per paper per year** (95% interval [-2.01, 0.22]), close to ordinary DiD's -0.78 on the same papers and years. Flagged papers received 2.89 citations annually, compared with 3.79 predicted by the adjusted synthetic trajectory. The comparison uses older papers with three complete pre-disclosure years. Donor weights remain broadly spread, but synthetic weighting does not improve prediction of the held-out pre-disclosure year. Whole-article bootstrap draws refit both paper and time weights; all weights, sample decisions, draws and source receipts are saved. This additive check is not another independent study in the synthesis.

## Comparative estimates and their uncertainty

Across four methodological audits and 367 contributing papers, inverse-variance weighting gives a relative citation-growth contrast of **-12.9%** (95% interval [-24.3, 0.2]%). The alternative instrumental-variable diagnostic gives -4.5% [-17.0, 9.9]%. These are summaries of the selected comparisons; interpreting them as effects of publicity requires the counterfactual assumptions above.

The total paper count conceals small groups and uneven information. Citation changes vary substantially across articles, and a few papers account for much of the estimated variance in some audits. Each component uses just one baseline year and one follow-up year. The [precision decomposition](docs/meta/precision.md) reconstructs the standard errors directly from citation counts and shows each audit's group sizes, weight, and concentration of variance. The pooled interval uses a normal critical value, without an added random-effects variance. It describes uncertainty under the model and comparison assumptions; it does not account for bias from different underlying trends or earlier disclosure.

## Citation-source validation

[Reconstructing the neuroscience histories with OpenAlex](docs/nieuwenhuis/README.md) also reproduces the original article-and-year comparison on the same papers and years: -11.5% using historical Web of Science exports and -10.9% using OpenAlex articles and reviews. The paired source-induced change in the estimated growth ratio is 0.8% (95% interval [-8.9, 12.4]%). This is a measurement comparison; neither database is assumed to contain a complete census of citations.

[Link and date diagnostics](docs/nieuwenhuis/diagnostics.md) distinguish coverage from dating differences. A [third-source link check](docs/nieuwenhuis/validation.md) and [full-cohort OpenCitations comparison](docs/nieuwenhuis/opencitations.md) provide further checks. Agreement in aggregate estimates does not establish that every recorded citation is correct.

## Reproduce

Install R 4.6.0, Python 3.11 or newer, GNU Make, and a TeX distribution providing XeLaTeX and `latexmk`. From the repository root:

```sh
make restore
python3 -m pip install -r requirements-i4r.txt
make check
```

`make restore` installs the packages pinned in `renv.lock`. `make check` reads the archived inputs, regenerates results, figures, tables, this README, and the PDF, and runs linting and tests. After dependency installation, reproducing the estimates requires no network access. Acquisition scripts are separate from analysis and preserve source URLs, retrieval dates, hashes and stage receipts where available.

For individual steps, use `make analysis`, `make figures`, `make tables`, `make manuscript`, `make nieuwenhuis`, `make journal-cohort`, `make lazic-sdid`, `make synthesis`, `make lint`, or `make test`. Edit README prose in `docs/README.in.md`; numerical values are inserted from generated results. Edit the paper in `ms/main.tex`. Follow the [number-formatting conventions](docs/number-formatting.md) when adding prose, tables, or figures.

## Source inventories and additional cases

The [study inventory](data/cohorts/README.md) and [larger FORRT/statcheck inventories](docs/inventories.md) preserve additional sources. A collected inventory is not an estimated citation effect. [Expansion status](docs/meta/expansion-status.md) distinguishes completed comparisons from work still requiring verified identities, assessments, dates or citation histories.

The Institute for Replication extension has **3 selected matched cases** and remains outside the synthesis. Its [source registry](docs/i4r/README.md), [case comparisons](docs/i4r/aggregate-results.md), [synthetic-control checks](docs/i4r/synthetic-results.md), and [standalone proportional checks](docs/i4r/proportional.md) are retained. The [coverage report](docs/i4r/coverage.md) and [evidence catalog](docs/i4r/catalog.html) distinguish discovered reports from verified consequential errors and supported citation comparisons. This small pilot appears only in the manuscript appendix.

The [citation-context extension](docs/pilot/README.md) follows specific challenged findings into later research. It contains a reproducible article and citation sample, source checks, and independent-reader materials. Claim verification and citation coding remain in progress; it does not yet estimate continued reliance on those findings.

| Path | Contents |
| --- | --- |
| `data/01_nieuwenhuis/` | Original citation workbooks and supplied classifications |
| `data/02_are_nw_citations_approving/` | Original citation-context coding |
| `data/cohorts/` | Study-specific source inventories, assessments and acquisition records |
| `data/meta/` | Synthesis components, estimates and verification records |
| `R/` | Import, validation, construction and estimation functions |
| `scripts/` | Acquisition, analysis and exhibit generation |
| `tabs/` | Generated estimates, tables and manuscript macros |
| `figs/` | Generated publication figures |
| `ms/` | LaTeX source, bibliography and compiled paper |
| `tests/` | Data integrity, pipeline and statistical checks |

[Measurement details](docs/data.md) explain coverage, duplicate records, questionable links, coding, and uncertainty. [The analysis guide](docs/analysis.md) maps research claims to computations and checks. Original source files remain intact; redistribution of the supplied neuroscience classification was authorized by its provider.

Please use [CITATION.cff](CITATION.cff) to cite this paper. The source neuroscience critique is Nieuwenhuis, Forstmann, and Wagenmakers (2011), [“Erroneous analyses of interactions in neuroscience: a problem of significance”](https://doi.org/10.1038/nn.2886).
