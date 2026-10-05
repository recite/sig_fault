.PHONY: restore analysis figures tables manuscript paper format lint test check clean pilot pilot-fetch pilot-fulltext pilot-test lal lal-fetch lal-test

restore:
	Rscript --vanilla -e 'if (!requireNamespace("renv", quietly = TRUE)) install.packages("renv", repos = "https://cloud.r-project.org"); renv::load(project = getwd()); renv::restore(prompt = FALSE)'

analysis:
	Rscript scripts/run_all.R

figures: analysis
	Rscript scripts/figures.R

tables: analysis
	Rscript scripts/tables.R

manuscript:
	cd ms && latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex

paper: figures tables
	$(MAKE) manuscript

format:
	Rscript -e 'for (p in c("R", "scripts", "tests")) styler::style_dir(p)'

lint:
	Rscript -e 'l <- unlist(lapply(c("R", "scripts", "tests"), lintr::lint_dir), recursive = FALSE); print(l); quit(status = as.integer(length(l) > 0))'

test: analysis
	$(MAKE) lal
	Rscript -e 'testthat::test_dir("tests/testthat", stop_on_failure = TRUE)'
	$(MAKE) pilot-test
	python3 -m unittest discover -s tests -p 'test_lal.py'

lal:
	python3 scripts/lal_citations.py registry
	python3 scripts/lal_citations.py panel
	Rscript scripts/lal_analysis.R

lal-fetch:
	python3 scripts/lal_citations.py fetch

lal-test: lal
	python3 -m unittest discover -s tests -p 'test_lal.py'
	Rscript -e 'testthat::test_dir("tests/testthat", filter = "lal", stop_on_failure = TRUE)'

pilot:
	Rscript scripts/pilot_registry.R
	Rscript scripts/pilot_iv_check.R
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

check: paper lint test

clean:
	cd ms && latexmk -C main.tex
