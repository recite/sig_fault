source("R/nieuwenhuis.R")
source("R/analysis.R")
panel <- read.csv("data/nieuwenhuis/opencitations_panel.csv", stringsAsFactors = FALSE)
estimates <- summaries <- annual <- models <- list()
for (sample in c("Available histories", "Histories without unresolved years")) {
  sample_rows <- panel[panel$status == "complete", ]
  if (sample != "Available histories") {
    sample_rows <- sample_rows[sample_rows$undated_works == 0L, ]
  }
  for (cohort in c("Historical cohort", "2009 publication cohort")) {
    selected <- if (cohort == "Historical cohort") {
      sample_rows
    } else {
      sample_rows[sample_rows$cohort == 2009L, ]
    }
    for (window in c("2012", "2012-2015")) {
      changes <- bridge_changes(selected,
        post = if (window == "2012") 2012L else 2012:2015,
        sources = c("wos", "opencitations")
      )
      estimates[[length(estimates) + 1L]] <- cbind(
        sample = sample, cohort = cohort, baseline = 2010L, post = window,
        bridge_comparison(changes, "opencitations")
      )
      for (source in c("wos", "opencitations")) {
        if (all(0:1 %in% changes$flag)) {
          model_panel <- selected
          model_panel$citations <- model_panel[[source]]
          fit <- panel_model(model_panel, "Source comparison",
            post = if (window == "2012") 2012L else 2012:2015
          )
          expected <- bridge_contrasts(changes, source)[["log_ratio"]]
          stopifnot(abs(fit$estimate - expected) < 1e-7)
          models[[length(models) + 1L]] <- cbind(
            sample = sample, cohort = cohort, source = source, post_window = window, fit
          )
        }
        for (flag in intersect(0:1, changes$flag)) {
          group <- changes[changes$flag == flag, ]
          before <- group[[paste0(source, "_before")]]
          after <- group[[paste0(source, "_after")]]
          summaries[[length(summaries) + 1L]] <- data.frame(
            sample = sample, cohort = cohort, baseline = 2010L, post = window,
            source = source, flag = flag, papers = nrow(group),
            mean_before = mean(before), mean_after = mean(after),
            median_before = median(before), median_after = median(after)
          )
        }
      }
    }
  }
  for (source in c("wos", "opencitations")) {
    for (year in sort(unique(sample_rows$year))) {
      for (flag in intersect(0:1, sample_rows$flag)) {
        group <- sample_rows[sample_rows$year == year & sample_rows$flag == flag, ]
        annual[[length(annual) + 1L]] <- data.frame(
          sample = sample, source = source, year = year, flag = flag,
          papers = nrow(group), mean = mean(group[[source]]), median = median(group[[source]])
        )
      }
    }
  }
}
write.csv(do.call(rbind, estimates),
  "data/nieuwenhuis/opencitations_contrasts.csv",
  row.names = FALSE, na = ""
)
write.csv(do.call(rbind, summaries),
  "data/nieuwenhuis/opencitations_period_summary.csv",
  row.names = FALSE, na = ""
)
write.csv(do.call(rbind, annual),
  "data/nieuwenhuis/opencitations_annual_summary.csv",
  row.names = FALSE, na = ""
)

write.csv(do.call(rbind, models),
  "data/nieuwenhuis/opencitations_models.csv",
  row.names = FALSE, na = ""
)
