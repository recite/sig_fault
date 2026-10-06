# Citation comparisons for external error disclosures

This module connects the [larger inventories](../inventories.md) to the existing
citation collector and control matcher. The target is the change in citations
following public disclosure of a material error, relative to comparable papers
without a known assessment. The sources identify candidates; their labels do not
automatically establish an error, its consequence or its public date.

The [disclosure report](../external-disclosures.md) gives current review and
collection counts. No external treatment-effect estimate is available yet.
[Matching exclusions](../../data/external/match_exclusions.csv) retain missing
histories, incomplete comparison pools and insufficient pre-periods explicitly.

## Records

- `data/inventories/primary_reviews.json`: source passages, numerical contrasts,
  author responses, identity corrections, access limits and source hashes.
- `data/inventories/disclosure_adjudications.json`: materiality and earliest
  documented public-date decisions, made before external citation collection.
- `data/inventories/original_metadata.json`: publisher metadata, with unresolved
  lookups retained in `original_metadata_retrieval.csv`.
- `data/external/`: deduplicated original papers, review links, assessments,
  disclosure events, retraction screening, and matching outputs.

Different reviews of the same original share an article ID. Verified publication
versions are aliases; an inventory link to the wrong paper is not. Originals
already in I4R cannot create a second external event. The exact-DOI Retraction
Watch screen records its frozen source hash and cutoff. No match does not establish
exhaustive notice coverage; a retraction in the disclosure year is conservatively
treated as already retracted.

## Reproduce and collect

The offline build uses public inputs:

```sh
make external-test
```

Acquisition is explicit and uses the existing shared cache and API cooldown state:

```sh
python3 scripts/external_registry.py screen-retractions
python3 scripts/external_registry.py resolve
python3 scripts/external_registry.py candidates
python3 scripts/external_registry.py control-metadata
python3 scripts/external_registry.py fetch
make external-test
```

Use `--cache-dir PATH` on acquisition commands when resuming from an existing
private cache. Do not substitute a fresh cache to evade a provider's rate limit.
The resolver targets disclosures that pass the documented public-date and article-age
gates. Matching still requires verified metadata and a complete eligible control
pool. Original citation histories alone are insufficient.

The shared matcher uses the [I4R design](../i4r/design.md): journal and publication-age
restrictions, pre-disclosure citation levels and growth, text distance, fixed
calipers, and at most three controls. Post-disclosure outcomes do not choose controls.
Matching and effect estimation remain separate steps. No broad citation total or
statistical inconsistency is interpreted as continued use of the erroneous claim.
