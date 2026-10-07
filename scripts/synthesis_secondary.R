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
writeLines(
  paste0("\\newcommand{\\", names(macros), "}{", macros, "}"),
  "tabs/meta_secondary_macros.tex"
)
lines <- c(
  "# Standalone I4R proportional checks", "",
  sprintf(
    "The selected %d matched cases have a relative-growth contrast of %.1f%%.",
    estimate$cases, estimate$percent
  ), "",
  "The pilot is excluded from all cross-audit synthesis. These cases remain useful",
  "for checking individual disclosure histories, matches and citation trajectories.", "",
  "See [case results](../i4r/aggregate-results.md),",
  "[proportional case data](../../data/i4r/aggregate/proportional_cases.csv), and",
  "[pre-period and leave-one-out checks](../../data/i4r/aggregate/proportional_sensitivity.csv)."
)
writeLines(lines, "docs/i4r/proportional.md")
