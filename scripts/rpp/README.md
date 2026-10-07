# RPP citation-study pipeline

Run from the repository root. Each numbered script has one job, reads explicit
upstream artifacts, and writes a receipt under
`data/cohorts/rpp/pipeline/receipts/`. The shared file, cache and receipt operations
live in `scripts/research_pipeline.py`; DOI normalization and authenticated HTTP
acquisition reuse `scripts/pilot.py`. Statistical functions live in `R/rpp.R`.

| Step | Script | Main outputs |
| --- | --- | --- |
| 01 | `01_get.py` | Checksummed original inputs and complete publisher metadata |
| 02 | `02_identify.py` | Verified original identities, all plausible matches, sourced decisions |
| 03 | `03_disclosures.py` | Dated announcement, project visibility logs, earlier report candidates |
| 04 | `04_controls.py` | Same-journal/year candidates, every exclusion, citation target roster |
| 05 | `05_citations.py` | Cached citing links, canonical DOI decisions, coverage, annual panel |
| 06 | `06_match.py` | Nearest controls, synthetic weights, all candidate distances and pre-fit |
| 07 | `07_analyze.py` | Estimates, diagnostics, trajectories, report and R environment |
| 08 | `08_verify.py` | Verification of the complete transitive receipt chain |

```sh
make rpp-fetch
make rpp
make rpp-verify
make rpp-test
```

`rpp-fetch` runs acquisition stages and their prerequisites, resuming from immutable
cached responses. It does not change a cached source when the live API changes.
`rpp` rebuilds everything offline and fails if a required response is absent.
Individual stages use standard Python module execution, for example:

```sh
python3 -m scripts.rpp.02_identify
python3 -m scripts.rpp.05_citations --offline --workers 4
```

OpenAlex credentials come from `OPENALEX_API_KEY` or
`~/.config/openalex/api_key` and are sent in an authorization header. Receipts and
cache filenames never contain the key. Python dependencies are listed in
the shared `requirements-i4r.txt`; R dependencies use the existing `renv.lock`.

## What a receipt proves

Receipts record the actual command, runtime, Git revision, executed-code hashes,
input/output hashes and CSV row counts, source URLs, retrieval timestamps,
executed checks, coverage and unresolved cases. Parent receipts are hashed and
verified recursively. Changing upstream code or a source invalidates descendants
even if an old output file remains on disk. A stage that raises an exception writes
a failed receipt; it cannot satisfy a downstream dependency.

Execution completion and scientific resolution are distinct. For example, the
disclosure step can finish collecting every project log while still leaving
first-disclosure dates unresolved. The citation stage retains incomplete histories
as missing. The estimation stage requires all 98 original citation histories.

Re-running a stage replaces its current receipt with the new run's evidence.
Git records released receipts; the original downloaded sources remain immutable.
No separate copies of old scripts are needed.

## Study-specific decisions

The [design](../../data/cohorts/rpp/pipeline/design.md) specifies the estimand,
windows, journal standardization, controls and inference. The
[identity ledger](../../data/cohorts/rpp/pipeline/identity_decisions.json) records
source corrections without modifying downloaded originals. Report-upload dates
and filenames remain candidate timing evidence; they are not silently promoted
to first disclosure. Raw responses are in `private-data/cohorts/rpp/pipeline/`.

The pipeline applies three nearest neighbors within verified journal and print
year, using annual 2010–2014 log(1 + citations) standardized by donor-year standard
deviations. Synthetic controls fit raw pre-period counts, standardized by donor-year
standard deviations, with nonnegative weights summing to one and a fixed 1e-6 ridge
penalty. Post-period outcomes never
enter either fit. Reused controls retain their original article IDs in inference.
