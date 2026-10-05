# Do publicized statistical errors continue to shape research?

This extension follows the **specific challenged finding into later research**. It asks whether later papers use that finding as evidence, acknowledge its limitations, or cite something else in the original article. Citation counts alone cannot make those distinctions.

The pilot is an acquisition and measurement study. It is not a completed estimate of error propagation. [Feasibility results](findings.md), [machine-readable status](../../data/pilot/status.json), the [reader packet](reader-packet.html), and the [claim records](../../data/pilot/claims.csv) distinguish work already checked from work awaiting independent readers. The published research note and its estimates remain a separate analysis.

[Two sampled examples](examples.md) show the substantive distinction: a later experiment invokes a challenged comparison when choosing stimulation conditions, whereas another paper uses a broader finding that may not depend on the challenged comparison to motivate a model. These are first-pass cases for independent review, not completed ratings.

## Design and sampling

The source registry contains 157 article assessments from Nieuwenhuis, Forstmann, and Wagenmakers and 70 IV designs from 67 papers reanalyzed by Lal, Lockhart, Xu, and Zu. The first source distinguishes a particular interaction-test error from comparisons not making that error. The second contains diagnostics, not a certification that substantive conclusions are false. These cohorts are analyzed separately.

Using seed `20261004`, the pilot selects ten of the 79 flagged neuroscience papers and ten distinct papers from the IV diagnostic screen. That screen identifies 17 distinct papers with either an effective first-stage F below 10 or an analytic IV p-value below .05 that becomes at least .05 under the archived AR or available tF procedure. The F threshold is a reproducible screening rule, not a universal weak-instrument test; crossing .05 does not prove an error. Selection is at the paper level, so multiple designs do not increase a paper's selection probability.

**Implementation refinement:** selection precedes independent claim verification. The approved strategy proposed selecting from already verified claims. Examining the source records showed that establishing such a frame is itself a central feasibility question. Keeping a random draw from the recorded assessments, including unresolved cases, lets us measure that difficulty rather than quietly substituting easier papers. No claim receives a final verified label until two readers have checked it. This is a retrospective protocol established after source inspection, not a preregistration.

All twenty selected identities were checked against bibliographic metadata and source information. Several source page numbers identify internal pages. One source labels an animal study as human; its volume, issue, internal page, methods, and full text establish the intended article. These decisions are recorded in [identities.csv](../../data/pilot/identities.csv), without changing the original workbook.

Incoming citation records are retrieved from OpenAlex through December 31, 2025. Each response must contain the target in its reference list; complete pagination and stable record counts are required. These are database-verified links, not yet full-text-verified citations. Duplicate DOIs count once per target, while one citing paper can contribute a relationship to each of several target papers. Records dated before the original article, self-links, and document types outside articles, reviews, preprints, proceedings articles, and book chapters do not enter the sample. Their disposition remains in the frame. One preprint DOI has two records with different titles and dates (2020 and 2021); both fall in the post-warning period, and it counts once. The date discrepancy remains in `duplicate_date_checks.csv` for version review. Conflicting sampling periods stop the draw. Version duplicates with different DOIs require review; the code does not assume they are independent publications.

For each paper, sample up to five pre-warning and ten post-warning relationships without replacement. SHA-256 ranks of the seed, paper, period, and citing-work ID make sampling invariant to API order and independent of full-text availability. Record both stratum sizes and inclusion probabilities. No unavailable or ambiguous paper is replaced.

The neuroscience warning date is August 26, 2011. The IV timing remains an interval: the author PDF dates its first version to July 10, 2021, whereas the identifiable public replication archive was released February 17, 2024. For this pilot, pre citations must precede the first date and post citations must be at least one calendar year after the second. Exclude intervening citations from the context sample. This conservative separation avoids assigning an unverified precise warning date; it is **not an event-study treatment date**. Earliest article-specific exposure and submission/preprint dates remain review tasks. General warnings count as public information even when they do not name particular papers.

## What has been checked

All ten selected IV point estimates reproduce from the deposited data and specifications to their reported four-decimal precision. [The verification table](../../data/pilot/iv_verification.csv) records inference differences rather than treating them as interchangeable estimates. It preserves the source's clustering and controls, uses explicit finite-sample conventions, and records covariance warnings. The joint first-stage F in this check is not always the audit's effective F.

One important discrepancy concerns Alt, Lassen, and Marshall. The instrument is an eight-level factor, giving seven excluded indicators, but the deposited summary reports one instrument. The correctly expanded joint AR test yields p=.1747, whereas the archived p=.9671 is reproduced by treating the category codes as a numeric variable. The sample remains fixed; the claim record marks the diagnostic for correction. This concerns the audit implementation and does not establish that the original paper's conclusion is false. Both calculations are independently reproduced using `lm` and the HC1 covariance matrix.

