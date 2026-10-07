source("R/meta.R")
source("R/rpp.R")
source("R/analysis.R")
source("R/hmx.R")
read <- function(path) read.csv(path, stringsAsFactors = FALSE)
write <- function(x, name) write.csv(x, file.path("data/meta", name), row.names = FALSE, na = "")
base <- read("data/meta/lazic_components.csv")
ids <- read("data/meta/lazic_component_identities.csv")
rpp_ids <- read("data/cohorts/rpp/pipeline/identities.csv")
hmx_directory <- "data/cohorts/hmx/pipeline"
hmx_panel_data <- hmx_panel(hmx_directory)
hmx_data <- hmx_sample(hmx_panel_data, selection = "nonoverlap")
hmx <- panel_model(hmx_data, "nonoverlap", pre = 2017L, post = 2019L)
hmx_published <- read(file.path(hmx_directory, "estimates.csv"))
hmx_published <- hmx_published[hmx_published$specification == "nonoverlap", ]
stopifnot(
  nrow(hmx_published) == 1L,
  abs(hmx$estimate - hmx_published$estimate) < 1e-10,
  abs(hmx$se - hmx_published$se) < 1e-10
)
hmx$audit <- "HMX"
hmx$lower <- hmx$percent_lower
hmx$upper <- hmx$percent_upper
hmx_ids <- unique(hmx_data[c("article_id", "doi")])
all_ids <- rbind(ids, data.frame(
  component = "RPP", article_id = rpp_ids$paper_id, doi = rpp_ids$doi
), data.frame(component = "HMX", hmx_ids))
known <- tolower(trimws(all_ids$doi))
stopifnot(
  !anyDuplicated(known[nzchar(known)]),
  !anyDuplicated(all_ids[c("component", "article_id")])
)
write(all_ids, "assessment_identities.csv")
panel <- read("data/cohorts/rpp/pipeline/panel.csv")
panel <- panel[panel$role %in% c("successful", "unsuccessful"), ]
stopifnot(
  all(panel$status == "complete"), !anyNA(panel$citations),
  !anyDuplicated(panel[c("paper_id", "year")]),
  setequal(unique(panel$paper_id), rpp_ids$paper_id)
)
weights <- table(rpp_ids$journal) / nrow(rpp_ids)
windows <- list(primary = list(2012:2014, 2016:2018), adjacent_years = list(2014L, 2016L))
rpp <- lapply(names(windows), function(name) {
  d <- rpp_periods(panel, windows[[name]][[1]], windows[[name]][[2]])
  fit <- rpp_contrast(d, weights)
  boot <- rpp_bootstrap(d, weights)
  stopifnot(boot$undefined == 0L)
  data.frame(
    window = name, audit = "RPP", estimate = fit$log_ratio, se = boot$se_log,
    percent = 100 * expm1(fit$log_ratio), lower = boot$lower, upper = boot$upper,
    n_flagged = sum(d$role == "unsuccessful"), n_comparison = sum(d$role == "successful")
  )
})
rpp <- do.call(rbind, rpp)
write(rpp, "rpp_timing.csv")
published <- read("data/cohorts/rpp/pipeline/estimates.csv")
published <- published[published$specification == "primary", ]
stopifnot(
  nrow(published) == 1L,
  abs(rpp$estimate[1] - published$log_relative_growth) < 1e-12,
  abs(rpp$se[1] - published$se_log_bootstrap) < 1e-12
)
source_models <- read("data/nieuwenhuis/source_models.csv")
bridge <- jsonlite::read_json("data/nieuwenhuis/status.json")
stopifnot(isTRUE(bridge$full_bridge_available), bridge$complete_paired_papers == 153L)
components <- results <- sensitivities <- omissions <- list()
for (diagnostic in unique(base$lal_diagnostic)) {
  for (window in rpp$window) {
    for (source in c("historical", "openalex")) {
      selected <- base[
        base$lal_diagnostic == diagnostic & base$lazic_horizon == "first_followup_year",
        c("audit", "estimate", "se")
      ]
      if (source == "openalex") {
        x <- source_models[
          source_models$cohort == "Historical cohort" &
            source_models$source == "openalex" & source_models$post_window == "2012",
        ]
        stopifnot(nrow(x) == 1L, x$paired_papers == 153L)
        selected[selected$audit == "Nieuwenhuis", c("estimate", "se")] <- x[c("estimate", "se")]
      }
      selected <- rbind(
        selected, rpp[rpp$window == window, c("audit", "estimate", "se")],
        hmx[c("audit", "estimate", "se")]
      )
      selected$weight <- (1 / selected$se^2) / sum(1 / selected$se^2)
      tags <- data.frame(
        lal_diagnostic = diagnostic, rpp_window = window, nieuwenhuis_source = source
      )
      components[[length(components) + 1L]] <- cbind(tags, selected)
      results[[length(results) + 1L]] <- cbind(tags, precision_synthesis(selected))
      sensitivities[[length(sensitivities) + 1L]] <- cbind(
        tags, precision_synthesis(selected, random = TRUE)
      )
      for (omitted in selected$audit) {
        omissions[[length(omissions) + 1L]] <- cbind(
          tags,
          omitted = omitted, precision_synthesis(selected[selected$audit != omitted, ])
        )
      }
    }
  }
}
components <- do.call(rbind, components)
results <- do.call(rbind, results)
sensitivities <- do.call(rbind, sensitivities)
omissions <- do.call(rbind, omissions)
write(components, "assessment_components.csv")
write(results, "assessment_synthesis.csv")
write(sensitivities, "assessment_sensitivity.csv")
write(omissions, "assessment_leave_one_out.csv")
primary <- results[results$rpp_window == "primary" & results$nieuwenhuis_source == "historical", ]
primary_re <- sensitivities[
  sensitivities$rpp_window == "primary" & sensitivities$nieuwenhuis_source == "historical",
]
primary_weights <- components[
  components$rpp_window == "primary" & components$nieuwenhuis_source == "historical" &
    components$lal_diagnostic == "Effective F below 10",
]
fmt <- function(x) sprintf("%.1f", x)
macros <- c(
  RppPapers = nrow(rpp_ids), RppFailed = rpp$n_flagged[1], RppSuccessful = rpp$n_comparison[1],
  RppPercent = fmt(rpp$percent[1]), RppReduction = fmt(-rpp$percent[1]),
  RppLower = fmt(rpp$lower[1]), RppUpper = fmt(rpp$upper[1]),
  RppLevel = fmt(published$estimate_citations), RppLevelLower = fmt(published$lower_citations),
  RppLevelUpper = fmt(published$upper_citations),
  RppMetaWeight = fmt(100 * primary_weights$weight[primary_weights$audit == "RPP"])
)
for (i in seq_len(nrow(primary))) {
  prefix <- if (primary$lal_diagnostic[i] == "Effective F below 10") "Weak" else "Sensitive"
  for (field in c("percent", "lower", "upper")) {
    suffix <- paste0(toupper(substr(field, 1, 1)), substring(field, 2))
    macros[paste0("Assessment", prefix, suffix)] <- fmt(primary[[field]][i])
    macros[paste0("AssessmentRe", prefix, suffix)] <- fmt(primary_re[[field]][i])
  }
}
periods <- rpp_periods(panel, 2012:2014, 2016:2018)
for (role in c("successful", "unsuccessful")) {
  x <- periods[periods$role == role, ]
  prefix <- if (role == "successful") "RppSuccessful" else "RppFailed"
  for (period in c("pre", "post")) {
    suffix <- if (period == "pre") "Before" else "After"
    macros[paste0(prefix, "Mean", suffix)] <- fmt(mean(x[[period]]))
    macros[paste0(prefix, "Median", suffix)] <- fmt(median(x[[period]]))
  }
}
table <- function(header, rows, alignment, path) {
  writeLines(c(
    paste0("\\begin{tabular}{", alignment, "}"), "\\toprule",
    paste0(paste(header, collapse = " & "), " \\\\"), "\\midrule",
    apply(rows, 1, function(x) paste0(paste(x, collapse = " & "), " \\\\")),
    "\\bottomrule", "\\end{tabular}"
  ), path)
}
interval <- function(x) sprintf("%.1f [%.1f, %.1f]", x$percent, x$lower, x$upper)
three <- read("data/meta/lazic_components.csv")
three <- lapply(primary$lal_diagnostic, function(diagnostic) {
  precision_synthesis(three[
    three$lal_diagnostic == diagnostic & three$lazic_horizon == "first_followup_year",
  ])
})
summary_rows <- cbind(
  primary$lal_diagnostic, vapply(three, interval, character(1)),
  interval(primary), interval(primary_re)
)
table(
  c("IV definition", "Three audits", "Five studies", "Five, random effects"),
  summary_rows, "lrrr", "tabs/assessment_summary.tex"
)
base_est <- read("data/meta/audit_contrasts.csv")
lazic_est <- read("data/lazic/estimates.csv")
chosen <- rbind(
  base_est[
    base_est$audit == "Nieuwenhuis" & base_est$sample == "Historical cohort",
    c("audit", "n_flagged", "n_comparison", "percent", "lower", "upper")
  ],
  base_est[
    base_est$audit == "Lal" & base_est$diagnostic == "Effective F below 10",
    c("audit", "n_flagged", "n_comparison", "percent", "lower", "upper")
  ],
  cbind(audit = "Lazic", lazic_est[
    lazic_est$specification == "first_followup_year",
    c("n_flagged", "n_comparison", "percent", "lower", "upper")
  ]),
  rpp[1, c("audit", "n_flagged", "n_comparison", "percent", "lower", "upper")],
  hmx[c("audit", "n_flagged", "n_comparison", "percent", "lower", "upper")]
)
macros["AssessmentPapers"] <- sum(chosen$n_flagged + chosen$n_comparison)
writeLines(
  paste0("\\newcommand{\\", names(macros), "}{", macros, "}"),
  "tabs/assessment_macros.tex"
)
jsonlite::write_json(
  as.list(macros), "tabs/assessment_macros.json",
  pretty = TRUE, auto_unbox = TRUE
)
component_rows <- cbind(
  c(
    "Neuroscience", "Instrumental variables", "Animal studies",
    "Psychology replications", "Interaction models"
  ),
  paste(chosen$n_flagged, chosen$n_comparison, sep = " / "), interval(chosen),
  fmt(100 * primary_weights$weight[match(chosen$audit, primary_weights$audit)])
)
table(
  c("Study", "Adverse / comparison", "Change (\\%) [95\\% interval]", "Weight (\\%)"),
  component_rows, "lrrr", "tabs/assessment_components.tex"
)
external <- read("data/cohorts/rpp/pipeline/external_estimates.csv")
external_text <- ifelse(is.na(external$lower), sprintf("%.2f (point estimate)", external$estimate),
  sprintf("%.2f [%.2f, %.2f]", external$estimate, external$lower, external$upper)
)
table(
  c("Replication judgment", "External comparison", "Annual citation contrast"),
  cbind(external$role, external$method, external_text), "llr", "tabs/rpp_summary.tex"
)
markdown <- function(rows) {
  apply(rows, 1, function(x) paste0("| ", paste(x, collapse = " | "), " |"))
}
report <- paste(readLines("docs/meta/assessments.in.md"), collapse = "\n")
for (name in names(macros)) {
  report <- gsub(paste0("{{", name, "}}"), macros[[name]], report, fixed = TRUE)
}
report <- gsub(
  "{{COMPONENTS}}", paste(markdown(component_rows), collapse = "\n"), report,
  fixed = TRUE
)
report <- gsub("{{SUMMARY}}", paste(markdown(summary_rows), collapse = "\n"), report, fixed = TRUE)
sensitivity_rows <- cbind(
  results$lal_diagnostic, results$rpp_window, results$nieuwenhuis_source, interval(results)
)
report <- gsub(
  "{{SENSITIVITY}}", paste(markdown(sensitivity_rows), collapse = "\n"), report,
  fixed = TRUE
)
stopifnot(!grepl("{{", report, fixed = TRUE))
writeLines(report, "docs/meta/assessments.md")
status <- list(
  estimand = paste(
    "Precision-weighted mean study-specific log",
    "adverse-versus-comparison post/pre citation ratios"
  ),
  population = paste(
    "Included assessed papers in five assembled studies,",
    "not all scientific papers or errors"
  ),
  studies = c("Nieuwenhuis", "Lal", "Lazic", "RPP", "HMX"),
  five_distinct_studies = length(unique(primary_weights$audit)) == 5L,
  no_known_original_overlap = !anyDuplicated(known[nzchar(known)]),
  unidentified_doi_note = paste(
    "One Lazic paper lacks DOI: 2012 Folia morphologica,",
    "outside RPP 2008 three-journal roster"
  ),
  hmx_reproduced = TRUE, hmx_overlap_excluded = "Vernby (2013), also in Lal",
  rpp_reproduced = TRUE, rpp_role = "Replication judgment; not a statistical-error classification",
  primary_contributing_papers = sum(chosen$n_flagged + chosen$n_comparison),
  acquisition_cache_required = FALSE,
  excluded = "I4R selected three-case pilot; inventories without completed citation comparisons",
  design = "docs/meta/assessment-design.md"
)
jsonlite::write_json(status, "data/meta/assessment_status.json", pretty = TRUE, auto_unbox = TRUE)
writeLines(
  trimws(capture.output(sessionInfo()), which = "right"), "data/meta/assessment_session.txt"
)
