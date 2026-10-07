# Historical versions of the panel-study audit

The dated 2023 source contains 37 original-paper references. Its pretrend
F-test classifies 8 as rejected and 25 as not rejected; 4
tests are unavailable. The final source inventory contains 49 papers. The
historical table preserves the diagnostic labels available in that version instead
of assigning the later labels to an earlier publication date.

The source is [arXiv version 1](https://arxiv.org/pdf/2309.15983v1), whose PDF carries
the September 27, 2023 archive date. The manuscript also lists July 5, 2022 as its
first-version date; that establishes earlier writing, not a verified public posting.
Its archived LaTeX `sm.tex`, Table A1, supplies the paper references and five
explicitly named test indicators. Citation keys link to `tscs.bib`. All 37
rows agree with a separate extraction reviewed against the source.

`x` means the statement in a diagnostic header holds. A blank means it does not;
`n.a.` remains unavailable. A rejected pretrend test identifies a design concern,
not proof that the original substantive conclusion is false. Missing tests do not
become comparison papers. Commented-out rows in the LaTeX source are not assessed
papers in the published historical table.

The citation analysis has not been run. Original DOI identities, correspondence
with the final roster, overlap with existing studies, and earlier public reports
must be verified before fixing its comparison and collecting citations. In
particular, Payson's a/b suffixes differ across versions; bibliography keys and
DOIs must establish identity.

From the repository root:

```
python3 -m scripts.panel.01_get
python3 -m scripts.panel.02_assessments
```

Stage 01 downloads and hashes the dated source archive, PDF and journal metadata.
It checks the existing final-supplement hashes and extracts only the three named
source files without executing the authors' code. Add `--offline` to replay from
the immutable cache. Stage 02 parses the historical table, validates the diagnostic
marks and emits [paper references and labels](historical_assessments.csv),
[diagnostic counts](historical_diagnostic_counts.csv), and this report. Both stages
record [receipts](receipts/) with code, input and output hashes. Raw downloads remain
in `private-data/cohorts/panel/pipeline/`.
