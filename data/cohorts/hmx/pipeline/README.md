# Citations around publication of the interaction-model audit

Papers flagged for severe extrapolation had a **-16.9% relative change in
mean citations** (95% interval [-43.4, 22.0]%) around the audit's
December 2018 journal publication. The contrast is sensitive to one highly cited
comparison paper. Omitting each paper in turn produces estimates from
-23.5% to 1.6%; the positive endpoint omits Huddy, Mason and Aarøe
(2015). This audit does not show a clear publication-related break in citation growth.

## What changed

| Severe extrapolation | Papers | Mean, 2017 | Mean, 2019 | Median, 2017 | Median, 2019 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Flagged | 14 | 10.2 | 11.9 | 8.5 | 10.0 |
| Not flagged | 8 | 10.4 | 14.5 | 5.5 | 3.0 |

Mean citations increased in both groups, with a larger increase among comparison
papers. The difference between the two changes is -2.5 citations per paper
per year (Welch 95% interval [-10.6, 5.6]). Median levels
move in the opposite direction to that relative mean comparison. These are changes
in group medians; they are not medians of individual changes.

The proportional estimate is the flagged-group post/pre citation ratio divided by
the comparison-group ratio, minus one, expressed as a percentage. It is not an
annualized growth rate. Article and year fixed-effects Poisson estimation agrees
with the ratio calculated directly from group means. The primary interval uses
article-clustered covariance and a t critical value with the number of contributing
articles minus one degrees of freedom. A paired article bootstrap within groups
(9,999 draws) gives [-38.2, 41.9]%. Both methods leave substantial
uncertainty about the relative change.

## Sample and publicity

The source is [Hainmueller, Mummolo and Xu's interaction-model audit](https://doi.org/10.1017/pan.2018.46).
The public source inventory preserves all 46 assessed interactions in 22 original
papers. Table A1's severe-extrapolation labels classify 14 papers as flagged and
eight as comparison papers. A paper is flagged if any assessed interaction is
flagged. Six comparison papers have another adverse diagnostic, so they are not
cleared of all concerns. A diagnostic concern does not establish that an original
paper's substantive conclusion is false.

The event is the online journal publication on December 18, 2018. The replication
archive was public in July 2018; an SSRN draft was posted in February 2016. Its
earliest roster and labels have not been verified. The comparison therefore
concerns additional publication-era publicity. It cannot identify first disclosure.
A causal reading requires comparable untreated citation trajectories. The earlier
trend estimate below does not establish that publication caused a break.

Citation histories are complete for all 22 originals. Counts use distinct OpenAlex
citing articles and reviews. Williams (2011) has zero such citations in both selected
years and contributes to descriptions but not the Poisson coefficient. The main
model therefore has 14 flagged and seven comparison papers. Longer follow-up and
all-document-type outcomes have different zero-history exclusions.

## Specifications

| Comparison | Flagged / comparison contributing to PPML | Change (%) [95% interval] |
| --- | ---: | ---: |
| Primary: 2017 versus 2019 | 14 / 7 | -16.9 [-43.4, 22.0] |
| Exclude paper already in IV audit | 13 / 7 | -17.3 [-43.9, 22.0] |
| Follow-up averaged over 2019–2021 | 14 / 8 | -30.4 [-60.4, 22.4] |
| All citing document types | 14 / 8 | -42.3 [-68.5, 5.7] |
| Earlier trend: 2015 versus 2017 | 14 / 8 | -13.9 [-62.7, 99.0] |
| Linearity diagnostic | 9 / 10 | -24.5 [-46.6, 6.8] |
| Low/high nonrejection diagnostic | 15 / 5 | -30.3 [-50.1, -2.5] |
| Journal/year effects on supported journals | 11 / 7 | -7.9 [-51.2, 73.9] |
| Exclude Malesky's previously criticized paper | 13 / 7 | -15.2 [-42.5, 25.1] |

Alternative diagnostics replace the severe-extrapolation definition; they are not
additional independent studies. Nonrejection of equal low/high effects is not itself
proof of an error. Journal/year adjustment excludes International Organization,
which has three flagged papers and no comparison papers. The remaining 19-paper
sample contains one all-zero history. The longer follow-up includes the authors'
December 2019 appendix update and its response to methodological criticism.

For meta-analysis, Vernby (2013) is excluded because it already contributes to the
IV audit. This leaves 21 original papers, of which 20 contribute to the Poisson
coefficient: -17.3% [-43.9, 22.0]%. The full standalone
analysis retains Vernby. The sample and diagnostic rules were fixed before citation acquisition.

## Reproduction and sources

Run `make hmx` from the repository root to reproduce estimates and this report from
public frozen data. `make hmx-fetch` retrieves sources and citation links; `make
hmx-verify` checks the complete acquisition receipt chain, including the local raw
cache. The [numbered scripts](../../../../scripts/hmx/README.md) describe each stage.
The [design](design.md) was committed before citation acquisition. The
[reference crosswalk](reference_crosswalk.csv), [publisher metadata](original_metadata.json),
[paper assessments](paper_assessments.csv), [timing](timing.json),
[overlap](overlap.csv), [coverage](citation_coverage.csv), and [receipts](receipts/)
preserve the decisions and their sources. All analyses are retrospective.