Hager and Krakowski published a [corrigendum](https://doi.org/10.1017/S000305542400008X) on February 6, 2024. It distinguishes changes to protest results from sabotage results. Readers must evaluate the corrected evidence and the precise claim being cited. The deposited audit input is not a substitute for that review.

## Measurement and analysis

Two readers first establish the challenged claim, relevant passage/table, what the criticism demonstrates, and what remains supported. Then they independently read every sampled citing paper using the [codebook](codebook.md). The unit is a citing-paper–original-paper relationship; examine all mentions and relevant qualifications, not just the first citation sentence. Consequential use includes a premise for a hypothesis, design choice, effect-size assumption, or meta-analysis input.

Primary descriptive outcomes are unqualified reliance among valid completed relationships and its distribution across original papers. Report results separately by audit and period, with both citation-weighted estimates (inverse sampling probabilities) and equal-paper summaries. Also report the number of assessed papers with any observed reliance; it is a detection measure, not an unbiased estimate of all papers ever relied upon. Missing full texts and unresolved claims are not negative outcomes. Do not generalize complete-case percentages to the full frame without addressing missingness. Intercoder agreement precedes adjudication; retain both original judgments and a separate adjudication record.

The expansion criteria are at least 80% identity-checked, readable full-text availability and at least 80% initial agreement on reliance and qualification, with category-level disagreements inspected. Report these by audit and period as well as overall. Agreement among mostly negative cases is insufficient on its own. Unresolved original claims also prevent a clean propagation estimate. Decisions to expand depend on measurement quality, not whether the results support persistent error propagation.

A later publicity analysis would select same-audit comparison papers on pre-warning information, examine at least three complete pre-warning years, and estimate each audit separately. Within-paper comparisons with unaffected findings are useful where genuinely comparable. Synthetic control requires a longer preperiod than the original neuroscience study offers. Neither model is estimated from this small, diagnostic-selected pilot.

## Reproduction

From the repository root, after `make restore`:

```sh
make pilot
make pilot-test
```

These commands use committed source data and the frozen citation frame; no network is required. Python 3.10 or newer is sufficient; its pilot code uses only the standard library. Existing R packages are pinned by `renv.lock`.

Acquisition commands require a network connection:

```sh
make pilot-fetch
make pilot-fulltext
```

The full-text command also extracts citation passages from verified XML by matching the original DOI in the reference list and locating every corresponding in-text reference. Extracted passages stay in the private cache. `context_index.csv` records what was located; failure to locate a passage does not mean the paper does not cite the original. Readers must inspect the complete text. To repeat this step on cached files, run `python3 scripts/pilot.py contexts` followed by `python3 scripts/pilot.py report`.

Successful responses and full texts are cached under ignored `private-data/pilot/`. OpenAlex's optional `OPENALEX_API_KEY` is sent only to its API and is never written into request manifests. No paid service is required. The frozen frame and sample cannot be silently overwritten by a different live result; a future refresh requires a separate named wave. Full texts are not redistributed. PDF downloads require manual identity/readability checks; a PDF file signature alone does not satisfy the availability criterion.

Copy `data/pilot/coding_template.csv` to `data/pilot/ratings.csv` before coding. Keep the template blank. `python3 scripts/pilot.py validate` rejects duplicate judgments, unknown pairs, and reliance codes without full-text review and supporting passages. Each independent reader should initially work in a separate copy; merge only after both have finished.

## Sources and contribution

- Nieuwenhuis, Forstmann, and Wagenmakers (2011), [Erroneous analyses of interactions in neuroscience](https://doi.org/10.1038/nn.2886).
- Lal, Lockhart, Xu, and Zu (2024), [67-study IV review](https://doi.org/10.1017/pan.2024.2); [replication data, version 1](https://doi.org/10.7910/DVN/MM5THZ). The deposited data license is CC0. Individual file hashes and IDs are in the archived metadata and source manifest.
- Hainmueller, Mummolo, and Xu (2019), [interaction-model review](https://doi.org/10.1017/pan.2018.46), remains a subsequent candidate cohort rather than part of this pilot.
- Serra-Garcia and Gneezy (2021), [Nonreplicable publications are cited more than replicable ones](https://escholarship.org/uc/item/04c726cc), and Clark, Connor, and Isch (2023), [Failing to replicate predicts citation declines in psychology](https://doi.org/10.1073/pnas.2304862120), establish why continued citation alone is not a new contribution. The proposed extension measures reliance on the particular challenged inference.

API references: [OpenAlex authentication](https://help.openalex.org/api/authentication/), [sorting](https://help.openalex.org/api/sorting/), [Europe PMC](https://europepmc.org/RestfulWebService), and [PMC metadata and full-text access](https://pmc.ncbi.nlm.nih.gov/tools/get-metadata/).
