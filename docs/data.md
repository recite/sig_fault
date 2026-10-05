# Data and measurement

The analysis uses the files supplied with this repository. It does not refresh citation counts from a live database. The citation workbooks were saved in April 2016; 2016 is incomplete and is excluded from the citation-rate analysis. The separate historical coding sample includes records from that partial year.

## Article classifications

`data/01_nieuwenhuis/from_nieuwenhuis/nieuwenhuis.xls` is the original author-supplied spreadsheet. The accompanying `nieuwenhuis_with_id.xls` and `.csv` add article identifiers used in the citation workbooks. The provider subsequently authorized redistribution; the earlier request in the accompanying correspondence has been superseded by that permission.

The analysis reads the CSV and checks every identifier and YES/NO classification against the identified Excel version. `Main Q = YES` means the reviewers identified an inference based on the difference between significant and nonsignificant results without the appropriate interaction test. `NO` means the paper did not make that mistake in the reviewed comparison. It is not a comprehensive certification of the paper. The original notes are retained, including uncertainty about the consequences of an error. A flagged paper is classified as having a *potentially serious* error when its note contains that phrase; other flagged papers are excluded from this subgroup comparison, not relabeled as controls.

The publication year is the first four characters of `year_volume`. Journal abbreviations `JN` and `JoN` both denote the *Journal of Neuroscience*. Source notes, dates, and bibliographic fields are not independently reinterpreted as new scientific classifications.

## Citation records

Each sheet in the two citation workbooks is labeled with the identifier of the intended cited paper. Each row is an exported database record for a purported citing document. The observation used in counting is a **citing-document–cited-paper relationship**. A document that cites multiple study papers contributes once to each of those papers.

The parser reads all fields as text, skips leading empty rows, and normalizes the first export header. One record in sheet 146 has multiple tab-delimited fields inside its title cell. Splitting these fields restores the expected schema and yields the 2009 PNAS article with DOI `10.1073/pnas.0905549106` and accession `WOS:000269806600087`. The repair requires that overflow fields be empty and that the recovered year and accession be present; malformed records cannot silently disappear.

Within each cited paper, records with the same normalized DOI count once. Where DOI is missing, accession is the key. Duplicate DOI records must agree on publication year. This removes repeated database entries without collapsing a document's citations to different study papers. No article-title fuzzy matching is used. The three false citation relationships explicitly identified in the historical coding are excluded. Every sampled relationship is checked against the original citation export.

## Coverage and unreliable searches

Two classified papers, IDs 95 and 124, have no citation sheet. Their histories are missing, not zero. Among covered papers, a year with no retained citation record is assigned zero. This assumes the available export covers the paper's citation history during the analysis window; database coverage and linkage errors may still omit citations.

Two other sheets are unsuitable as citation histories:

