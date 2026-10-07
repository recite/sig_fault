source("R/meta.R")
source("R/analysis.R")
source("R/hmx.R")
read <- function(path) read.csv(path, stringsAsFactors = FALSE)
write <- function(x, name) write.csv(x, file.path("data/meta", name), row.names = FALSE, na = "")
base <- read("data/meta/lazic_components.csv")
hmx_data <- hmx_sample(hmx_panel("data/cohorts/hmx/pipeline"), selection = "nonoverlap")
hmx <- panel_model(hmx_data, "nonoverlap", pre = 2017L, post = 2019L)
hmx$audit <- "HMX"
ids <- rbind(
  read("data/meta/lazic_component_identities.csv"),
  data.frame(component = "HMX", unique(hmx_data[c("article_id", "doi")]))
)
known <- tolower(trimws(ids$doi))
stopifnot(!anyDuplicated(known[nzchar(known)]))
write(ids, "methodological_identities.csv")
source_models <- read("data/nieuwenhuis/source_models.csv")
components <- results <- sensitivities <- omissions <- list()
for (diagnostic in unique(base$lal_diagnostic)) {
  for (citation_source in c("historical", "openalex")) {
    selected <- base[
      base$lal_diagnostic == diagnostic & base$lazic_horizon == "first_followup_year",
      c("audit", "estimate", "se")
    ]
    if (citation_source == "openalex") {
      x <- source_models[
        source_models$cohort == "Historical cohort" &
          source_models$source == "openalex" & source_models$post_window == "2012",
      ]
      stopifnot(nrow(x) == 1L, x$paired_papers == 153L)
      selected[selected$audit == "Nieuwenhuis", c("estimate", "se")] <- x[c("estimate", "se")]
    }
    selected <- rbind(selected, hmx[c("audit", "estimate", "se")])
    stopifnot(setequal(selected$audit, c("Nieuwenhuis", "Lal", "Lazic", "HMX")))
    selected$weight <- (1 / selected$se^2) / sum(1 / selected$se^2)
    tags <- data.frame(lal_diagnostic = diagnostic, nieuwenhuis_source = citation_source)
    components[[length(components) + 1L]] <- cbind(tags, selected)
    results[[length(results) + 1L]] <- cbind(tags, precision_synthesis(selected))
    sensitivities[[length(sensitivities) + 1L]] <- cbind(
      tags, precision_synthesis(selected, random = TRUE)
    )
    for (omitted in selected$audit) {
      omissions[[length(omissions) + 1L]] <- cbind(tags,
        omitted = omitted,
        precision_synthesis(selected[selected$audit != omitted, ])
      )
    }
  }
}
components <- do.call(rbind, components)
results <- do.call(rbind, results)
sensitivities <- do.call(rbind, sensitivities)
write(components, "methodological_components.csv")
write(results, "methodological_synthesis.csv")
write(sensitivities, "methodological_sensitivity.csv")
write(do.call(rbind, omissions), "methodological_leave_one_out.csv")
primary <- results[results$nieuwenhuis_source == "historical", ]
primary_re <- sensitivities[sensitivities$nieuwenhuis_source == "historical", ]
base_est <- read("data/meta/audit_contrasts.csv")
lazic <- read("data/lazic/estimates.csv")
cols <- c("n_flagged", "n_comparison", "percent", "lower", "upper")
hmx$lower <- hmx$percent_lower
hmx$upper <- hmx$percent_upper
chosen <- rbind(
  base_est[
    base_est$audit == "Nieuwenhuis" & base_est$sample == "Historical cohort",
    c("audit", cols)
  ],
  base_est[
    base_est$audit == "Lal" & base_est$diagnostic == "Effective F below 10",
    c("audit", cols)
  ],
  cbind(audit = "Lazic", lazic[lazic$specification == "first_followup_year", cols]),
  hmx[c("audit", cols)]
)
fmt <- function(x) sprintf("%.1f", x)
journal_papers <- hmx_sample(
  hmx_panel("data/cohorts/hmx/pipeline"),
  selection = "journal_support"
)
hmx_papers <- read("data/cohorts/hmx/pipeline/paper_assessments.csv")
hmx_assessments <- read("data/cohorts/hmx/assessments.csv")
other_diagnostic <- hmx_papers$linearity_rejected == "flagged" |
  hmx_papers$low_high_not_rejected == "flagged"
