.PHONY: restore analysis figures tables manuscript paper format lint test check clean

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
	Rscript -e 'testthat::test_dir("tests/testthat", stop_on_failure = TRUE)'

check: paper lint test

clean:
	cd ms && latexmk -C main.tex
