source("R/meta.R")
base <- read.csv("data/meta/audit_contrasts.csv", stringsAsFactors = FALSE)
lazic <- read.csv("data/lazic/estimates.csv", stringsAsFactors = FALSE)
results <- components <- sensitivities <- weights <- leave_one_out <- list()
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
    selected$weight <- (1 / selected$se^2) / sum(1 / selected$se^2)
    weights[[length(weights) + 1L]] <- cbind(
      lal_diagnostic = diagnostic, lazic_horizon = horizon, selected
    )
    for (method in c("equal_audit", "random_effects")) {
      fit_sensitivity <- if (method == "equal_audit") {
        z <- equal_audit_synthesis(selected)
        z$lower_one_sided_95 <- 100 * expm1(z$estimate - qt(.95, z$df) * z$se)
        z$tau2 <- z$q <- z$q_df <- z$q_p <- z$i2 <- NA_real_
        z
      } else {
        precision_synthesis(selected, random = TRUE)
      }
      sensitivities[[length(sensitivities) + 1L]] <- cbind(
        lal_diagnostic = diagnostic, lazic_horizon = horizon,
        method = method, fit_sensitivity
      )
    }
    for (omitted in selected$audit) {
      leave_one_out[[length(leave_one_out) + 1L]] <- cbind(
        lal_diagnostic = diagnostic, lazic_horizon = horizon, omitted = omitted,
        precision_synthesis(selected[selected$audit != omitted, ])
      )
    }
    components[[length(components) + 1L]] <- cbind(
      lal_diagnostic = diagnostic, lazic_horizon = horizon, selected
    )
    results[[length(results) + 1L]] <- cbind(
      lal_diagnostic = diagnostic, lazic_horizon = horizon,
      precision_synthesis(selected)
    )
  }
}
write.csv(do.call(rbind, components), "data/meta/lazic_components.csv", row.names = FALSE)
write.csv(do.call(rbind, results), "data/meta/lazic_synthesis.csv", row.names = FALSE)
write.csv(do.call(rbind, weights), "data/meta/weights.csv", row.names = FALSE)
write.csv(do.call(rbind, sensitivities), "data/meta/weighting_sensitivity.csv", row.names = FALSE)
write.csv(do.call(rbind, leave_one_out), "data/meta/leave_one_audit_out.csv", row.names = FALSE)

bridge_status <- jsonlite::read_json("data/nieuwenhuis/status.json")
stopifnot(
  isTRUE(bridge_status$full_bridge_available),
  bridge_status$complete_paired_papers == bridge_status$historical_papers
)
source_models <- read.csv("data/nieuwenhuis/source_models.csv", stringsAsFactors = FALSE)
source_variations <- list()
for (x in components) {
  for (citation_source in c("openalex", "openalex_broad")) {
    fit <- source_models[
      source_models$cohort == "Historical cohort" &
        source_models$source == citation_source & source_models$post_window == "2012",
    ]
    stopifnot(nrow(fit) == 1L, fit$paired_papers == bridge_status$historical_papers)
    selected <- x[c("audit", "estimate", "se", "df")]
    nw_row <- selected$audit == "Nieuwenhuis"
    selected[nw_row, c("estimate", "se", "df")] <- fit[c("estimate", "se", "df")]
    source_variations[[length(source_variations) + 1L]] <- cbind(
      lal_diagnostic = x$lal_diagnostic[1], lazic_horizon = x$lazic_horizon[1],
      nieuwenhuis_source = citation_source, precision_synthesis(selected)
    )
  }
}
source_variations <- do.call(rbind, source_variations)
write.csv(source_variations, "data/meta/openalex_synthesis.csv", row.names = FALSE)

jsonlite::write_json(list(
  status = "three_audit_precision_weighted_synthesis",
  estimand = paste(
    "Inverse-variance weighted mean log flagged-versus-comparison post/pre citation ratios,",
    "transformed as 100 * (exp(mean_log_ratio) - 1)."
  ),
  components = c("Nieuwenhuis", "Lal", "Lazic"),
  synthesis_results = "data/meta/lazic_synthesis.csv",
  component_estimates = "data/meta/lazic_components.csv",
  excluded_from_pooling = "I4R: three selected matched cases, retained separately",
  weights_file = "data/meta/weights.csv",
  weighting_sensitivity = "data/meta/weighting_sensitivity.csv",
  openalex_source_comparison = "data/nieuwenhuis/status.json",
  openalex_synthesis = "data/meta/openalex_synthesis.csv",
  primary_lazic_contrast = "2016 to 2019, first-known-publicity cohort",
  harmonized_lazic_contrast = "2016 to 2018; journal publication occurred in 2018",
  weights = "Inverse squared component standard error, normalized to sum to one",
  population = "The three assembled audits, not a random sample of publicized errors",
  limitations = c(
    "Different error definitions, databases and document types remain.",
    "Nieuwenhuis papers published in 2010 have partial publication-year baselines.",
    "Public availability is not verified reader exposure.",
    "Main intervals condition on included audits; REML/modified-KH is reported separately.",
    "The Lal formal-publication contrast follows earlier circulation.",
    "Lazic counts distinct indexed citing works of all types, including book chapters."
  )
), "data/meta/status.json", pretty = TRUE, auto_unbox = TRUE)

ids <- read.csv("data/meta/component_identities.csv", stringsAsFactors = FALSE)
ids <- ids[ids$component %in% c("Nieuwenhuis", "Lal"), ]
articles <- read.csv("data/lazic/articles.csv", stringsAsFactors = FALSE)
changes <- read.csv("data/lazic/paper_changes.csv", stringsAsFactors = FALSE)
primary_ids <- changes$paper_id[changes$specification == "primary"]
articles <- articles[articles$article_id %in% primary_ids, ]
known <- articles$doi[nzchar(articles$doi)]
stopifnot(!length(intersect(tolower(known), tolower(ids$doi))))
write.csv(rbind(ids, data.frame(
  component = "Lazic", article_id = articles$article_id, doi = articles$doi
)), "data/meta/lazic_component_identities.csv", row.names = FALSE)

