# I4R article, error and disclosure registry

Start with [the extension guide](../../docs/i4r/README.md), [coverage](../../docs/i4r/coverage.md), [dictionary](../../docs/i4r/codebook.md), and [construction contract](../../docs/i4r/data-construction.md).

Human-reviewed inputs are `reviews/`, `curated_claims.csv`, the two article rosters, `identity_decisions.csv`, and `disclosure_adjudications.json`. Frozen acquisition inputs include the source inventory, source links, verified bibliographic metadata, retrieval logs and completed citation tables. The offline `make i4r` rebuilds article/assessment/event tables and all matching and analysis outputs.

Missing, disputed and insufficiently reviewed findings remain explicit. The current release of these data is a work in progress; a catalog review record does not mean an error was verified. No citation-effect estimate is currently available. Raw source documents are retained locally under ignored `private-data/i4r/`; URLs and hashes are public.
