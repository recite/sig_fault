source("R/lal.R")
library(ggplot2)
panel <- read.csv("data/lal/panel.csv", stringsAsFactors = FALSE)
stopifnot(length(unique(panel$paper_id)) == 67L)
diagnostics <- c("weak", "sensitive", "screen", "ar_loss")
labels <- c(
  weak = "Effective F below 10", sensitive = "Inferential sensitivity",
  screen = "Either diagnostic", ar_loss = "AR-only sensitivity"
)
estimates <- absolute <- summaries <- changes <- leave_one <- list()
index <- 0L
for (diagnostic in diagnostics) {
  x <- lal_subset(panel, diagnostic)
  main <- lal_ppml(x, "2023 to 2025")
  main$diagnostic <- diagnostic
  estimates[[length(estimates) + 1L]] <- main
  absolute[[diagnostic]] <- transform(lal_absolute(x, "2023 to 2025"), diagnostic = diagnostic)
  change <- lal_changes(x)
  changes[[diagnostic]] <- transform(change, diagnostic = diagnostic)
  for (flag in 0:1) {
    group <- change[change$flag == flag, ]
    index <- index + 1L
    summaries[[index]] <- data.frame(
      diagnostic = diagnostic, flag = flag, papers = nrow(group),
      mean_2023 = mean(group$before), mean_2025 = mean(group$after),
      median_2023 = median(group$before), median_2025 = median(group$after),
      mean_change = mean(group$change), median_change = median(group$change),
      declined = sum(group$change < 0), unchanged = sum(group$change == 0)
    )
  }
  variants <- list(
    baseline_2022 = list(pre = 2022L, post = 2025L),
    two_year_baseline = list(pre = 2022:2023, post = 2025L),
    preperiod_2022_2023 = list(pre = 2022L, post = 2023L),
    early_circulation = list(pre = 2020L, post = 2022:2023)
  )
  dat <- x[x$publication_year < 2022L, ]
  estimates[[length(estimates) + 1L]] <- transform(
    lal_ppml(dat, "2023_baseline_same_2022_eligible_cohort"),
    diagnostic = diagnostic
  )
  for (variant in names(variants)) {
    years <- variants[[variant]]
    dat <- lal_subset(panel, diagnostic, pre = years$pre, post = years$post)
    estimates[[length(estimates) + 1L]] <- transform(
      lal_ppml(dat, variant),
      diagnostic = diagnostic
    )
  }
  for (effect in c("journal", "cohort")) {
    estimates[[length(estimates) + 1L]] <- transform(
      lal_ppml(x, paste0(effect, "_by_year"), effects = effect),
      diagnostic = diagnostic
    )
  }
  estimates[[length(estimates) + 1L]] <- transform(
    lal_ppml(x, "all_document_types", outcome = "citations_all_types"),
    diagnostic = diagnostic
  )
  concerns <- c("iv_Alt2015", "iv_Carnegie2017", "iv_Hager2022")
  estimates[[length(estimates) + 1L]] <- transform(
    lal_ppml(x, "broad_document_types", outcome = "citations_broad"),
    diagnostic = diagnostic
  )
  estimates[[length(estimates) + 1L]] <- transform(
    lal_ppml(x, "broad_oxford_books_collapsed", outcome = "citations_broad_book_collapsed"),
    diagnostic = diagnostic
  )
  dat <- x[!x$paper_id %in% concerns, ]
  if (length(unique(dat$paper_id[dat$flag == 1])) >= 2L) {
    estimates[[length(estimates) + 1L]] <- transform(
      lal_ppml(dat, "exclude_audit_and_correction_concerns"),
      diagnostic = diagnostic
    )
  }
  for (paper in unique(x$paper_id[x$flag == 1])) {
    leave_one[[length(leave_one) + 1L]] <- transform(
      lal_ppml(x[x$paper_id != paper, ], "omit_one_flagged_paper"),
      diagnostic = diagnostic, omitted_paper = paper
    )
  }
}
estimates <- do.call(rbind, estimates)
absolute <- do.call(rbind, absolute)
summaries <- do.call(rbind, summaries)
changes <- do.call(rbind, changes)
leave_one <- do.call(rbind, leave_one)
write.csv(estimates, "data/lal/estimates.csv", row.names = FALSE)
write.csv(absolute, "data/lal/absolute_changes.csv", row.names = FALSE)
write.csv(summaries, "data/lal/summary.csv", row.names = FALSE)
write.csv(changes, "data/lal/paper_changes.csv", row.names = FALSE)
write.csv(leave_one, "data/lal/leave_one_out.csv", row.names = FALSE)