results <- do.call(rbind, results)
primary <- results[results$lazic_horizon == "first_followup_year", ]
body <- c(
  "\\begin{tabular}{lrr}", "\\toprule",
  "IV definition & Change (\\%) & 95\\% interval \\\\", "\\midrule"
)
macros <- character()
for (i in seq_len(nrow(primary))) {
  x <- primary[i, ]
  body <- c(body, sprintf(
    "%s & %.1f & [%.1f, %.1f] \\\\", x$lal_diagnostic,
    x$percent, x$lower, x$upper
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
  "# Precision-weighted synthesis across three audits", "",
  paste(
    "The [four-study synthesis](assessments.md) adds psychology replication evidence",
    "and retains these three-audit estimates as a separately reported comparison."
  ), "",
  paste(
    "The synthesis combines the Nieuwenhuis, Lal and Lazic contrasts on the log",
    "relative-growth scale, weighting each by the inverse of its estimated sampling",
    "variance. The I4R pilot is excluded from pooling; its three matched cases",
    "remain available as [standalone comparisons](../i4r/aggregate-results.md)."
  ), "",
  "| IV definition | Lazic follow-up | Change, % | 95% interval | One-sided 95% lower bound, % |",
  "| --- | ---: | ---: | ---: | ---: |"
)
for (i in seq_len(nrow(results))) {
  x <- results[i, ]
  lines <- c(lines, sprintf(
    "| %s | %s | %.1f | [%.1f, %.1f] | %.1f |",
    x$lal_diagnostic, if (x$lazic_horizon == "primary") "2019" else "2018",
    x$percent, x$lower, x$upper, x$lower_one_sided_95
  ))
}
lines <- c(
  lines, "", paste(
    "Nieuwenhuis uses 2010 and 2012; Lal uses 2023 and 2025; Lazic uses 2016 and 2018,",
    "with its later 2019 follow-up shown separately. Each row includes one contrast per",
    "audit. The IV definitions are alternative analyses of overlapping evidence. The",
    "weights and timing choices are retrospective, after inspection of component results."
  ), "", paste(
    "The main fixed-effect interval uses the standard normal inverse-variance method",
    "and treats component variances as estimated inputs. It concerns the weighted mean",
    "of these included audit effects, not a prediction for a new audit. A causal",
    "interpretation additionally requires comparable untreated citation trajectories",
    "within the component designs."
  ), "", "## Weighting and heterogeneity", "",
  "| IV definition | Lazic follow-up | Method | Change, % [95% interval] |",
  "| --- | ---: | --- | ---: |"
)
sensitivities <- do.call(rbind, sensitivities)
for (i in seq_len(nrow(sensitivities))) {
  x <- sensitivities[i, ]
  lines <- c(lines, sprintf(
    "| %s | %s | %s | %.1f [%.1f, %.1f] |", x$lal_diagnostic,
    if (x$lazic_horizon == "primary") "2019" else "2018",
    if (x$method == "equal_audit") "Equal audit" else "REML, modified Knapp-Hartung",
    x$percent, x$lower, x$upper
  ))
}
lines <- c(lines, "", paste(
  "The random-effects sensitivity estimates between-audit heterogeneity by REML",
  "and uses modified Knapp-Hartung intervals with two degrees of freedom. The",
  "adjustment cannot shrink the standard error below its unadjusted value. Three",
  "audits supply little information about the distribution of effects across critiques."
), "", paste(
  "See the [audit weights](../../data/meta/weights.csv),",
  "[leave-one-audit-out results](../../data/meta/leave_one_audit_out.csv),",
  "[component ledger](../../data/meta/lazic_components.csv), and",
  "[identity ledger](../../data/meta/lazic_component_identities.csv).",
  "No known Lazic DOI overlaps the other audit papers; one included Lazic paper",
  "has no DOI. [Methods](design.md) and [status](../../data/meta/status.json)",
  "document scope and assumptions. Run `make synthesis` to reproduce."
))
lines <- c(
  lines, "", "## Replacing the neuroscience citation source", "", paste(
    "The following comparisons replace the historical neuroscience counts with",
    "OpenAlex on the same papers and years. Each still contains three audits;",
    "different databases do not create independent studies. The main synthesis",
    "retains the historical source. These are source sensitivities, not estimates",
    "of database bias relative to a known truth."
  ), "", "| IV definition | Lazic follow-up | OpenAlex types | Three audits, % [95% interval] |",
  "| --- | ---: | --- | ---: |"
)
for (i in seq_len(nrow(source_variations))) {
  x <- source_variations[i, ]
  lines <- c(lines, sprintf(
    "| %s | %s | %s | %.1f [%.1f, %.1f] |", x$lal_diagnostic,
    if (x$lazic_horizon == "primary") "2019" else "2018",
    if (x$nieuwenhuis_source == "openalex") "Articles/reviews" else "Broader types",
    x$percent, x$lower, x$upper
  ))
}
lines <- c(lines, "", paste(
  "See the [paired citation-source comparison](../nieuwenhuis/README.md),",
  "[source-specific model estimates](../../data/nieuwenhuis/source_models.csv), and",
  "[synthesis data](../../data/meta/openalex_synthesis.csv)."
))
lines <- gsub("] (", "](", lines, fixed = TRUE)
writeLines(lines, "docs/meta/README.md")
