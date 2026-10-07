# Methodological Criticism and Continued Citation

Ken Cor and Gaurav Sood

[Read the paper](ms/main.pdf) · [Analysis results](tabs/results.json) · [Data and measurement](docs/data.md)

Finding an error can improve later research only if researchers learn about it and reconsider their use of the affected work. We study what happens to citations after methodological audits identify problems in published research. The question is whether publicizing those problems changes subsequent citation, and whether citing papers acknowledge the concerns.

## What we learn

**The affected papers remained widely cited. The comparative estimates allow a citation penalty, whose size depends on the diagnostic and comparison.** In the neuroscience audit, flagged papers' median annual citations rose from {{MedianFlaggedBefore}} in 2010 to {{MedianFlaggedMin}}–{{MedianFlaggedMax}} during 2012–2015. A separate sample of citing passages recorded no acknowledgment of concerns in **{{Nonack}} of {{Rated}} valid completed ratings**.

Across four methodological audits and **{{AuditPapers}} contributing papers**, the main precision-weighted contrast is **{{AuditWeakPercent}}%** (95% interval [{{AuditWeakLower}}, {{AuditWeakUpper}}]%). Substituting the alternative instrumental-variable diagnostic gives {{AuditSensitivePercent}}% [{{AuditSensitiveLower}}, {{AuditSensitiveUpper}}]%. These percentages compare flagged and comparison papers' post/pre citation ratios. They summarize this collection of audits, not an average effect across all scientific errors.

Continued citation and a penalty can coexist: a criticized paper may receive many citations while receiving fewer than it otherwise would have. Citations also need not endorse the disputed inference; a later paper may use an unaffected result, a method, or background information. The context sample measures recorded acknowledgment after the neuroscience critique, not authors' awareness or the change in acknowledgment from before publication.

## Data and research design

The paper examines four audits with recoverable original papers, methodological assessments, and publicity dates:

| Audit | Assessment and comparison | Years used in synthesis |
| --- | --- | --- |
| [Neuroscience](docs/data.md) | Invalid comparisons of significant and nonsignificant effects; {{Flagged}} flagged and {{Comparison}} comparison papers | 2010 and 2012, around the 2011 critique |
| [Animal experiments](docs/lazic/README.md) | Pseudoreplication; {{LazicFlagged}} flagged and {{LazicComparison}} comparison papers after excluding unclear assessments and an earlier-warning paper | 2016 and 2018, around the 2017 public release |
| [Instrumental variables](docs/lal/README.md) | Weak-instrument screening or sensitivity of inference in {{LalPapers}} assessed political-science papers | 2023 and 2025, around formal publication in 2024 |
| [Interaction models](data/cohorts/hmx/pipeline/README.md) | Severe extrapolation; {{HmxFlaggedPapers}} flagged and {{HmxComparisonPapers}} comparison papers | 2017 and 2019, around online publication in 2018 |

The assessments range from identifiable errors in reasoning to diagnostic concerns about an estimate. A flagged diagnostic need not establish that a substantive conclusion is false. An unflagged paper may have other problems. Failed-replication citation research is a separate project and is excluded from this paper and its four-audit synthesis.

We count distinct citing documents per original paper and year. Zero counts require a completed citation history; missing histories remain missing. Poisson models with article and calendar-year fixed effects compare proportional citation changes, with uncertainty clustered by article. The synthesis combines one log relative-growth estimate per audit using inverse estimated sampling variances. Papers with no citations in either selected year remain in descriptive summaries but do not identify the Poisson coefficient. The interaction component excludes an original already included in the instrumental-variable audit.

The causal interpretation requires comparable proportional citation paths without the publicity episode. The audits were not randomized, and earlier growth sometimes differs. The instrumental-variable and interaction critiques circulated before formal publication, so their comparisons concern additional publicity. The longer neuroscience follow-up covers 2012–2015, and the animal-study follow-up also examines 2019 and later years. Those comparisons are reported alongside the adjacent-year synthesis.

The [manuscript appendix](ms/main.pdf) reports journal and publication-cohort adjustments, alternative diagnostics, earlier trends, longer windows, whole-paper bootstraps and influential-paper checks. All analyses are retrospective. In the interaction audit, omitting one highly cited comparison paper changes the proportional estimate from {{HmxPercent}}% to {{HmxLooMax}}%; medians and means also move differently. Pooling does not remove that sensitivity or establish the counterfactual.

## Citation-source validation

[Reconstructing the neuroscience histories with OpenAlex](docs/nieuwenhuis/README.md) gives a similar estimate on the same original papers and years: {{NwOaWosPercent}}% using historical Web of Science exports and {{NwOaPercent}}% using OpenAlex articles and reviews. The paired source-induced change in the estimated growth ratio is {{NwOaDifference}}% (95% interval [{{NwOaDifferenceLower}}, {{NwOaDifferenceUpper}}]%). This is a measurement comparison; neither database is assumed to contain a complete census of citations.

[Link and date diagnostics](docs/nieuwenhuis/diagnostics.md) distinguish coverage from dating differences. A [third-source link check](docs/nieuwenhuis/validation.md) and [full-cohort OpenCitations comparison](docs/nieuwenhuis/opencitations.md) provide further checks. Agreement in aggregate estimates does not establish that every recorded citation is correct.

## Reproduce

Install R 4.6.0, Python 3.11 or newer, GNU Make, and a TeX distribution providing XeLaTeX and `latexmk`. From the repository root:

```sh
make restore
python3 -m pip install -r requirements-i4r.txt
make check
```

`make restore` installs the packages pinned in `renv.lock`. `make check` reads the archived inputs, regenerates results, figures, tables, this README, and the PDF, and runs linting and tests. After dependency installation, reproducing the estimates requires no network access. Acquisition scripts are separate from analysis and preserve source URLs, retrieval dates, hashes and stage receipts where available.

For individual steps, use `make analysis`, `make figures`, `make tables`, `make manuscript`, `make nieuwenhuis`, `make synthesis`, `make lint`, or `make test`. Edit README prose in `docs/README.in.md`; numerical values are inserted from generated results. Edit the paper in `ms/main.tex`.

## Source inventories and additional cases

The [study inventory](data/cohorts/README.md) and [larger FORRT/statcheck inventories](docs/inventories.md) preserve additional sources. A collected inventory is not an estimated citation effect. [Expansion status](docs/meta/expansion-status.md) distinguishes completed comparisons from work still requiring verified identities, assessments, dates or citation histories.

The Institute for Replication extension has **{{IfrCases}} selected matched cases** and remains outside the synthesis. Its [source registry](docs/i4r/README.md), [case comparisons](docs/i4r/aggregate-results.md), [synthetic-control checks](docs/i4r/synthetic-results.md), and [standalone proportional checks](docs/i4r/proportional.md) are retained. The [coverage report](docs/i4r/coverage.md) and [evidence catalog](docs/i4r/catalog.html) distinguish discovered reports from verified consequential errors and supported citation comparisons. This small pilot appears only in the manuscript appendix.

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
