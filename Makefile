RSCRIPT ?= Rscript

.PHONY: restore analysis figures tables manuscript paper format lint test check clean pilot pilot-fetch pilot-fulltext pilot-test lal lal-fetch lal-test i4r i4r-sources i4r-test i4r-aggregate nieuwenhuis nieuwenhuis-fetch nieuwenhuis-test synthesis

restore:
	$(RSCRIPT) --vanilla -e 'if (!requireNamespace("renv", quietly = TRUE)) install.packages("renv", repos = "https://cloud.r-project.org"); renv::load(project = getwd()); renv::restore(prompt = FALSE)'

analysis:
	$(RSCRIPT) scripts/run_all.R

figures: analysis
	$(RSCRIPT) scripts/figures.R

tables: analysis i4r-aggregate lazic-analysis nieuwenhuis synthesis
	$(RSCRIPT) scripts/tables.R

manuscript: references
	cd ms && latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex

paper: figures tables synthesis
	$(MAKE) manuscript

format:
	$(RSCRIPT) -e 'for (p in c("R", "scripts", "tests")) styler::style_dir(p)'

lint:
	python3 -m black --check scripts/research_pipeline.py scripts/citation_history.py scripts/hmx scripts/panel scripts/rpp scripts/meta scripts/references tests/test_references.py tests/test_research_pipeline.py tests/test_panel_pipeline.py
	python3 -m isort --check-only --profile black scripts/research_pipeline.py scripts/citation_history.py scripts/hmx scripts/panel scripts/rpp scripts/meta scripts/references tests/test_references.py tests/test_research_pipeline.py tests/test_panel_pipeline.py
	python3 -m flake8 --max-line-length=88 scripts/research_pipeline.py scripts/citation_history.py scripts/hmx scripts/panel scripts/rpp scripts/meta scripts/references tests/test_references.py tests/test_research_pipeline.py tests/test_panel_pipeline.py
	python3 -m black --check scripts/pilot.py tests/test_pilot.py scripts/i4r_*.py tests/test_i4r*.py scripts/nieuwenhuis*.py tests/test_nieuwenhuis*.py scripts/audit_inventories.py tests/test_audit_inventories.py scripts/inventory_events.py tests/test_inventory_events.py scripts/external_registry.py tests/test_external_registry.py scripts/lazic*.py tests/test_lazic*.py
	python3 -m isort --check-only --profile black scripts/pilot.py tests/test_pilot.py scripts/i4r_*.py tests/test_i4r*.py scripts/nieuwenhuis*.py tests/test_nieuwenhuis*.py scripts/audit_inventories.py tests/test_audit_inventories.py scripts/inventory_events.py tests/test_inventory_events.py scripts/external_registry.py tests/test_external_registry.py scripts/lazic*.py tests/test_lazic*.py
	python3 -m flake8 --max-line-length=88 scripts/pilot.py tests/test_pilot.py scripts/i4r_*.py tests/test_i4r*.py scripts/nieuwenhuis*.py tests/test_nieuwenhuis*.py scripts/audit_inventories.py tests/test_audit_inventories.py scripts/inventory_events.py tests/test_inventory_events.py scripts/external_registry.py tests/test_external_registry.py scripts/lazic*.py tests/test_lazic*.py
	$(RSCRIPT) -e 'l <- unlist(lapply(c("R", "scripts", "tests"), lintr::lint_dir), recursive = FALSE); print(l); quit(status = as.integer(length(l) > 0))'

test: analysis
	python3 -m unittest discover -s tests -p 'test_research_pipeline.py'
	$(MAKE) lal
	$(RSCRIPT) -e 'testthat::test_dir("tests/testthat", stop_on_failure = TRUE)'
	$(MAKE) pilot-test
	python3 -m unittest discover -s tests -p 'test_lal.py'
	$(MAKE) i4r-test
	$(MAKE) nieuwenhuis-test

lal:
	python3 scripts/lal_citations.py registry
	python3 scripts/lal_citations.py panel
	$(RSCRIPT) scripts/lal_analysis.R

lal-fetch:
	python3 scripts/lal_citations.py fetch

lal-test: lal
	python3 -m unittest discover -s tests -p 'test_lal.py'
	$(RSCRIPT) -e 'testthat::test_dir("tests/testthat", filter = "lal", stop_on_failure = TRUE)'

