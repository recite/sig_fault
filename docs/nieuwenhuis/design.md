# Comparing citation sources in the Nieuwenhuis cohort

The measurement question is whether replacing the historical Web of Science exports with current OpenAlex records changes the measured citation trajectories and the flagged-versus-comparison contrast for the same papers and years. A disagreement is a source discrepancy, not an identified estimate of database bias: neither source is assumed to contain every valid citation. Database coverage, reference errors, document types, version aggregation and publication dates can all contribute.

## Population and identity

Retain all 157 assessments in the supplied Nieuwenhuis workbook. The historical main analysis contains 153 papers: two lack citation exports and two have demonstrably unreliable export histories. The primary source comparison holds those 153 identities fixed. The OpenAlex extension can include the four additional papers only in a separately labeled sample. Missing API histories remain missing, never zero. Publication-year restrictions do not alter the historical bridge sample.

Resolve original articles from the source journal, issue/volume, page (which can be an internal page), and supplied URL. A unique bibliographic match must agree on the available locators. Keep candidates and conflicting locators explicit. DOI identity is checked before collecting references. Source classification remains fixed; a metadata match does not re-adjudicate the original statistical assessment.

## Outcomes and contrasts

For each database, show annual means and medians for 2009–2015, the 2010 baseline and 2012–2015 post-period average, absolute differences in changes, and the existing article/year fixed-effects Poisson proportional contrast. Repeat the proportional contrast for the common one-full-year follow-up (2010 versus 2012). For pooling with newer audits, use the latter window and show the 2009 publication cohort separately: 2010 is only a partial exposure year for papers published during 2010. Do not impose I4R's two-full-pre-year age rule retrospectively on this cohort.

OpenAlex's primary count includes articles and reviews, matching the Lal extension. Historical exports lack a document-type field beyond Web of Science's broad publication type, so their original counts cannot be described as identically type-restricted. Report that asymmetry and preserve a broader OpenAlex sensitivity. DOI overlap and year disagreement among shared citation links separate some sources of discrepancy; non-DOI links remain unresolved rather than automatically false. Manual review can establish particular false or missing links, but absence from one database alone cannot.

Source differences in the growth contrast must be estimated on the same complete-paper sample. When both groups are available, bootstrap paired paper histories within flag groups to estimate uncertainty in the difference between database contrasts. Do not subtract independent standard errors for paired measurements. Existing ten-paper pilot histories include flagged papers only and cannot identify a flagged-versus-comparison effect.

## Reproducibility and status

The protocol is retrospective: historical estimates and the Lal results are already known, and ten flagged-paper OpenAlex histories have been inspected in the separate context pilot. This document records the bridge design before acquiring the remaining histories. Public metadata, reference edges, acquisition status and source hashes remain distinct. Cached pilot histories may be reused with their original provenance; no new API result silently overwrites a frozen frame. Collection respects the shared OpenAlex rate-limit checkpoint.

A cross-audit synthesis will first display each study-specific contrast. Any pooled quantity must be labeled as an average association in the assembled cases, unless assumptions needed to identify the effect of publicity are separately justified. Lal's diagnostic flags and formal-publication date are not equivalent to verified material errors and their first public disclosure. Report those differences alongside the estimates rather than making perfect population enumeration a prerequisite for every descriptive result.
