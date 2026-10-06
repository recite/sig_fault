source("R/i4r.R")
source("R/meta.R")
panel <- read.csv("data/i4r/aggregate/analysis_panel.csv", stringsAsFactors = FALSE)
panel <- panel[panel$horizon == 1L, ]
estimate <- i4r_proportional(panel)
stopifnot(estimate$inference == "exploratory_case_delta", estimate$se > 0)

nw <- read.csv("data/nieuwenhuis/identities.csv", stringsAsFactors = FALSE)
historical <- read.csv("data/nieuwenhuis/paired_panel.csv")
nw <- nw[nw$article_id %in% historical$article_id, ]
lal <- read.csv("data/lal/identities.csv", stringsAsFactors = FALSE)
i4r <- rbind(
  read.csv("data/i4r/articles.csv", stringsAsFactors = FALSE),
  read.csv("data/i4r/control_articles.csv", stringsAsFactors = FALSE)
)
i4r <- i4r[i4r$article_id %in% panel$article_id, ]
stopifnot(
  !anyDuplicated(i4r$article_id), !anyDuplicated(tolower(trimws(i4r$doi))),
  nrow(i4r) == length(unique(panel$article_id))
)
identities <- rbind(
  data.frame(component = "Nieuwenhuis", article_id = nw$paper_id, doi = nw$doi),
  data.frame(component = "Lal", article_id = lal$paper_id, doi = lal$doi),
  data.frame(component = "I4R matched cases", article_id = i4r$article_id, doi = i4r$doi)
)
identities$doi <- tolower(trimws(identities$doi))
stopifnot(!anyNA(identities$doi), all(nzchar(identities$doi)))
overlap <- vapply(split(identities$component, identities$doi), function(x) {
  length(unique(x)) > 1L
}, logical(1))
if (any(overlap)) stop("Shared original/control DOI requires cross-component covariance")
write.csv(identities, "data/meta/component_identities.csv", row.names = FALSE)

panel$treated_post <- panel$treated * panel$post
fit <- fixest::fepois(citations ~ treated_post | article_id + post,
  data = panel, weights = ~weight, glm.tol = 1e-10, fixef.tol = 1e-10,
  nthreads = 1, notes = FALSE
)
stopifnot(isTRUE(fit$convStatus), abs(coef(fit)["treated_post"] - estimate$estimate) < 1e-7)
write.csv(estimate, "data/i4r/aggregate/proportional_estimate.csv", row.names = FALSE)
cases <- i4r_case_levels(panel)
cases$estimate <- with(cases, ifelse(
  treated_before > 0 & treated_after > 0 & control_before > 0 & control_after > 0,
  log(treated_after / treated_before) - log(control_after / control_before), NA_real_
))
cases$percent <- 100 * expm1(cases$estimate)
write.csv(cases, "data/i4r/aggregate/proportional_cases.csv", row.names = FALSE)

sensitivity <- list()
for (warning in unique(panel$warning_id)) {
  sensitivity[[length(sensitivity) + 1L]] <- cbind(
    specification = paste0("omit_", warning),
    i4r_proportional(panel[panel$warning_id != warning, ])
  )
}
alternate <- read.csv("data/i4r/aggregate/sensitivity_panel.csv", stringsAsFactors = FALSE)
for (specification in unique(alternate$specification)) {
  x <- alternate[alternate$specification == specification, ]
  sensitivity[[length(sensitivity) + 1L]] <- cbind(
    specification = specification, i4r_proportional(x)
  )
}
sensitivity <- do.call(rbind, sensitivity)
write.csv(sensitivity, "data/i4r/aggregate/proportional_sensitivity.csv", row.names = FALSE)
equal_case <- if (all(is.finite(cases$estimate))) mean(cases$estimate) else NA_real_
write.csv(data.frame(
  cases = nrow(cases), estimate = equal_case, percent = 100 * expm1(equal_case),
  estimand = "Equal-case mean log ratio; different weighting from ratio of group means"
), "data/i4r/aggregate/proportional_equal_case.csv", row.names = FALSE)

contrasts <- read.csv("data/meta/audit_contrasts.csv", stringsAsFactors = FALSE)
combined <- list()
for (cohort in unique(contrasts$sample[contrasts$audit == "Nieuwenhuis"])) {
  for (diagnostic in unique(contrasts$diagnostic[contrasts$audit == "Lal"])) {
    selected <- contrasts[
      (contrasts$audit == "Nieuwenhuis" & contrasts$sample == cohort) |
        (contrasts$audit == "Lal" & contrasts$diagnostic == diagnostic),
    ]
    inputs <- rbind(
      selected[c("audit", "estimate", "se", "df")],
      data.frame(audit = "I4R matched cases", estimate[c("estimate", "se", "df")])
    )
    pooled <- equal_audit_synthesis(inputs)
    names(pooled)[names(pooled) == "audits"] <- "components"
    combined[[length(combined) + 1L]] <- cbind(
      nw_sample = cohort, lal_diagnostic = diagnostic,
      nw_percent = selected$percent[selected$audit == "Nieuwenhuis"],
      lal_percent = selected$percent[selected$audit == "Lal"], i4r_percent = estimate$percent,
      pooled
    )
  }
}
combined <- do.call(rbind, combined)
write.csv(combined, "data/meta/three_component_synthesis.csv", row.names = FALSE)
jsonlite::write_json(list(
  status = "secondary_three_component_descriptive_synthesis",
  estimand = "Equal-component average of log relative growth in group mean citations",
  i4r_cases = estimate$cases, overlapping_original_control_dois = sum(overlap),
  covariance_assumption = paste(
    "Zero cross-component covariance; absence of shared DOIs is insufficient proof"
  ),
  primary_i4r_article_review_analysis_complete = FALSE,
  caveats = c(
    paste(
      "Retrospective, selected I4R all-type outcome with", estimate$disclosures,
      "disclosure events"
    ),
    "Different source coverage, warning definitions and exposure clocks",
    "Exploratory case-delta and Welch intervals; no between-component generalization variance",
    "This is not an identified common causal publicity effect"
  )
), "data/meta/three_component_status.json", pretty = TRUE, auto_unbox = TRUE)