annual <- list()
for (cohort in c("Published by 2016", "Full cohort")) {
  for (diagnostic in diagnostics) {
    first <- if (cohort == "Full cohort") 2023L else 2017L
    dat <- panel[panel$publication_year < first & panel$citation_year >= first, ]
    if (diagnostic %in% c("sensitive", "ar_loss")) dat <- dat[dat$analytic_positive == 1L, ]
    dat$flag <- dat[[diagnostic]]
    groups <- split(dat, list(dat$flag, dat$citation_year), drop = TRUE)
    for (x in groups) {
      annual[[length(annual) + 1L]] <- data.frame(
        cohort = cohort, diagnostic = diagnostic, flag = x$flag[1],
        year = x$citation_year[1], papers = nrow(x),
        mean = mean(x$citations), median = median(x$citations)
      )
    }
  }
}
annual <- do.call(rbind, annual)
write.csv(annual, "data/lal/annual_summary.csv", row.names = FALSE)
theme <- theme_minimal(base_size = 11) + theme(
  panel.grid.minor = element_blank(), panel.grid.major.x = element_blank(),
  axis.text = element_text(color = "black"), legend.position = "top",
  strip.text = element_text(face = "bold"), plot.margin = margin(8, 12, 8, 8)
)
for (cohort in unique(annual$cohort)) {
  dat <- annual[annual$cohort == cohort & annual$diagnostic %in% c("weak", "sensitive"), ]
  plot_data <- rbind(
    transform(dat, value = mean, statistic = "Mean citations per paper"),
    transform(dat, value = median, statistic = "Median citations per paper")
  )
  plot_data$group <- ifelse(plot_data$flag == 1L, "Meets diagnostic", "Comparison")
  plot_data$diagnostic <- labels[plot_data$diagnostic]
  p <- ggplot(plot_data, aes(year, value, color = group, linetype = group)) +
    geom_vline(xintercept = 2024, color = "grey65", linewidth = .4) +
    geom_line(linewidth = .7) +
    geom_point(size = 1.7) +
    facet_grid(diagnostic ~ statistic, scales = "free_y") +
    scale_color_manual(values = c(Comparison = "#555555", `Meets diagnostic` = "#156082")) +
    scale_linetype_manual(values = c(Comparison = "dashed", `Meets diagnostic` = "solid")) +
    scale_x_continuous(breaks = sort(unique(dat$year))) +
    scale_y_continuous(limits = c(0, NA)) +
    labs(
      x = "Citing publication year", y = NULL, color = NULL, linetype = NULL,
      subtitle = cohort,
      caption = "Line: 2024 formal publication; earlier circulation began in 2021."
    ) +
    theme
  name <- if (cohort == "Full cohort") "citation_paths" else "longer_paths"
  for (extension in c("pdf", "png")) {
    ggsave(paste0("docs/lal/", name, ".", extension), p, width = 8.2, height = 5.4, dpi = 160)
  }
}
ar <- panel[panel$ar_loss == 1L & panel$citation_year >= 2017, ]
p <- ggplot(ar, aes(citation_year, citations, color = paper_id)) +
  geom_vline(xintercept = 2024, color = "grey65") +
  geom_line() +
  geom_point() +
  scale_x_continuous(breaks = 2017:2025) +
  labs(x = "Citing publication year", y = "Annual citations", color = NULL) +
  theme
ggsave("docs/lal/ar_individual_paths.png", p, width = 8.2, height = 3.5, dpi = 160)

