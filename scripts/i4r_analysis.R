source("R/i4r.R")
input <- "data/i4r/analysis_panel.csv"
panel <- read.csv(input, stringsAsFactors = FALSE)
output <- "docs/i4r/results.md"
dir.create(dirname(output), recursive = TRUE, showWarnings = FALSE)
if (!nrow(panel)) {
  unlink(file.path("data/i4r", c("estimates.csv", "descriptive.csv", "sensitivity_estimates.csv")))
  writeLines(c(
    "# Citation analysis status", "",
    paste(
      "No treatment-effect estimate is available. The current build has no",
      "complete, verified matched citation panel."
    ),
    "",
    paste(
      "Source collection and assessment review are separate from exposure-date",
      "verification, article resolution, control matching, and citation retrieval.",
      "Missing stages must not be interpreted as zero citations or a null effect."
    ),
    "",
    paste(
      "Run the acquisition stages after resolving the recorded API/access limits;",
      "the offline build will then estimate the declared matched changes. See",
      "[coverage](coverage.md) and [design](design.md)."
    )
  ), output)
} else {
  estimates <- do.call(rbind, lapply(split(panel, panel$horizon), i4r_estimate))
  write.csv(estimates, "data/i4r/estimates.csv", row.names = FALSE)
  groups <- split(panel, interaction(panel$horizon, panel$treated, panel$event_time, drop = TRUE))
  descriptive <- do.call(rbind, lapply(groups, function(g) {
    ordered <- g[order(g$citations), ]
    median <- ordered$citations[which(cumsum(ordered$weight) >= sum(ordered$weight) / 2)[1]]
    data.frame(
      horizon = g$horizon[1], treated = g$treated[1], event_time = g$event_time[1],
      mean = stats::weighted.mean(g$citations, g$weight), median = median,
      distinct_articles = length(unique(g$article_id)), weight = sum(g$weight)
    )
  }))
  write.csv(descriptive, "data/i4r/descriptive.csv", row.names = FALSE)
  sensitivities <- read.csv("data/i4r/sensitivity_panel.csv", stringsAsFactors = FALSE)
  sensitivity_results <- list()
  if (nrow(sensitivities)) {
    for (name in unique(sensitivities$specification)) {
      subset <- sensitivities[sensitivities$specification == name, ]
      result <- i4r_estimate(subset)
      result$specification <- name
      sensitivity_results[[length(sensitivity_results) + 1L]] <- result
    }
  }
  primary <- panel[panel$horizon == 1, ]
  if (length(unique(primary$warning_id)) > 1L) {
    for (warning in unique(primary$warning_id)) {
      result <- i4r_estimate(primary[primary$warning_id != warning, ])
      result$specification <- paste0("omit_disclosure_", warning)
      sensitivity_results[[length(sensitivity_results) + 1L]] <- result
    }
  }
  unlink("data/i4r/sensitivity_estimates.csv")
  if (length(sensitivity_results)) {
    write.csv(
      do.call(rbind, sensitivity_results),
      "data/i4r/sensitivity_estimates.csv",
      row.names = FALSE
    )
  }
  lines <- c(
    "# Citation changes after public error disclosure", "",
    paste(
      "Estimates apply to the dated, matched, observed subset; they are not",
      "estimates for every I4R article.", ""
    ),
    "| Horizon | Affected articles | Disclosure events | Matched change | 95% interval |",
    "| --- | ---: | ---: | ---: | --- |"
  )
  for (i in seq_len(nrow(estimates))) {
    r <- estimates[i, ]
    lines <- c(lines, sprintf(
      "| +%s year | %s | %s | %.2f | [%.2f, %.2f] |",
      r$horizon, r$affected_articles, r$disclosure_events, r$estimate, r$lower, r$upper
    ))
  }
  writeLines(c(lines, "", paste(
    "Units are additional citing journal articles/reviews per affected article.",
    "Intervals use article and disclosure-event clusters, conditional on matches;",
    "few events make inference fragile. Causal interpretation requires parallel",
    "counterfactual citation trends. Counts do not establish reliance on the error."
  )), output)
}