primary_rows <- combined$nw_sample == "Historical cohort" &
  combined$lal_diagnostic %in% c("Effective F below 10", "Inferential sensitivity")
primary <- combined[primary_rows, ]
macros <- c(
  IfrProportional = sprintf("%.1f", estimate$percent),
  IfrProportionalLower = sprintf("%.1f", estimate$lower),
  IfrProportionalUpper = sprintf("%.1f", estimate$upper),
  IfrEqualCaseProportional = sprintf("%.1f", 100 * expm1(equal_case)),
  IfrProportionalPre = sprintf("%.1f", sensitivity$percent[
    sensitivity$specification == "placebo_pre2_pre1"
  ]),
  IfrProportionalOmitInventors = sprintf("%.1f", sensitivity$percent[
    sensitivity$specification == "omit_dp_292"
  ])
)
for (i in seq_len(nrow(primary))) {
  r <- primary[i, ]
  prefix <- if (r$lal_diagnostic == "Effective F below 10") "ThreeWeak" else "ThreeSensitive"
  for (field in c("percent", "lower", "upper")) {
    macros[paste0(prefix, tools::toTitleCase(field))] <- sprintf("%.1f", r[[field]])
  }
}
writeLines(
  paste0("\\newcommand{\\", names(macros), "}{", macros, "}"),
  "tabs/meta_secondary_macros.tex"
)
lines <- c(
  "# Secondary synthesis including the matched I4R cases", "",
  sprintf(
    paste(
      "Mean citations rose %.1f%% in the affected I4R group and %.1f%% in its matched controls.",
      "The affected group's post/pre citation ratio was %.1f%% higher than the controls'",
      "(exploratory interval [%.1f, %.1f]%%)."
    ), 100 * (estimate$treated_after / estimate$treated_before - 1),
    100 * (estimate$control_after / estimate$control_before - 1),
    estimate$percent, estimate$lower, estimate$upper
  ), "",
  sprintf(paste(
    "This ratio of group means gives more influence to highly cited papers.",
    "A different summary, the equal-case average log ratio, corresponds to %.1f%%."
  ), 100 * expm1(equal_case)), "",
  sprintf(paste(
    "In the preceding year, the affected group's post/pre ratio was already",
    "%s%% higher than controls'.",
    "Omitting the inventor-clusters disclosure changes the post-disclosure contrast to %s%%.",
    "These checks prevent interpreting the positive contrast as an increase caused by publicity."
  ), macros["IfrProportionalPre"], macros["IfrProportionalOmitInventors"]), "",
  "Neither summary makes the selected disclosures representative of the I4R collection.", "",
  paste0(
    "| Neuroscience sample | IV diagnostic | Neuroscience (%) | IV (%) | I4R (%) |",
    " Combined (%) | Exploratory 95% interval |"
  ),
  "| --- | --- | ---: | ---: | ---: | ---: | --- |"
)
for (i in seq_len(nrow(combined))) {
  r <- combined[i, ]
  lines <- c(lines, sprintf(
    "| %s | %s | %.1f | %.1f | %.1f | %.1f | [%.1f, %.1f] |",
    r$nw_sample, r$lal_diagnostic, r$nw_percent, r$lal_percent, r$i4r_percent,
    r$percent, r$lower, r$upper
  ))
}
lines <- c(
  lines, "",
  "Each component receives one third of the log-scale weight. I4R combines several",
  "individual disclosures, so this is an equal-component summary, not three independent audits.",
  "The source and document-type differences remain: historical Web of Science,",
  "OpenAlex articles/reviews for the IV audit, and OpenAlex all-type totals for I4R.",
  "The absence of shared original/control DOIs prevents direct double counting but does not",
  "establish independence: citing papers and calendar-year shocks can overlap.",
  "The intervals assume zero cross-component covariance and omit generalization uncertainty.",
  "These are descriptive sensitivity estimates, not a common causal effect of publicity.", "",
  "See [the retrospective amendment](design.md#retrospective-three-component-sensitivity),",
  "[I4R case contrasts](../../data/i4r/aggregate/proportional_cases.csv),",
  "[pre-period and leave-one-out checks](../../data/i4r/aggregate/proportional_sensitivity.csv),",
  "[component identities](../../data/meta/component_identities.csv), and",
  "[status](../../data/meta/three_component_status.json).",
  "Run `make synthesis` to rebuild."
)
writeLines(lines, "docs/meta/secondary.md")
