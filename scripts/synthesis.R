source("R/analysis.R")
source("R/lal.R")
dir.create("data/meta", recursive = TRUE, showWarnings = FALSE)

nw <- read.csv("data/derived/panel.csv", stringsAsFactors = FALSE)
lal <- read.csv("data/lal/estimates.csv", stringsAsFactors = FALSE)
levels <- read.csv("data/lal/summary.csv", stringsAsFactors = FALSE)
rows <- list()
for (sample in c("Historical cohort", "2009 publication cohort")) {
  x <- if (sample == "Historical cohort") nw else nw[nw$cohort == 2009L, ]
  fit <- panel_model(x, sample, post = 2012L)
  rows[[length(rows) + 1L]] <- data.frame(
    audit = "Nieuwenhuis", diagnostic = "Interaction-test error", source = "Web of Science",
    sample = sample, pre_year = 2010L, post_year = 2012L,
    estimate = fit$estimate, se = fit$se, df = fit$df, percent = fit$percent,
    lower = fit$percent_lower, upper = fit$percent_upper,
    n_flagged = fit$n_flagged, n_comparison = fit$n_comparison
  )
}
labels <- c(
  weak = "Effective F below 10", sensitive = "Inferential sensitivity",
  screen = "Either diagnostic", ar_loss = "AR-only sensitivity"
)
main <- lal[lal$specification == "2023 to 2025", ]
for (diagnostic in names(labels)) {
  fit <- main[main$diagnostic == diagnostic, ]
  stopifnot(nrow(fit) == 1L)
  rows[[length(rows) + 1L]] <- data.frame(
    audit = "Lal", diagnostic = labels[diagnostic], source = "OpenAlex articles/reviews",
    sample = if (diagnostic %in% c("sensitive", "ar_loss")) {
      "At least one analytically significant estimate"
    } else {
      "All assessed papers"
    }, pre_year = 2023L, post_year = 2025L,
    estimate = fit$estimate, se = fit$se, df = fit$df, percent = fit$percent,
    lower = fit$lower, upper = fit$upper,
    n_flagged = fit$n_flagged, n_comparison = fit$n_comparison
  )
}
contrasts <- do.call(rbind, rows)
write.csv(contrasts, "data/meta/audit_contrasts.csv", row.names = FALSE)
jsonlite::write_json(list(
  status = "study_specific_estimates_available_synthesis_pending",
  estimand = paste(
    "Study-specific log ratio of flagged and comparison groups' post/pre citation ratios",
    "from the full calendar year preceding the warning year to the year following it."
  ),
  limitations = c(
    "Historical Nieuwenhuis cohort includes partial publication-year baselines.",
    "Database and document-type harmonization remains incomplete.",
    "Lal formal publication followed earlier circulation; diagnostics differ from verified errors.",
    "I4R matched citation panels remain incomplete."
  ),
  pooling_rule = paste(
    "Display study-specific contrasts first. Multiple diagnostics from one audit are dependent",
    "alternatives, not independent studies. No pooled estimate is emitted at this stage."
  )
), "data/meta/status.json", pretty = TRUE, auto_unbox = TRUE)

fragment <- c(
  "\\begin{tabular}{lrrrr}", "\\toprule",
  "Diagnostic & Flagged & Comparison & Change (\\%) & 95\\% interval \\\\", "\\midrule"
)
for (diagnostic in names(labels)) {
  fit <- main[main$diagnostic == diagnostic, ]
  fragment <- c(fragment, sprintf(
    "%s & %d & %d & %.1f & [%.1f, %.1f] \\\\", labels[diagnostic],
    fit$n_flagged, fit$n_comparison, fit$percent, fit$lower, fit$upper
  ))
}
writeLines(c(fragment, "\\bottomrule", "\\end{tabular}"), "tabs/lal_summary.tex")
macros <- c(
  LalVerifiedDesigns = nrow(read.csv("data/pilot/iv_verification.csv")),
  LalPapers = length(unique(read.csv("data/lal/papers.csv")$paper_id)),
  LalARCount = main$n_flagged[main$diagnostic == "ar_loss"],
  LalWeakBroad = sprintf("%.1f", lal$percent[
    lal$diagnostic == "weak" & lal$specification == "broad_document_types"
  ])
)
for (diagnostic in c("weak", "sensitive")) {
  prefix <- if (diagnostic == "weak") "LalWeak" else "LalSensitive"
  fit <- main[main$diagnostic == diagnostic, ]
  sub <- levels[levels$diagnostic == diagnostic & levels$flag == 1L, ]
  macros[paste0(prefix, "Before")] <- sprintf("%.1f", sub$mean_2023)
  macros[paste0(prefix, "After")] <- sprintf("%.1f", sub$mean_2025)
  macros[paste0(prefix, "MedianBefore")] <- sprintf("%.1f", sub$median_2023)
  macros[paste0(prefix, "MedianAfter")] <- sprintf("%.1f", sub$median_2025)
  macros[paste0(prefix, "Change")] <- sprintf("%.1f", fit$percent)
  alternate <- lal[lal$diagnostic == diagnostic & lal$specification == "baseline_2022", ]
  macros[paste0(prefix, "Alternate")] <- sprintf("%.1f", alternate$percent)
  same_cohort <- lal$specification == "2023_baseline_same_2022_eligible_cohort"
  older <- lal[lal$diagnostic == diagnostic & same_cohort, ]
  macros[paste0(prefix, "OlderBaseline")] <- sprintf("%.1f", older$percent)
}
writeLines(paste0("\\newcommand{\\", names(macros), "}{", macros, "}"), "tabs/lal_macros.tex")
