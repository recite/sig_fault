RSCRIPT ?= Rscript

.PHONY: restore analysis figures tables manuscript paper format lint test check clean pilot pilot-fetch pilot-fulltext pilot-test lal lal-fetch lal-test i4r i4r-sources i4r-test i4r-aggregate nieuwenhuis nieuwenhuis-fetch nieuwenhuis-test synthesis

restore:
	$(RSCRIPT) --vanilla -e 'if (!requireNamespace("renv", quietly = TRUE)) install.packages("renv", repos = "https://cloud.r-project.org"); renv::load(project = getwd()); renv::restore(prompt = FALSE)'

analysis:
	$(RSCRIPT) scripts/run_all.R

figures: analysis
	$(RSCRIPT) scripts/figures.R

tables: analysis i4r-aggregate
	$(RSCRIPT) scripts/tables.R

manuscript:
	cd ms && latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex

paper: figures tables synthesis
	$(MAKE) manuscript

format:
	$(RSCRIPT) -e 'for (p in c("R", "scripts", "tests")) styler::style_dir(p)'

lint:
	python3 -m black --check scripts/i4r_*.py tests/test_i4r*.py scripts/nieuwenhuis*.py tests/test_nieuwenhuis*.py scripts/audit_inventories.py tests/test_audit_inventories.py
	python3 -m isort --check-only --profile black scripts/i4r_*.py tests/test_i4r*.py scripts/nieuwenhuis*.py tests/test_nieuwenhuis*.py scripts/audit_inventories.py tests/test_audit_inventories.py
	python3 -m flake8 --max-line-length=88 scripts/i4r_*.py tests/test_i4r*.py scripts/nieuwenhuis*.py tests/test_nieuwenhuis*.py scripts/audit_inventories.py tests/test_audit_inventories.py
	$(RSCRIPT) -e 'l <- unlist(lapply(c("R", "scripts", "tests"), lintr::lint_dir), recursive = FALSE); print(l); quit(status = as.integer(length(l) > 0))'

test: analysis
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

check: paper lint test inventories-test

clean:
	cd ms && latexmk -C main.tex

i4r:
	python3 scripts/i4r_registry.py build
	python3 scripts/i4r_registry.py validate
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

synthesis: analysis lal nieuwenhuis i4r-aggregate i4r-synthetic
	$(RSCRIPT) scripts/synthesis.R
	$(RSCRIPT) scripts/synthesis_secondary.R

.PHONY: i4r-synthetic
i4r-synthetic: i4r-aggregate
	OPENBLAS_NUM_THREADS=1 python3 scripts/i4r_synthetic.py

.PHONY: inventories inventories-test
inventories:
	python3 scripts/audit_inventories.py build

inventories-test: inventories
	python3 -m unittest discover -s tests -p 'test_audit_inventories.py'
