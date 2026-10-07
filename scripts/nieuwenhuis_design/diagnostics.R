source("R/data.R")
source("R/journal_cohort.R")
source("R/design_diagnostics.R")
source_panel <- read.csv("data/nieuwenhuis/paired_panel.csv", stringsAsFactors = FALSE)
meta <- design_characteristics(read_classification())
index <- match(source_panel$article_id, meta$article_id)
stopifnot(!anyNA(index), identical(source_panel$flag, meta$flag[index]))
stopifnot(identical(source_panel$journal, meta$journal[index]))
stopifnot(identical(source_panel$cohort, meta$cohort[index]))
fields <- c(
  "animal", "species", "subject_type", "within_between_ss", "country_authors",
  paste0("species_", c("human", "mouse", "rat", "primate", "other", "unknown")),
  "between", "country_us", "country_unknown"
)
source_panel[fields] <- meta[index, fields]
source_panel$publication_2009 <- as.integer(source_panel$cohort == 2009L)
rich <- c("journal", "cohort", "subject_type", "within_between_ss")
basic <- c("journal", "cohort")
species_columns <- c("journal", "cohort", "species", "within_between_ss")
panel <- transform(source_panel, citations = wos)
support <- journal_cohort_support(panel, rich)
eligible <- support$papers$article_id[support$papers$supported]
species_support <- journal_cohort_support(panel, species_columns)
species_eligible <- species_support$papers$article_id[species_support$papers$supported]
selection <- source_panel[source_panel$year == 2010L, ]
selection$species_supported <- selection$article_id %in% species_eligible
selection$study_type_supported <- selection$article_id %in% eligible
selection$reason <- ifelse(selection$study_type_supported, "both groups in exact cell",
  "no opposite-classification paper in exact cell"
)
output <- "data/nieuwenhuis/design"
write_result <- function(x, name) write.csv(x, file.path(output, name), row.names = FALSE)
write_result(selection, "design_characteristics.csv")
write_result(support$strata, "study_type_support.csv")
write_result(species_support$strata, "species_support.csv")
variables <- c(
  paste0("species_", c("human", "mouse", "rat", "primate", "other", "unknown")),
  "between", "country_us", "country_unknown", "publication_2009",
  "citations", "log_baseline"
)
models <- equal <- influences <- balances <- weights <- list()
for (source in c("wos", "openalex")) {
  full <- transform(source_panel, citations = source_panel[[source]])
  reference <- full[full$year == 2010L, ]
  reference$log_baseline <- log1p(reference$citations)
  unweighted <- journal_cohort_support(full)
  unweighted$papers$weight <- 1
  balances[[length(balances) + 1L]] <- transform(
    design_balance(reference, variables, unweighted, reference),
    source = source, design = "unweighted"
  )
  for (design in c(
    "journal_year", "same_sample_journal_year", "study_type",
    "species_sample_journal_year", "species"
  )) {
    ids <- if (design %in% c("species_sample_journal_year", "species")) {
      species_eligible
    } else {
      eligible
    }
    x <- if (design == "journal_year") full else full[full$article_id %in% ids, ]
    columns <- switch(design,
      study_type = rich,
      species = species_columns,
      basic
    )
    sup <- journal_cohort_support(x, columns)
    baseline <- x[x$year == 2010L, ]
    baseline$log_baseline <- log1p(baseline$citations)
    balances[[length(balances) + 1L]] <- transform(
      design_balance(baseline, variables, sup, reference),
      source = source, design = design
    )
    for (poisson in c(TRUE, FALSE)) {
      result <- journal_cohort_model(x, poisson = poisson, stratum_columns = columns)
      models[[length(models) + 1L]] <- transform(result$estimate, source = source, design = design)
      if (poisson) {
        information <- design_information(result)
        cells <- sup$strata
        cells$linear_weight <- with(cells, flagged * comparison / (flagged + comparison))
        cells$linear_weight <- cells$linear_weight / sum(cells$linear_weight)
        cells$equal_flagged_weight <- cells$flagged / sum(cells$flagged)
        cells$information_share <- information$information_share[
          match(cells$stratum, information$stratum)
        ]
        stopifnot(!anyNA(cells), all(cells$linear_weight > 0))
        weights[[length(weights) + 1L]] <- transform(cells, source = source, design = design)
      }
    }
    att <- equal_flagged_change(x, columns)
    equal[[length(equal) + 1L]] <- transform(att$estimate, source = source, design = design)
    influences[[length(influences) + 1L]] <- transform(att$papers, source = source, design = design)
  }
}
models <- do.call(rbind, models)
equal <- do.call(rbind, equal)
balances <- do.call(rbind, balances)
weights <- do.call(rbind, weights)
# Source characteristics are invariant across designs; keep a common output schema.
influence_fields <- c(
  "article_id", "flag", "journal", "cohort", "stratum", "before", "after", "change",
  "weight", "computation_weight", "outcome_weight", "leverage", "variance_share", "source", "design"
)
influences <- do.call(rbind, lapply(influences, function(x) x[influence_fields]))
write_result(models, "design_models.csv")
write_result(equal, "equal_flagged_estimates.csv")
write_result(influences, "equal_flagged_influence.csv")
write_result(balances, "balance.csv")
write_result(weights, "estimation_weights.csv")

