source("R/meta.R")
base <- read.csv("data/meta/audit_contrasts.csv", stringsAsFactors = FALSE)
lazic <- read.csv("data/lazic/estimates.csv", stringsAsFactors = FALSE)
results <- components <- list()
for (horizon in c("first_followup_year", "primary")) {
  fit <- lazic[lazic$specification == horizon, ]
  stopifnot(nrow(fit) == 1L)
  extra <- data.frame(audit = "Lazic", estimate = fit$estimate, se = fit$se, df = fit$df)
  for (diagnostic in c("Effective F below 10", "Inferential sensitivity")) {
    selected <- base[
      (base$audit == "Nieuwenhuis" & base$sample == "Historical cohort") |
        (base$audit == "Lal" & base$diagnostic == diagnostic),
      c("audit", "estimate", "se", "df")
    ]
    selected <- rbind(selected, extra)
    stopifnot(nrow(selected) == 3L)
    components[[length(components) + 1L]] <- cbind(
      lal_diagnostic = diagnostic, lazic_horizon = horizon, selected
    )
    results[[length(results) + 1L]] <- cbind(
      lal_diagnostic = diagnostic, lazic_horizon = horizon,
      equal_audit_synthesis(selected)
    )
  }
}
write.csv(do.call(rbind, components), "data/meta/lazic_components.csv", row.names = FALSE)
write.csv(do.call(rbind, results), "data/meta/lazic_synthesis.csv", row.names = FALSE)
jsonlite::write_json(list(
  status = "three_audit_descriptive_synthesis",
  estimand = paste(
    "Equal-audit mean log flagged-versus-comparison post/pre citation ratios,",
    "transformed as 100 * (exp(mean_log_ratio) - 1)."
  ),
  components = c("Nieuwenhuis", "Lal", "Lazic"),
  synthesis_results = "data/meta/lazic_synthesis.csv",
  component_estimates = "data/meta/lazic_components.csv",
  i4r_sensitivity = "data/meta/lazic_with_i4r.csv",
  openalex_source_comparison = "data/nieuwenhuis/status.json",
  primary_lazic_contrast = "2016 to 2019, first-known-publicity cohort",
  harmonized_lazic_contrast = "2016 to 2018; journal publication occurred in 2018",
  weights = "One third per audit on the log ratio-of-ratios scale",
  population = "The three assembled audits, not a random sample of publicized errors",
  limitations = c(
    "Different error definitions, databases and document types remain.",
    "The complete Nieuwenhuis OpenAlex comparison remains pending.",
    "Nieuwenhuis papers published in 2010 have partial publication-year baselines.",
    "Public availability is not verified reader exposure.",
    "Only three audits; intervals omit across-audit generalization uncertainty.",
    "The Lal formal-publication contrast follows earlier circulation.",
    "Lazic counts distinct indexed citing works of all types, including book chapters."
  )
), "data/meta/status.json", pretty = TRUE, auto_unbox = TRUE)

ids <- read.csv("data/meta/component_identities.csv", stringsAsFactors = FALSE)
articles <- read.csv("data/lazic/articles.csv", stringsAsFactors = FALSE)
changes <- read.csv("data/lazic/paper_changes.csv", stringsAsFactors = FALSE)
primary_ids <- changes$paper_id[changes$specification == "primary"]
articles <- articles[articles$article_id %in% primary_ids, ]
known <- articles$doi[nzchar(articles$doi)]
stopifnot(!length(intersect(tolower(known), tolower(ids$doi))))
write.csv(rbind(ids, data.frame(
  component = "Lazic", article_id = articles$article_id, doi = articles$doi
)), "data/meta/lazic_component_identities.csv", row.names = FALSE)

pilot <- read.csv("data/i4r/aggregate/proportional_estimate.csv", stringsAsFactors = FALSE)
stopifnot(nrow(pilot) == 1L)
four <- list()
for (x in components) {
  inputs <- rbind(
    x[c("audit", "estimate", "se", "df")],
    data.frame(audit = "I4R matched cases", pilot[c("estimate", "se", "df")])
  )
  pooled <- equal_audit_synthesis(inputs)
  names(pooled)[names(pooled) == "audits"] <- "components"
  four[[length(four) + 1L]] <- cbind(
    lal_diagnostic = x$lal_diagnostic[1], lazic_horizon = x$lazic_horizon[1], pooled
  )
}
write.csv(do.call(rbind, four), "data/meta/lazic_with_i4r.csv", row.names = FALSE)

