# Verification of the four-study synthesis

An independent reconstruction from the exported components reproduced all eight
inverse-variance estimates and normal intervals, including the neuroscience-source
and psychology-window substitutions. All 32 leave-one-study-out coefficients and
standard errors also matched. Independent REML optimization and modified
Knapp–Hartung calculations agreed at the displayed precision.

The main contributing-paper denominator is 153 neuroscience papers, 67 IV papers,
127 animal-study papers contributing to the selected Poisson fit, and 98 psychology
papers: 445 in total. Substituting the inferential-sensitivity IV definition uses
55 IV papers and hence 433 originals. Each synthesis contains one estimate per
study. The psychology input uses the standard deviation of its log-scale bootstrap
draws, not its level standard error or a reconstructed percentile-interval width.

No known DOI overlaps the original-paper cohorts. The animal-study paper without
a DOI was published in 2012 in Folia morphologica and cannot belong to the 2008
psychology three-journal cohort. External psychology donors do not enter this pool.
This checks shared originals, not independence of all citing papers or field shocks.

The complete `make check` passed with the new synthesis as a dependency of the
paper build. The psychology pipeline also rebuilt offline with its full receipt
chain. The ordinary synthesis requires public frozen data only; API acquisition
remains a separate step. Input, code and output hashes are recorded in the
[synthesis receipt](../../data/meta/receipts/01_synthesize.json).

An isolated reproduction copied only the inputs and code declared in the receipt,
with no private-data directory. It regenerated all numerical CSVs, manuscript tables,
macros and the synthesis report byte-for-byte.