other_concern <- hmx_papers$severe_extrapolation == "comparison" & other_diagnostic
macros <- c(
  AuditHmxOriginals = nrow(hmx_papers),
  AuditHmxInteractions = length(unique(sub(":.*", "", hmx_assessments$assessment_id))),
  AuditHmxOtherConcerns = sum(other_concern),
  AuditPapers = sum(chosen$n_flagged + chosen$n_comparison),
  AuditHmxJournalPapers = length(unique(journal_papers$article_id))
)
for (i in seq_len(nrow(primary))) {
  prefix <- if (primary$lal_diagnostic[i] == "Effective F below 10") "Weak" else "Sensitive"
  for (field in c("percent", "lower", "upper")) {
    suffix <- paste0(toupper(substr(field, 1, 1)), substring(field, 2))
    macros[paste0("Audit", prefix, suffix)] <- fmt(primary[[field]][i])
    macros[paste0("AuditRe", prefix, suffix)] <- fmt(primary_re[[field]][i])
  }
}
writeLines(
  paste0("\\newcommand{\\", names(macros), "}{", macros, "}"),
  "tabs/methodological_macros.tex"
)
jsonlite::write_json(
  as.list(macros), "tabs/methodological_macros.json",
  pretty = TRUE, auto_unbox = TRUE
)
weights <- subset(
  components, lal_diagnostic == "Effective F below 10" & nieuwenhuis_source == "historical"
)
interval <- function(x) sprintf("%.1f [%.1f, %.1f]", x$percent, x$lower, x$upper)
rows <- cbind(
  c("Neuroscience", "Instrumental variables", "Animal studies", "Interaction models"),
  paste(chosen$n_flagged, chosen$n_comparison, sep = " / "), interval(chosen),
  fmt(100 * weights$weight[match(chosen$audit, weights$audit)])
)
pooled <- primary[primary$lal_diagnostic == "Effective F below 10", ]
rows <- rbind(rows, c("Precision-weighted mean", "", interval(pooled), "100.0"))
writeLines(c(
  "\\begin{tabular}{lrrr}", "\\toprule",
  "Audit & Flagged / comparison & Change (\\%) [95\\% interval] & Weight (\\%) \\\\", "\\midrule",
  apply(rows, 1, function(x) paste0(paste(x, collapse = " & "), " \\\\")),
  "\\bottomrule", "\\end{tabular}"
), "tabs/methodological_components.tex")
jsonlite::write_json(list(
  studies = unique(weights$audit), papers = unname(as.integer(macros["AuditPapers"])),
  no_known_doi_overlap = TRUE, replication_cohorts_excluded = TRUE,
  estimand = paste(
    "Inverse-variance mean of study-specific",
    "flagged-versus-comparison log citation growth contrasts"
  )
), "data/meta/methodological_status.json", pretty = TRUE, auto_unbox = TRUE)
report <- c(
  "# Citation changes after methodological criticism", "",
  paste(
    "Four audits contribute", macros["AuditPapers"],
    "papers to the main proportional synthesis."
  ),
  "Psychology replication outcomes are analyzed separately and are not pooled here.", "",
  "| Audit | Flagged / comparison | Change, % [95% interval] | Weight, % |",
  "| --- | ---: | ---: | ---: |",
  apply(rows, 1, function(x) paste0("| ", paste(x, collapse = " | "), " |")), "",
  paste(
    "Substituting the IV inferential-sensitivity diagnostic gives",
    paste0(
      macros["AuditSensitivePercent"], "% [", macros["AuditSensitiveLower"], ", ",
      macros["AuditSensitiveUpper"], "]%."
    )
  ),
  paste(
    "The primary REML sensitivity with modified Knapp–Hartung uncertainty gives",
    paste0(
      macros["AuditReWeakPercent"], "% [", macros["AuditReWeakLower"], ", ",
      macros["AuditReWeakUpper"], "]%."
    )
  ), "",
  "These summarize selected audits, not a universal effect of publicizing errors.",
  "The assessments, document-type coverage and prior draft circulation differ across audits.",
  "Continued citation can coexist with a relative citation penalty.", "",
  "The [design](assessment-design.md),",
  "[components](../../data/meta/methodological_components.csv),",
  "[sensitivity estimates](../../data/meta/methodological_sensitivity.csv), and",
  "[leave-one-audit-out results](../../data/meta/methodological_leave_one_out.csv)",
  "document definitions and uncertainty.",
  "[The receipt](../../data/meta/receipts/01_synthesize.json)",
  "records actual inputs, code, checks and outputs."
)
writeLines(report, "docs/meta/assessments.md")