results <- do.call(rbind, results)
primary <- results[results$lazic_horizon == "first_followup_year", ]
body <- c(
  "\\begin{tabular}{lrr}", "\\toprule",
  "IV definition & Three audits & With I4R pilot \\\\", "\\midrule"
)
four <- do.call(rbind, four)
macros <- character()
for (i in seq_len(nrow(primary))) {
  x <- primary[i, ]
  take <- four$lazic_horizon == "first_followup_year" &
    four$lal_diagnostic == x$lal_diagnostic
  extra <- four[take, ]
  body <- c(body, sprintf(
    "%s & %.1f [%.1f, %.1f] & %.1f [%.1f, %.1f] \\\\", x$lal_diagnostic,
    x$percent, x$lower, x$upper, extra$percent, extra$lower, extra$upper
  ))
  prefix <- if (x$lal_diagnostic == "Effective F below 10") "Weak" else "Sensitive"
  for (field in c("percent", "lower", "upper")) {
    suffix <- paste0(toupper(substr(field, 1, 1)), substring(field, 2))
    macros <- c(macros, sprintf(
      "\\newcommand{\\LazicMeta%s%s}{%.1f}", prefix, suffix, x[[field]]
    ))
  }
}
writeLines(c(body, "\\bottomrule", "\\end{tabular}"), "tabs/lazic_meta_summary.tex")
writeLines(macros, "tabs/lazic_meta_macros.tex")

lines <- c(
  "# Three-audit synthesis", "",
  paste(
    "The synthesis gives equal weight to the Nieuwenhuis, Lal and Lazic audit contrasts",
    "on the log ratio-of-ratios scale. It summarizes these assembled audits, not a",
    "random sample of publicized errors. I4R remains a separate four-component sensitivity."
  ), "",
  paste(
    "| IV definition | Lazic follow-up | Three audits, % [95% interval] |",
    "With I4R, % [95% interval] |"
  ),
  "| --- | ---: | ---: | ---: |"
)
for (i in seq_len(nrow(results))) {
  x <- results[i, ]
  take <- four$lazic_horizon == x$lazic_horizon &
    four$lal_diagnostic == x$lal_diagnostic
  extra <- four[take, ]
  lines <- c(lines, sprintf(
    "| %s | %s | %.1f [%.1f, %.1f] | %.1f [%.1f, %.1f] |",
    x$lal_diagnostic, if (x$lazic_horizon == "primary") "2019" else "2018",
    x$percent, x$lower, x$upper, extra$percent, extra$lower, extra$upper
  ))
}
lines <- c(lines, "", paste(
  "Nieuwenhuis uses 2010 and 2012; Lal uses 2023 and 2025; Lazic uses 2016 and 2018",
  "for the common before/after-warning contrast, with its main 2019 follow-up shown",
  "separately. The two IV definitions are alternatives from one audit, not independent",
  "studies. The I4R component summarizes only three selected matched disclosures."
), "", paste(
  "Neither three-audit definition establishes a common citation penalty. The intervals",
  "are conditional on these audits and assume independent component errors; they omit",
  "audit-selection and generalization uncertainty. Citation databases, document types,",
  "publicity clocks and error definitions remain different. An imprecise synthesis is",
  "not evidence that publicity had no effect."
), "", paste(
  "No known Lazic DOI overlaps the existing original/control DOI inventory; one",
  "included Lazic paper has no DOI. See the [component ledger]",
  "(../../data/meta/lazic_components.csv), [identity ledger]",
  "(../../data/meta/lazic_component_identities.csv), and [cohort results]",
  "(../lazic/results.md). Run `make synthesis` to reproduce."
), "", paste(
  "See [methods and sample definitions](design.md) and [current status]",
  "(../../data/meta/status.json). The [two-audit comparisons](two-audit.md)",
  "retain additional IV definitions and neuroscience source/cohort sensitivities;",
  "the [I4R extension without Lazic](secondary.md) is also available. These are",
  "alternative summaries of overlapping evidence, not additional independent studies."
))
lines <- gsub("] (", "](", lines, fixed = TRUE)
writeLines(lines, "docs/meta/README.md")
