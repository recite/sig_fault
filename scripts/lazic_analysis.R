source("R/lal.R")
source("R/lazic.R")

panel <- read.csv("data/lazic/opencitations/panel.csv", stringsAsFactors = FALSE)
articles <- read.csv("data/lazic/articles.csv", stringsAsFactors = FALSE)
prior <- read.csv("data/lazic/prior_warnings.csv", colClasses = "character")
notices <- read.csv("data/lazic/notice_links.csv", colClasses = "character")
stopifnot(!anyDuplicated(articles$article_id), !anyDuplicated(panel[c("article_id", "year")]))
stopifnot(setequal(unique(panel$article_id), articles$article_id))
meta <- articles[match(panel$article_id, articles$article_id), ]
panel$pmid <- as.character(meta$pmid)
panel$publication_year <- meta$publication_year
panel$split_unit <- meta$split_unit
panel$journal <- meta$journal
panel <- panel[!is.na(panel$flagged), ]
stopifnot(all(panel$status == "complete"), !anyNA(panel$citations))
primary <- panel[!panel$pmid %in% prior$pmid, ]
errata <- notices$pmid[notices$relation == "ErratumIn"]
samples <- list(
  primary = primary,
  all_classified = panel,
  exclude_all_prior_errata = primary[!primary$pmid %in% errata, ],
  older_cohort = primary[primary$publication_year <= 2013L, ]
)
absolute <- proportional <- summaries <- changes <- bootstrap <- list()
for (name in c(names(samples), "longer_window", "pretrend", "first_followup_year")) {
  dat <- if (name %in% c("longer_window", "first_followup_year")) {
    primary
  } else if (name == "pretrend") {
    samples$older_cohort
  } else {
    samples[[name]]
  }
  pre <- if (name == "pretrend") 2014L else 2016L
  post <- switch(name,
    pretrend = 2016L,
    longer_window = 2019:2021,
    first_followup_year = 2018L,
    2019L
  )
  change <- lazic_changes(dat, pre, post)
  absolute[[name]] <- lazic_absolute(change, name)
  x <- dat[dat$year %in% c(pre, post), ]
  x$paper_id <- x$article_id
  x$citation_year <- x$year
  x$flag <- x$flagged
  x$post <- as.integer(x$year %in% post)
  x$flag_post <- x$flag * x$post
  proportional[[name]] <- lal_ppml(x, name)
  changes[[name]] <- transform(change, specification = name)
  for (flag in 0:1) {
    group <- change[change$flag == flag, ]
    summaries[[length(summaries) + 1L]] <- data.frame(
      specification = name, flag = flag, papers = nrow(group),
      mean_before = mean(group$before), mean_after = mean(group$after),
      median_before = median(group$before), median_after = median(group$after),
      mean_change = mean(group$change), median_change = median(group$change),
      increased = sum(group$change > 0), declined = sum(group$change < 0)
    )
  }
  if (name == "primary") {
    boot <- lazic_bootstrap(change)
    bootstrap[[name]] <- data.frame(statistic = rownames(boot), boot, row.names = NULL)
  }
}
write.csv(do.call(rbind, absolute), "data/lazic/absolute_changes.csv", row.names = FALSE)
write.csv(do.call(rbind, proportional), "data/lazic/estimates.csv", row.names = FALSE)
write.csv(do.call(rbind, changes), "data/lazic/paper_changes.csv", row.names = FALSE)
write.csv(do.call(rbind, summaries), "data/lazic/summary.csv", row.names = FALSE)
write.csv(do.call(rbind, bootstrap), "data/lazic/bootstrap.csv", row.names = FALSE)

change <- changes$primary
change$split_unit <- articles$split_unit[match(change$paper_id, articles$article_id)]
strata <- split(change, change$split_unit)
weights <- vapply(strata, function(x) sum(x$flag == 1L), numeric(1))
weights <- weights / sum(weights)
contrast <- function(x) mean(x$change[x$flag == 1L]) - mean(x$change[x$flag == 0L])
estimate <- sum(weights * vapply(strata, contrast, numeric(1)))
set.seed(2017L)
draws <- replicate(5000L, {
  sum(weights * vapply(strata, function(x) {
    groups <- split(x, x$flag)
    samples <- lapply(groups, function(g) g[sample.int(nrow(g), nrow(g), replace = TRUE), ])
    contrast(do.call(rbind, samples))
  }, numeric(1)))
})
write.csv(data.frame(
  specification = "split_unit_standardized_to_flagged", estimate = estimate,
  lower = unname(quantile(draws, .025)), upper = unname(quantile(draws, .975)),
  bootstrap_repetitions = 5000L
), "data/lazic/stratified.csv", row.names = FALSE)

annual <- list()
for (name in c("primary", "older_cohort")) {
  x <- samples[[name]]
  x <- x[x$year >= if (name == "primary") 2016L else 2014L, ]
  for (group in split(x, list(x$flagged, x$year), drop = TRUE)) {
    annual[[length(annual) + 1L]] <- data.frame(
      sample = name, year = group$year[1], flag = group$flagged[1], papers = nrow(group),
      mean = mean(group$citations), median = median(group$citations)
    )
  }
}
write.csv(do.call(rbind, annual), "data/lazic/annual_summary.csv", row.names = FALSE)
print(absolute$primary)
print(proportional$primary)

annual <- do.call(rbind, annual)
plot_data <- rbind(
  transform(annual, value = mean, statistic = "Mean citations per paper"),
  transform(annual, value = median, statistic = "Median citations per paper")
)
plot_data$group <- ifelse(plot_data$flag == 1L, "Flagged", "Comparison")
plot_data$sample <- ifelse(plot_data$sample == "primary", "Primary sample", "Published by 2013")
library(ggplot2)
p <- ggplot(plot_data, aes(year, value, color = group, linetype = group)) +
  geom_vline(xintercept = c(2017, 2018), color = "grey70", linewidth = .4) +
  geom_line(linewidth = .7) +
  geom_point(size = 1.5) +
  facet_grid(sample ~ statistic, scales = "free_y") +
  scale_color_manual(values = c(Comparison = "#555555", Flagged = "#156082")) +
  scale_linetype_manual(values = c(Comparison = "dashed", Flagged = "solid")) +
  scale_x_continuous(breaks = c(2014, 2016, 2018, 2020, 2022, 2024)) +
  scale_y_continuous(limits = c(0, NA)) +
  labs(
    x = "Citing publication year", y = NULL, color = NULL, linetype = NULL,
    caption = paste(
      "Vertical lines: 2017 public release; 2018 journal publication.",
      "All indexed document types."
    )
  ) +
  theme_minimal(base_size = 11) +
  theme(
    panel.grid.minor = element_blank(), panel.grid.major.x = element_blank(),
    axis.text = element_text(color = "black"), legend.position = "top",
    strip.text = element_text(face = "bold"), plot.margin = margin(8, 12, 8, 8)
  )
for (extension in c("pdf", "png")) {
  ggsave(paste0("docs/lazic/citation_paths.", extension), p,
    width = 8.2, height = 5.4, dpi = 160
  )
}