pilot:
	$(RSCRIPT) scripts/pilot_registry.R
	$(RSCRIPT) scripts/pilot_iv_check.R
	python3 scripts/pilot.py sample
	python3 scripts/pilot.py validate
	python3 scripts/pilot.py report

pilot-fetch:
	python3 scripts/pilot.py fetch

pilot-fulltext:
	python3 scripts/pilot.py fulltext
	python3 scripts/pilot.py landing
	python3 scripts/pilot.py contexts
	python3 scripts/pilot.py report

pilot-test: pilot
	python3 -m unittest discover -s tests -p 'test_pilot.py'
	python3 scripts/pilot.py validate

check: paper lint test inventories-test external-test lazic-test cohorts panel-test

clean:
	cd ms && latexmk -C main.tex

i4r:
	python3 scripts/i4r_registry.py build
	python3 scripts/i4r_registry.py validate
	$(MAKE) inventories
	python3 scripts/i4r_match.py
	$(RSCRIPT) scripts/i4r_analysis.R
	python3 scripts/i4r_report.py

i4r-sources:
	python3 scripts/i4r_sources.py fetch
	python3 scripts/i4r_sources.py expand
	python3 scripts/i4r_sources.py inventory
	python3 scripts/i4r_sources.py documents
	python3 scripts/i4r_sources.py archives --max-archive-mb 3000
	python3 scripts/i4r_sources.py manifest

i4r-test: i4r
	$(MAKE) i4r-aggregate
	python3 -m unittest discover -s tests -p 'test_i4r*.py'
	$(RSCRIPT) -e 'testthat::test_dir("tests/testthat", filter = "i4r", stop_on_failure = TRUE)'

i4r-aggregate: i4r
	python3 scripts/i4r_aggregate.py validate
	python3 scripts/i4r_match.py --citation-file data/i4r/aggregate/citations.csv --output-dir data/i4r/aggregate
	$(RSCRIPT) scripts/i4r_analysis.R data/i4r/aggregate docs/i4r/aggregate-results.md

nieuwenhuis: analysis
	python3 scripts/nieuwenhuis.py compare
	python3 scripts/nieuwenhuis_diagnostics.py build
	$(RSCRIPT) scripts/nieuwenhuis_analysis.R
	$(MAKE) nieuwenhuis-validation
	$(MAKE) nieuwenhuis-opencitations
	python3 scripts/nieuwenhuis.py report

.PHONY: nieuwenhuis-validation
nieuwenhuis-validation:
	python3 scripts/nieuwenhuis_validation.py build

nieuwenhuis-fetch:
	python3 scripts/nieuwenhuis.py resolve
	python3 scripts/nieuwenhuis.py journals
	python3 scripts/nieuwenhuis.py reconcile
	python3 scripts/nieuwenhuis.py fetch
	python3 scripts/nieuwenhuis.py manifest

nieuwenhuis-test: nieuwenhuis
	python3 -m unittest discover -s tests -p 'test_nieuwenhuis*.py'
	$(RSCRIPT) -e 'testthat::test_dir("tests/testthat", filter = "nieuwenhuis", stop_on_failure = TRUE)'

synthesis-components: analysis lal nieuwenhuis i4r-aggregate i4r-synthetic
	$(RSCRIPT) scripts/synthesis.R
	$(RSCRIPT) scripts/synthesis_secondary.R

.PHONY: i4r-synthetic
i4r-synthetic: i4r-aggregate
	OPENBLAS_NUM_THREADS=1 python3 scripts/i4r_synthetic.py

.PHONY: inventories inventories-test
inventories:
	python3 scripts/audit_inventories.py build
	python3 scripts/inventory_events.py build

inventories-test: inventories
	python3 -m unittest discover -s tests -p 'test_audit_inventories.py'
	python3 -m unittest discover -s tests -p 'test_inventory_events.py'

.PHONY: nieuwenhuis-opencitations nieuwenhuis-opencitations-fetch
nieuwenhuis-opencitations:
	python3 scripts/nieuwenhuis_opencitations.py build
	$(RSCRIPT) scripts/nieuwenhuis_opencitations.R
	python3 scripts/nieuwenhuis_opencitations.py report

