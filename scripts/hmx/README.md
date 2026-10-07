# Interaction-audit citation pipeline

The analysis follows the 22 original papers in Hainmueller, Mummolo and Xu's audit.
The primary comparison uses severe-extrapolation labels and 2017 versus 2019 citation
counts around the December 2018 journal publication. See the
[design](../../data/cohorts/hmx/pipeline/design.md) and
[results](../../data/cohorts/hmx/pipeline/README.md), and
[data dictionary](../../data/cohorts/hmx/pipeline/data_dictionary.md).

| Stage | Operation | Main outputs |
| --- | --- | --- |
| `01_get.py` | Preserve publisher metadata and the version-one replication archive; verify original source hashes | Metadata, archive listing |
| `02_identify.py` | Resolve originals from publisher-deposited references; check author, journal, print year and cross-study overlap | Identities, overlap ledger |
| `03_design.py` | Aggregate source diagnostics without converting missing tests to favorable labels | Paper assessments, timing, citation targets |
| `04_citations.py` | Acquire complete citation lists using the shared citation module | Links, coverage, DOI decisions, annual panel |
| `05_analyze.py` | Fit the specified models and article bootstrap from public frozen data | Estimates, means, medians, influence and uncertainty checks |
| `06_report.py` | Generate report and manuscript values from those estimates | Study README, LaTeX and JSON macros |

`make hmx` reproduces estimation and reporting without a key or private files.
`make hmx-fetch` performs acquisition; the shared client reads the locally configured
OpenAlex key without recording it in receipts. `make hmx-verify` validates the source
and analysis receipt chains against local files. To replay acquisition without a
network request, run stages 01, 02 and 04 with `--offline` (stage 03 is always offline).
`make hmx-test` checks sample definitions and independently verifies the proportional
estimate and clustered standard error.

Every stage writes a receipt under `data/cohorts/hmx/pipeline/receipts/` with input,
output and code hashes and the checks actually run. Raw downloads remain in
`private-data/cohorts/hmx/pipeline/`; public analysis does not depend on that cache.
The public coverage and edge files preserve the frozen acquisition result, including
zero-history exclusions and complete citation histories.