lines <- c(
  "# Citation trajectories after the Lal et al. IV audit", "",
  "This analysis extends the Nieuwenhuis design to all 67 papers in the IV audit. It compares",
  "annual citations from articles and reviews to papers meeting specified adverse diagnostics",
  "with other assessed papers. Book chapters and preprints enter only the sensitivity analyses.",
  "[Design and timing](design.md) were recorded before estimating the expanded cohort.", "",
  "## Main comparison: 2023 to 2025", "",
  "Means and medians describe citations per paper per year. The 2024 transition year is omitted",
  "from the model. The inferential-sensitivity comparison includes only papers with at least one",
  "analytically significant estimate; the weak-F comparison includes all assessed papers.", "",
  "| Diagnostic | Group | Papers | Mean 2023 | Mean 2025 | Median 2023 | Median 2025 |",
  "| --- | --- | ---: | ---: | ---: | ---: | ---: |"
)
for (i in seq_len(nrow(summaries))) {
  x <- summaries[i, ]
  lines <- c(lines, sprintf(
    "| %s | %s | %d | %.1f | %.1f | %.1f | %.1f |",
    labels[x$diagnostic], ifelse(x$flag == 1, "Meets diagnostic", "Comparison"),
    x$papers, x$mean_2023, x$mean_2025, x$median_2023, x$median_2025
  ))
}
lines <- c(
  lines, "", "![Mean and median citation paths](citation_paths.png)", "",
  "## Relative and absolute changes", "",
  "The PPML percentage compares post/pre citation ratios using article and calendar-year fixed",
  "effects. Its intervals use article-clustered covariance and t(G-1) critical values. Absolute",
  "changes compare equal-paper mean changes with HC3 uncertainty.", "",
  "| Diagnostic | Relative change, % (95% CI) | Absolute difference in changes (95% CI) |",
  "| --- | ---: | ---: |"
)
for (diagnostic in diagnostics) {
  x <- estimates[estimates$diagnostic == diagnostic & estimates$specification == "2023 to 2025", ]
  a <- absolute[absolute$diagnostic == diagnostic, ]
  lines <- c(lines, sprintf(
    "| %s | %.1f [%.1f, %.1f] | %.1f [%.1f, %.1f] |",
    labels[diagnostic], x$percent, x$lower, x$upper, a$estimate, a$lower, a$upper
  ))
}
lines <- c(
  lines, "", "## Baseline sensitivity", "",
  "All entries are relative changes (%). The same-cohort column holds fixed the papers eligible",
  "for a 2022 baseline. Baseline choice changes the sign of the broader sensitivity contrast.", "",
  "| Diagnostic | 2023 baseline | 2022 baseline | 2023, same cohort as 2022 |",
  "| --- | ---: | ---: | ---: |"
)
for (diagnostic in diagnostics) {
  sub <- estimates[estimates$diagnostic == diagnostic, ]
  specs <- c("2023 to 2025", "baseline_2022", "2023_baseline_same_2022_eligible_cohort")
  values <- sub$percent[match(specs, sub$specification)]
  lines <- c(lines, sprintf(
    "| %s | %.1f | %.1f | %.1f |",
    labels[diagnostic], values[1], values[2], values[3]
  ))
}
ar_changes <- changes[changes$diagnostic == "ar_loss" & changes$flag == 1L, ]
lines <- c(
  lines, "", "## Interpretation and checks", "",
  "The [interpretation](interpretation.md) discusses what the observed paths imply.",
  "These are citation associations around formal publication, not identified effects of first",
  "learning about an error: the critique circulated from 2021, and the diagnostics do not prove",
  "that substantive findings are false. The broader audit also questions practices shared by",
  "papers in both groups. Only one complete calendar year follows 2024 publication.", "",
  sprintf(
    "The three AR-loss papers' total journal citations change from %d to %d.",
    sum(ar_changes$before), sum(ar_changes$after)
  ),
  "Their model intervals are exploratory and especially fragile with so few flagged papers.",
  "[Their individual paths](ar_individual_paths.png) and",
  "[leave-one-out estimates](../../data/lal/leave_one_out.csv) expose that dependence.", "",
  "[Longer paths for a fixed older cohort](longer_paths.png) show pre-publication evolution.",
  "[All specifications](../../data/lal/estimates.csv) include alternative baselines, pre-period",
  "and early-circulation comparisons, journal/cohort adjustments, document types, and exclusions",
  "for audit or correction concerns. The design log records changes and their reasons.", "",
  "## Reproduce", "", "```sh", "make lal", "make lal-test", "```", "",
  "The frozen frame runs offline using the repository's R environment and Python standard library.",
  "`make lal-fetch` retrieves citation histories; changed live results cannot",
  "overwrite the frozen frame. The data dictionary is in [data.md](data.md).", "",
  "Source: [Lal et al.](https://doi.org/10.1017/pan.2024.2),",
  "[replication archive](https://doi.org/10.7910/DVN/MM5THZ)."
)
writeLines(lines, "docs/lal/README.md")
print(estimates[estimates$specification == "2023 to 2025", ])