nieuwenhuis-opencitations-fetch:
	python3 scripts/nieuwenhuis_validation.py fetch --full-cohort


.PHONY: external external-test
external: inventories
	python3 scripts/external_registry.py build
	python3 scripts/external_registry.py opencitations-build
	python3 scripts/i4r_match.py --data-dir data/external

external-test: external
	python3 -m unittest discover -s tests -p 'test_external_registry.py'

.PHONY: lazic lazic-test
lazic:
	python3 scripts/lazic_citations.py build
	python3 scripts/lazic.py build

lazic-test: lazic
	python3 -m unittest discover -s tests -p 'test_lazic*.py'

.PHONY: lazic-fetch
lazic-fetch:
	python3 scripts/lazic_citations.py fetch

.PHONY: lazic-analysis synthesis-components
lazic-analysis: lazic
	$(RSCRIPT) scripts/lazic_analysis.R
	python3 scripts/lazic_report.py

synthesis: lazic-analysis synthesis-components hmx
	$(RSCRIPT) scripts/lazic_synthesis.R
	META_RSCRIPT='$(RSCRIPT)' python3 -m scripts.meta.01_synthesize

.PHONY: cohorts cohorts-import cohorts-fetch
cohorts:
	$(RSCRIPT) scripts/cohort_inventory.R --validate

cohorts-import:
	$(RSCRIPT) scripts/cohort_inventory.R

cohorts-fetch:
	$(RSCRIPT) scripts/cohort_inventory.R --fetch

.PHONY: rpp rpp-fetch rpp-verify rpp-test
rpp-fetch:
	python3 -m scripts.rpp.01_get
	python3 -m scripts.rpp.02_identify
	python3 -m scripts.rpp.03_disclosures
	python3 -m scripts.rpp.04_controls
	python3 -m scripts.rpp.05_citations

rpp:
	python3 -m scripts.rpp.01_get --offline
	python3 -m scripts.rpp.02_identify
	python3 -m scripts.rpp.03_disclosures --offline
	python3 -m scripts.rpp.04_controls
	python3 -m scripts.rpp.05_citations --offline
	OPENBLAS_NUM_THREADS=1 python3 -m scripts.rpp.06_match
	RPP_RSCRIPT='$(RSCRIPT)' python3 -m scripts.rpp.07_analyze
	python3 -m scripts.rpp.08_verify

rpp-verify:
	python3 -m scripts.rpp.08_verify

rpp-test:
	python3 -m unittest discover -s tests -p 'test_research_pipeline.py'
	$(RSCRIPT) -e 'testthat::test_dir("tests/testthat", filter = "rpp", stop_on_failure = TRUE)'

.PHONY: hmx hmx-fetch hmx-verify hmx-test
hmx-fetch:
	python3 -m scripts.hmx.01_get
	python3 -m scripts.hmx.02_identify
	python3 -m scripts.hmx.03_design
	python3 -m scripts.hmx.04_citations

hmx:
	HMX_RSCRIPT='$(RSCRIPT)' python3 -m scripts.hmx.05_analyze
	python3 -m scripts.hmx.06_report

hmx-verify:
	python3 -c 'from scripts.research_pipeline import ROOT, verify_receipt; verify_receipt(ROOT / "data/cohorts/hmx/pipeline/receipts/04_citations.json"); verify_receipt(ROOT / "data/cohorts/hmx/pipeline/receipts/06_report.json")'

hmx-test:
	python3 -m unittest discover -s tests -p 'test_research_pipeline.py'
	$(RSCRIPT) -e 'testthat::test_dir("tests/testthat", filter = "hmx", stop_on_failure = TRUE)'

.PHONY: panel-sources panel-sources-fetch panel-test
panel-sources-fetch:
	python3 -m scripts.panel.01_get
	python3 -m scripts.panel.02_assessments

panel-sources:
	python3 -m scripts.panel.01_get --offline
	python3 -m scripts.panel.02_assessments

panel-test:
	python3 -m unittest discover -s tests -p 'test_panel_pipeline.py'

.PHONY: references references-fetch
references:
	python3 -m scripts.references.02_validate
	python3 -m unittest discover -s tests -p "test_references.py"

references-fetch:
	python3 -m scripts.references.01_get
