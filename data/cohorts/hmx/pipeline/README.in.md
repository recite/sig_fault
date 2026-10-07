# Citations around publication of the interaction-model audit

Papers flagged for severe extrapolation had a **${HmxPercent}% relative change in
mean citations** (95% interval [${HmxLower}, ${HmxUpper}]%) around the audit's
December 2018 journal publication. The contrast is sensitive to one highly cited
comparison paper. Omitting each paper in turn produces estimates from
${HmxLooMin}% to ${HmxLooMax}%; the positive endpoint omits Huddy, Mason and Aarøe
(2015). This audit does not show a clear publication-related break in citation growth.

## What changed

| Severe extrapolation | Papers | Mean, 2017 | Mean, 2019 | Median, 2017 | Median, 2019 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Flagged | $HmxFlaggedPapers | $HmxFlaggedMeanBefore | $HmxFlaggedMeanAfter | $HmxFlaggedMedianBefore | $HmxFlaggedMedianAfter |
| Not flagged | $HmxComparisonPapers | $HmxComparisonMeanBefore | $HmxComparisonMeanAfter | $HmxComparisonMedianBefore | $HmxComparisonMedianAfter |

Mean citations increased in both groups, with a larger increase among comparison
papers. The difference between the two changes is $HmxAbsolute citations per paper
per year (Welch 95% interval [$HmxAbsoluteLower, $HmxAbsoluteUpper]). Median levels
move in the opposite direction to that relative mean comparison. These are changes
in group medians; they are not medians of individual changes.

The proportional estimate is the flagged-group post/pre citation ratio divided by
the comparison-group ratio, minus one, expressed as a percentage. It is not an
annualized growth rate. Article and year fixed-effects Poisson estimation agrees
with the ratio calculated directly from group means. The primary interval uses
article-clustered covariance and a t critical value with the number of contributing
articles minus one degrees of freedom. A paired article bootstrap within groups
(9,999 draws) gives [$HmxBootLower, $HmxBootUpper]%. Both methods leave substantial
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
$specifications

Alternative diagnostics replace the severe-extrapolation definition; they are not
additional independent studies. Nonrejection of equal low/high effects is not itself
proof of an error. Journal/year adjustment excludes International Organization,
which has three flagged papers and no comparison papers. The remaining 19-paper
sample contains one all-zero history. The longer follow-up includes the authors'
December 2019 appendix update and its response to methodological criticism.

For meta-analysis, Vernby (2013) is excluded because it already contributes to the
IV audit. This leaves 21 original papers, of which 20 contribute to the Poisson
coefficient: $HmxMetaPercent% [$HmxMetaLower, $HmxMetaUpper]%. The full standalone
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
