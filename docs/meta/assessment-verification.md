# Verification of the five-study synthesis

Independent calculations from the exported components reproduce all eight
inverse-variance estimates and normal intervals, including the neuroscience-source
and psychology-window substitutions. All 40 leave-one-study-out coefficients,
standard errors and intervals also match. The component estimates use the specified
log-scale sampling variances, not percentile-interval widths or level standard errors.

The main contributing-paper denominator is 153 neuroscience papers, 67 IV papers,
127 animal-study papers, 98 psychology papers and 20 interaction-audit papers:
465 in total. Substituting the inferential-sensitivity IV definition uses 55 IV
papers and hence 453 originals. All-zero papers excluded from Poisson coefficients
remain in the study descriptions. Each synthesis contains one estimate per study.

Vernby (2013) appears in the IV and interaction audits. The interaction component
excludes it. No known DOI overlaps the resulting five components. The animal-study
paper without a DOI was published in 2012 in Folia morphologica and lies outside
the psychology roster and the political-science audits. External psychology donors
do not enter this pool. This checks shared originals, not independence of all
citing papers or field shocks.

The synthesis script recomputes both the psychology contrast and bootstrap and the
interaction nonoverlap coefficient and clustered standard error from public annual
panels. It checks them against their study exports and records input, code and
output hashes in the [receipt](../../data/meta/receipts/01_synthesize.json).
Acquisition remains a separate operation requiring source caches; the ordinary
paper build uses frozen public data.

An isolated run with only the public inputs and code, and no private-data directory,
regenerated 23 interaction-analysis and synthesis outputs byte-for-byte, including
numerical tables, manuscript fragments and the synthesis report. Session-information
files were excluded from byte comparison because the loaded context can differ.

The complete local `make check` passed after integration. The manuscript compiled
without unresolved references or overfull content, and all 22 rendered pages were
inspected. The complete psychology pipeline replayed offline with unchanged numerical
outputs; acquisition and analysis receipt chains were verified against their files.
