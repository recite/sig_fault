source("R/nieuwenhuis.R")
source("R/analysis.R")
panel <- read.csv("data/nieuwenhuis/paired_panel.csv", stringsAsFactors = FALSE)
stopifnot(length(unique(panel$article_id)) == 153L)
estimates <- summaries <- models <- list()
for (cohort in c("Historical cohort", "2009 publication cohort")) {
  selected <- if (cohort == "Historical cohort") panel else panel[panel$cohort == 2009L, ]
  for (window in c("2012", "2012-2015")) {
    changes <- bridge_changes(selected, post = if (window == "2012") 2012L else 2012:2015)
    for (source in c("openalex", "openalex_broad")) {
      estimates[[length(estimates) + 1L]] <- cbind(
        cohort = cohort, baseline = 2010L, post = window,
        bridge_comparison(changes, source)
      )
    }
    for (source in c("wos", "openalex", "openalex_broad")) {
      if (all(0:1 %in% changes$flag)) {
        model_panel <- selected[selected$article_id %in% changes$article_id, ]
        model_panel$citations <- model_panel[[source]]
        fit <- panel_model(model_panel, "Paired citation sources",
          post = if (window == "2012") 2012L else 2012:2015
        )
        expected <- bridge_contrasts(changes, source)[["log_ratio"]]
        stopifnot(abs(fit$estimate - expected) < 1e-7)
        models[[length(models) + 1L]] <- cbind(
          cohort = cohort, source = source, post_window = window,
          paired_papers = nrow(changes), fit
        )
      }
      for (flag in intersect(0:1, changes$flag)) {
        group <- changes[changes$flag == flag, ]
        before <- group[[paste0(source, "_before")]]
        after <- group[[paste0(source, "_after")]]
        summaries[[length(summaries) + 1L]] <- data.frame(
          cohort = cohort, baseline = 2010L, post = window, source = source, flag = flag,
          papers = nrow(group), mean_before = mean(before), mean_after = mean(after),
          median_before = median(before), median_after = median(after),
          mean_change = mean(after - before), median_change = median(after - before)
        )
      }
    }
  }
}
write.csv(
  do.call(rbind, estimates), "data/nieuwenhuis/source_contrasts.csv",
  row.names = FALSE, na = ""
)
summary <- if (length(summaries)) {
  do.call(rbind, summaries)
} else {
  data.frame(
    cohort = character(), baseline = integer(), post = character(), source = character(),
    flag = integer(), papers = integer(), mean_before = numeric(), mean_after = numeric(),
    median_before = numeric(), median_after = numeric(),
    mean_change = numeric(), median_change = numeric()
  )
}
write.csv(summary, "data/nieuwenhuis/period_summary.csv", row.names = FALSE)

models <- if (length(models)) {
  do.call(rbind, models)
} else {
  data.frame(cohort = character(), source = character(), post_window = character())
}
write.csv(models, "data/nieuwenhuis/source_models.csv", row.names = FALSE)

contrasts <- do.call(rbind, estimates)
main_fit <- models[models$cohort == "Historical cohort" & models$post_window == "2012-2015", ]
main_delta <- contrasts[
  contrasts$cohort == "Historical cohort" &
    contrasts$post == "2012-2015" & contrasts$source == "openalex",
]
if (nrow(main_fit) == 3L && all(main_delta$status == "complete")) {
  oa <- main_fit[main_fit$source == "openalex", ]
  wos <- main_fit[main_fit$source == "wos", ]
  broad <- main_fit[main_fit$source == "openalex_broad", ]
  ratio <- main_delta[main_delta$estimand == "log_ratio", ]
  absolute <- main_delta[main_delta$estimand == "absolute", ]
  values <- c(
    NwOaPercent = oa$percent, NwOaLower = oa$percent_lower, NwOaUpper = oa$percent_upper,
    NwOaWosPercent = wos$percent, NwOaBroadPercent = broad$percent,
    NwOaDifference = 100 * expm1(ratio$difference),
    NwOaDifferenceLower = 100 * expm1(ratio$lower),
    NwOaDifferenceUpper = 100 * expm1(ratio$upper),
    NwOaAbsoluteDifference = absolute$difference,
    NwOaAbsoluteLower = absolute$lower, NwOaAbsoluteUpper = absolute$upper
  )
  values <- setNames(sprintf("%.1f", values), names(values))
  writeLines(
    paste0("\\newcommand{\\", names(values), "}{", values, "}"),
    "tabs/nieuwenhuis_source_macros.tex"
  )
  jsonlite::write_json(as.list(values), "tabs/nieuwenhuis_source_macros.json",
    pretty = TRUE, auto_unbox = TRUE
  )
}