format_value <- function(x) unname(formatC(ifelse(abs(x) < .05, 0, x), digits = 1, format = "f"))
macros <- list(
  DesignMatchedFlagged = sum(selection$study_type_supported & selection$flag == 1L),
  DesignMatchedComparison = sum(selection$study_type_supported & selection$flag == 0L),
  DesignSpeciesFlagged = sum(selection$species_supported & selection$flag == 1L),
  DesignSpeciesComparison = sum(selection$species_supported & selection$flag == 0L)
)
for (source in c("wos", "openalex")) {
  prefix <- if (source == "wos") "DesignWos" else "DesignOa"
  for (design in unique(models$design)) {
    suffix <- switch(design,
      journal_year = "Full",
      same_sample_journal_year = "Same",
      study_type = "Rich",
      species_sample_journal_year = "SpeciesSame",
      species = "Species"
    )
    m <- models[models$source == source & models$design == design & models$model == "PPML", ]
    e <- equal[equal$source == source & equal$design == design, ]
    stopifnot(nrow(m) == 1L, nrow(e) == 1L)
    values <- list(
      Percent = m$percent, Lower = m$percent_lower, Upper = m$percent_upper,
      Equal = e$estimate, EqualLower = e$lower, EqualUpper = e$upper
    )
    for (name in names(values)) {
      macros[[paste0(prefix, suffix, name)]] <- format_value(values[[name]])
    }
  }
}
human_index <- balances$source == "wos" & balances$design == "journal_year" &
  balances$variable == "species_human"
human <- balances[human_index, ]
macros$BalanceHumanFlagged <- format_value(100 * human$flagged_mean)
macros$BalanceHumanComparison <- format_value(100 * human$comparison_mean)
jsonlite::write_json(macros, "tabs/design_diagnostics_macros.json",
  auto_unbox = TRUE, pretty = TRUE
)
writeLines(
  paste0("\\newcommand{\\", names(macros), "}{", unlist(macros), "}"),
  "tabs/design_diagnostics_macros.tex"
)
table <- c(
  "\\begin{tabular}{llrrr}", "\\toprule",
  "Source & Comparison & Flagged / other & Change (\\%) & 95\\% interval \\\\",
  "\\midrule"
)
labels <- c(
  journal_year = "Journal/year, full", same_sample_journal_year = "Journal/year, 120 papers",
  study_type = "Human/animal and design", species_sample_journal_year = "Journal/year, 95 papers",
  species = "Species and design"
)
for (i in which(models$model == "PPML")) {
  r <- models[i, ]
  table <- c(table, paste0(
    if (r$source == "wos") "WoS" else "OpenAlex", " & ", labels[[r$design]], " & ",
    r$n_flagged, " / ", r$n_comparison, " & ", format_value(r$percent), " & [",
    format_value(r$percent_lower), ", ", format_value(r$percent_upper), "] \\\\"
  ))
}
writeLines(c(table, "\\bottomrule", "\\end{tabular}"), "tabs/design_diagnostics_estimates.tex")

