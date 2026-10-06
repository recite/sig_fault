# A complete 200-paper pseudoreplication audit

Lazic, Clarke-Williams and Munafò examined whether animal studies treated dependent
observations as independent experimental units. We recovered the **entire deposited
sample of 200 papers**, including its comparison group: 91 classified as
pseudoreplication, 45 as correctly analyzed, and 64 for which reporting was too
unclear to judge. All 200 papers are identified by PMID; 198 also have a DOI.

The source concerns experiments that applied interventions to parents and examined
offspring. For example, counting offspring from the same treated litter as independent
replications can exaggerate the information supporting a result. These are the
auditors' methodological assessments. The dataset does not supply corrected effect
sizes or establish that every finding in a flagged paper is wrong.

Sources: [published audit](https://doi.org/10.1371/journal.pbio.2005282),
[complete deposited dataset](https://doi.org/10.5523/bris.2uad9gecss2r2ksaujt85gj4a).
The repository records September 6, 2017 as its publication date; the journal article
appeared April 4, 2018 and links a preprint. Thus 2018 cannot be treated as the first
public release of the classifications. The earliest preprint date and whether the
deposited file has changed since release remain timing checks before estimation.

## Data and reproduction

- [articles.csv](../../data/lazic/articles.csv): all 200 papers, classifications,
  study-design codes, bibliographic identities and source provenance.
- [raw inputs](../../data/lazic/raw/): original dataset, dictionary and readme.
- [metadata.csv](../../data/lazic/metadata.csv): exact PMID matches from PubMed.
- [notice links](../../data/lazic/notice_links.csv): all PubMed comment/correction
  relations, including prior errata for five papers. A linked erratum does not
  automatically establish a material statistical correction.
- [profile](../../data/lazic/profile.json) and
  [status](../../data/lazic/status.json): generated counts and current readiness.

Run `make lazic` offline or `make lazic-test` to rebuild and check the registry.
`python3 scripts/lazic.py fetch-metadata` refreshes the PubMed metadata from cached
or new EFetch responses. Each request contains 100 of the source PMIDs and requires
exact response coverage. Raw response files and retrieval sidecars live in
`private-data/lazic/`; public manifests record URLs and SHA-256 checksums.

The left-hand universe is the source's 200 PMIDs. The metadata join is exactly
one-to-one, with no unmatched or additional records permitted. No fuzzy title matching
is used. Duplicate DOIs stop the build for review. PMID 22648583 (flagged) and
25031729 (unclear) lack DOI metadata and remain in the registry.

The [dictionary](dictionary.md) specifies recodes and missing values; the
[analysis design](design.md) records the comparison before citation collection.
No citation-effect estimates from this cohort are available yet.
An [additional primate-research audit](other-audits.md) was inspected, but its
deposited data omit the article identities needed for citation linkage.

## Attribution and license

The dataset is credited to Marcus Munafo (2017), with contributors Charlie
Clarke-Williams and Stan Lazic, University of Bristol,
DOI 10.5523/bris.2uad9gecss2r2ksaujt85gj4a. Its original files and reused classifications
are subject to the source's
[Non-Commercial Government Licence](https://www.nationalarchives.gov.uk/doc/non-commercial-government-licence/version/2/).
They are not relicensed by this repository. The original bytes are retained, including
the `Correct_analyis` column spelling and the source readme's inconsistent filenames.