| Sheet | Intended paper | Evidence about the export |
| --- | --- | --- |
| 23 | Kouneiher, Charron, and Koechlin (2009), [“Motivation and cognitive control in the human prefrontal cortex”](https://doi.org/10.1038/nn.2321), *Nature Neuroscience* 12:939–945 | Contains the target paper itself, records dating to 1987, and a 2012 article whose reference list does not cite the target. |
| 25 | Löken et al. (2009), [“Coding of pleasant touch by unmyelinated afferents in humans”](https://doi.org/10.1038/nn.2312), *Nature Neuroscience* 12:547–548 | Contains the target paper itself in two database indexes and a 2007 record. The target's exported citation-count field reports many more citations than the sheet supplies. |

These facts establish a search/linkage problem, not just a mistyped year. Both sheets include the searched-for article itself and papers preceding it, a pattern consistent with exporting literature-search results instead of the intended citing-article results. The workbook stores no query text or search log, so the precise search operation cannot be reconstructed. Filtering out only the impossible dates would leave an unverified and potentially incomplete set of citations. The main analysis therefore excludes both entire histories; the sensitivity analysis retains their records within the common date window after the ordinary duplicate and known-false-link rules.

The chronology check covers every sheet. The target-self screen compares journal and year and matches the supplied page to the exported first page. The supplied page can be an internal page, so that screen is not an exhaustive identity check. These two are the only histories triggering either screen, and their target identities were confirmed by title and DOI. This screen detects impossible links but does not establish that every other link is correct. The independently checked 2012 false link in sheet 23 is Nummenmaa et al., [“Dorsal Striatum and Its Limbic Connectivity Mediate Abnormal Anticipatory Reward Processing in Obesity”](https://doi.org/10.1371/journal.pone.0031089), also identified as false in the original coding.

## Citation-context coding

`data/02_are_nw_citations_approving/post_nw_pub_citation_100_approving.csv` is the historical coding file. The manuscript describes random selection of citation relationships after 2011. We retain that realized sample rather than resampling with a modern random-number generator. The record identifiers refer to the original sampling frame, not consecutive respondent numbers.

The misleadingly named `approving` column is interpreted using the original coding protocol: `yes` records no acknowledgment of concerns; `no` records acknowledgment. An ordinary citation without criticism does not necessarily endorse every result in the cited paper. Missing codes remain missing. Notes distinguish a paper that could not be located from false citation matches; one other record has no completed code or explanation. The generated [status table](../tabs/coding_counts.csv) gives the full accounting. An explicit false-link note takes precedence over an ordinary-citation code. Sample 6937 has both: its citing paper, [Gau et al. (2013)](https://pubmed.ncbi.nlm.nih.gov/23516290/), does not include the intended [Yang et al. (2009) paper](https://pubmed.ncbi.nlm.nih.gov/19129396/) among its 48 references. It is classified as a false link; its original code and note remain available in the derived coding file.

The reported acknowledgment proportion is conditional on completed ratings of valid citation relationships. Its Wilson interval is a binomial reference interval for citation relationships, not an estimate of the fraction of researchers aware of the error. The manuscript also gives bounds that assign both unresolved, non-false records to either category. The sample includes repeated cited papers. Selection and coding error are not captured by the interval.

The original manuscript reports an independent reliability check, but the repository contains only one set of item-level codes. A second coder's ratings and the highlighted citing PDFs are not present in the source tree or data workbooks. We report the available codes without asserting independently reproduced intercoder agreement. The single recorded acknowledgment is DOI `10.1016/j.biopsycho.2014.07.013`; its full citation passage is not in the coding file, which stores a preceding sentence. The published result relies on the archived coding, not a newly completed full-text recoding.

## Generated data

`make analysis` writes the following CSV files to `data/derived/`:

| File | Key and meaning |
| --- | --- |
| `classification.csv` | `article_id`; original metadata and derived flag, seriousness, year, and journal |
| `raw.csv` | `article_id`, `accession`; imported records with repair, duplicate, false-link, chronology, and target-self indicators |
| `panel.csv` | `article_id`, `year`; balanced counts for main-analysis papers, 2009–2015 |
| `changes.csv` | `article_id`; 2010 count, 2012–2015 annual mean, and their difference |
| `coding.csv` | `sample_id`; historical code and explicit disposition |
| `annual.csv` | `flag`, `year`; means, medians, totals, zeros, and maxima |
| `estimates.csv` | named comparison; estimate, standard error, degrees of freedom, and interval |
| `year_changes.csv` | year-specific comparisons to 2010, with pointwise and simultaneous intervals |
| `leave_one_out.csv` | omitted paper; recomputed main comparison |

In `panel.csv`, the 2009 counts for papers published in 2010 are structural prepublication zeros. They appear in the descriptive trajectory but do not enter the main 2010-baseline comparison or the pre-critique check restricted to 2009 papers. Source-file SHA-256 hashes and aggregate diagnostics are generated in `tabs/results.json`.