lines <- c(
  "# Comparability and weighting diagnostics", "",
  "The design compares papers assessed in the same audit and published in the same journal/year.",
  "The balance check uses original research characteristics and pre-critique citations.",
  "It does not treat classification as randomized.", "",
  "Journal/year standardization leaves an imbalance in study populations: 25% of flagged papers",
  "study humans, versus about 55% of comparison papers. The richer comparison additionally holds",
  "human/nonhuman status and within/between-subject design fixed. Unknown subject type remains",
  "unknown. It retains 68 flagged and 52 comparison papers in 20 supported cells.",
  "The balance table also shows a remaining mouse-study imbalance. Matching exact species",
  "and within/between-subject design retains 49 flagged and 46 comparison papers in 19 cells.", "",
  "| Source | Comparison | Papers, flagged / other | Proportional change, % | 95% interval |",
  "| --- | --- | ---: | ---: | ---: |"
)
for (i in which(models$model == "PPML")) {
  r <- models[i, ]
  lines <- c(lines, sprintf(
    "| %s | %s | %d / %d | %.1f | [%.1f, %.1f] |",
    r$source, r$design, r$n_flagged, r$n_comparison, r$percent, r$percent_lower, r$percent_upper
  ))
}
lines <- c(
  lines, "",
  "The middle comparison applies the original adjustment to the retained sample, separating",
  "the change in sample from the additional adjustment. Models use 2010 versus 2012–2015.", "",
  "## An explicit equal-flagged-paper contrast", "",
  "This additive difference gives every flagged paper equal weight and compares its change with",
  "the average change of comparison papers in its cell. Effects may differ across cells.", "",
  "| Source | Comparison | Additional citations per paper per year | Approximate 95% interval |",
  "| --- | --- | ---: | ---: |"
)
for (i in seq_len(nrow(equal))) {
  r <- equal[i, ]
  lines <- c(lines, sprintf(
    "| %s | %s | %.2f | [%.2f, %.2f] |",
    r$source, r$design, r$estimate, r$lower, r$upper
  ))
}
lines <- c(
  lines, "",
  "Equal-flagged estimates are independently checked against their weighted-regression identity.",
  "Intervals use HC3 and residual t degrees of freedom, conditional on cells and weights.",
  "Ten human/nonhuman/design cells have one comparison paper; six have one flagged paper.",
  "Within-arm",
  "variances cannot be estimated separately in those singleton cells. The HC3 intervals are",
  "model-based approximations, not exact randomization or fully nonparametric intervals.", "",
  "## What the checks establish", "",
  "The original groups differ in study populations. Holding study population",
  "and within/between-subject design fixed leaves similar estimates on the same sample.",
  "This supports the comparison against that specific explanation. It does not show that all",
  "possible determinants of citation growth are balanced. The balance file also reports species,",
  "author-country labels and baseline citation counts, including standardized differences.", "",
  "The linear fixed-effects weights are nonnegative in this common-date balanced design; their",
  "formula and numerical checks are recorded. PPML information shares describe curvature",
  "of the fitted objective, not robust variance or an exact heterogeneous-effect average. The",
  "equal-flagged contrast makes its target population and article weights explicit.", "",
  "[Design and assumptions](../../../docs/nieuwenhuis/design-diagnostics.md).",
  "`design_characteristics.csv` records the original labels and every sample decision;",
  "`balance.csv`, `estimation_weights.csv` and `equal_flagged_influence.csv` record the checks."
)
writeLines(lines, file.path(output, "diagnostics.md"))
status <- list(
  full_papers = nrow(selection), matched_flagged = macros$DesignMatchedFlagged,
  matched_comparison = macros$DesignMatchedComparison,
  matched_cells = sum(support$strata$supported), balance_rows = nrow(balances),
  species_flagged = macros$DesignSpeciesFlagged,
  species_comparison = macros$DesignSpeciesComparison,
  models = nrow(models), equal_flagged_estimates = nrow(equal),
  unknown_subject_ids = selection$article_id[selection$subject_type == "unknown"],
  interpretation = "Conditional parallel-trends design; balance does not imply random assignment"
)
jsonlite::write_json(status, file.path(output, "diagnostics_status.json"),
  auto_unbox = TRUE, pretty = TRUE
)
