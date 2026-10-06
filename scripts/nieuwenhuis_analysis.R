source("R/nieuwenhuis.R")
panel <- read.csv("data/nieuwenhuis/paired_panel.csv", stringsAsFactors = FALSE)
stopifnot(length(unique(panel$article_id)) == 153L)
estimates <- summaries <- list()
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
