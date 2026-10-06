source("R/analysis.R")
source("R/lal.R")
source("R/meta.R")
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
  status = "provisional_two_audit_synthesis_available",
  secondary_synthesis = "three_component_status.json describes the retrospective I4R extension",
  estimand = paste(
    "Equal-audit average of log flagged-versus-comparison post/pre citation ratios",
    "from the full calendar year preceding the warning year to the year following it."
  ),
  limitations = c(
    "Historical Nieuwenhuis cohort includes partial publication-year baselines.",
    "Database and document-type harmonization remains incomplete.",
    "Lal formal publication followed earlier circulation; diagnostics differ from verified errors.",
    paste(
      "Primary I4R article/review citation panels remain incomplete;",
      "secondary all-type absolute contrasts and a three-component",
      "proportional sensitivity are available."
    ),
    "Intervals assume independent audit errors and omit generalization uncertainty."
  ),
  pooling_rule = paste(
    "Display study-specific contrasts first. Multiple diagnostics from one audit are dependent",
    "alternatives, not independent studies. Each synthesis includes one contrast per audit."
  )
), "data/meta/status.json", pretty = TRUE, auto_unbox = TRUE)

combined <- list()
for (sample in unique(contrasts$sample[contrasts$audit == "Nieuwenhuis"])) {
  for (diagnostic in names(labels)) {
    take <- (contrasts$audit == "Nieuwenhuis" & contrasts$sample == sample) |
      (contrasts$audit == "Lal" & contrasts$diagnostic == labels[diagnostic])
    selected <- contrasts[take, ]
    result <- equal_audit_synthesis(selected)
    combined[[length(combined) + 1L]] <- cbind(
      nw_sample = sample, lal_diagnostic = labels[diagnostic],
      nw_percent = selected$percent[selected$audit == "Nieuwenhuis"],
      lal_percent = selected$percent[selected$audit == "Lal"], result
    )
  }
}
combined <- do.call(rbind, combined)
write.csv(combined, "data/meta/synthesis.csv", row.names = FALSE)
oc_models <- read.csv("data/nieuwenhuis/opencitations_models.csv", stringsAsFactors = FALSE)
take_oc <- oc_models$sample == "Available histories" &
  oc_models$source == "opencitations" & oc_models$post_window == "2012"
oc_models <- oc_models[take_oc, ]
source_sensitivity <- list()
for (sample in unique(contrasts$sample[contrasts$audit == "Nieuwenhuis"])) {
  fit <- oc_models[oc_models$cohort == sample, ]
  stopifnot(nrow(fit) == 1L)
  for (diagnostic in names(labels)) {
    take <- (contrasts$audit == "Nieuwenhuis" & contrasts$sample == sample) |
      (contrasts$audit == "Lal" & contrasts$diagnostic == labels[diagnostic])
    selected <- contrasts[take, ]
    replace <- selected$audit == "Nieuwenhuis"
    selected$estimate[replace] <- fit$estimate
    selected$se[replace] <- fit$se
    selected$df[replace] <- fit$df
    source_sensitivity[[length(source_sensitivity) + 1L]] <- cbind(
      nw_sample = sample, lal_diagnostic = labels[diagnostic],
      nw_source = "OpenCitations dated works, all types", nw_percent = fit$percent,
      equal_audit_synthesis(selected)
    )
  }
}
source_sensitivity <- do.call(rbind, source_sensitivity)
write.csv(source_sensitivity, "data/meta/opencitations_synthesis.csv", row.names = FALSE)

body <- c(
  "\\begin{tabular}{lrrrl}", "\\toprule",
  "IV diagnostic & Neuroscience & IV audit & Combined & 95\\% interval \\\\", "\\midrule"
)
primary_rows <- combined$nw_sample == "Historical cohort" &
  combined$lal_diagnostic %in% labels[c("weak", "sensitive")]
for (i in which(primary_rows)) {
  row <- combined[i, ]
  body <- c(body, sprintf(
    "%s & %.1f & %.1f & %.1f & [%.1f, %.1f] \\\\", row$lal_diagnostic,
    row$nw_percent, row$lal_percent, row$percent, row$lower, row$upper
  ))
}
writeLines(c(body, "\\bottomrule", "\\end{tabular}"), "tabs/meta_summary.tex")

meta_macros <- c()
for (diagnostic in c("weak", "sensitive")) {
  main_cohort <- combined$nw_sample == "Historical cohort"
  row <- combined[main_cohort & combined$lal_diagnostic == labels[diagnostic], ]
  prefix <- if (diagnostic == "weak") "MetaWeak" else "MetaSensitive"
  for (field in c("percent", "lower", "upper")) {
    meta_macros[paste0(prefix, tools::toTitleCase(field))] <- sprintf("%.1f", row[[field]])
  }
}
writeLines(
  paste0("\\newcommand{\\", names(meta_macros), "}{", meta_macros, "}"),
  "tabs/meta_macros.tex"
)
dir.create("docs/meta", recursive = TRUE, showWarnings = FALSE)
report <- c(
  "# Provisional synthesis across two methodological audits", "",
  "The completed neuroscience and IV cohorts permit a common-window summary, while",
  "the full OpenAlex neuroscience comparison and primary I4R article/review panels remain pending.",
  "Every row below includes one estimate from each audit, with equal audit weights.",
  "Alternative IV diagnostics are separate analyses of the same evidence.", "",
  paste0(
    "| Neuroscience sample | IV diagnostic | Neuroscience (%) | IV (%) | ",
    "Combined (%) | 95% interval |"
  ),
  "| --- | --- | ---: | ---: | ---: | --- |"
)
for (i in seq_len(nrow(combined))) {
  row <- combined[i, ]
  report <- c(report, sprintf(
    "| %s | %s | %.1f | %.1f | %.1f | [%.1f, %.1f] |",
    row$nw_sample, row$lal_diagnostic, row$nw_percent, row$lal_percent,
    row$percent, row$lower, row$upper
  ))
}
report <- c(
  report, "",
  "The combined estimate changes with the IV diagnostic. It is not evidence for",
  "a uniform citation response, nor an estimate of the effect of the typical scientific error.",
  "The AR-only rows are exploratory: their IV component has only three flagged papers.", "",
  "A [secondary three-component synthesis](secondary.md) adds the proportional contrast",
  "from the separately matched I4R annual-total analysis. It preserves the different",
  "measurement and exposure definitions and is an exploratory descriptive extension.", "",
  "A [source sensitivity](../../data/meta/opencitations_synthesis.csv) replaces the",
  "neuroscience component with OpenCitations on the same papers and years. It does",
  "not add another independent audit; see the",
  "[measurement comparison](../nieuwenhuis/opencitations.md).",
  "",
  "See [methods](design.md), [component estimates](../../data/meta/audit_contrasts.csv),",
  "[synthesis data](../../data/meta/synthesis.csv), and [status](../../data/meta/status.json).",
  "Run `make synthesis` to reproduce these results and the manuscript table."
)
writeLines(report, "docs/meta/README.md")

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
