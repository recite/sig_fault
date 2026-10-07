source("R/journal_cohort.R")
panel <- read.csv("data/nieuwenhuis/paired_panel.csv", stringsAsFactors = FALSE)
stopifnot(all(panel$status == "complete"), !anyNA(panel), length(unique(panel$article_id)) == 153L)
output <- "data/nieuwenhuis/design"
write_result <- function(x, name) write.csv(x, file.path(output, name), row.names = FALSE)
results <- annual <- paths <- list()
for (source in c("wos", "openalex")) {
  x <- transform(panel, citations = panel[[source]])
  support <- journal_cohort_support(x)
  stopifnot(all(support$strata$supported))
  if (source == "wos") {
    write_result(support$strata, "support.csv")
    write_result(support$papers, "weights.csv")
  }
  paths[[source]] <- transform(journal_cohort_paths(x), source = source)
  for (sample in c("all", "published_2009")) {
    d <- if (sample == "all") x else x[x$cohort == 2009L, ]
    for (window in c("longer_followup", "first_followup")) {
      post <- if (window == "longer_followup") 2012:2015 else 2012L
      for (poisson in c(TRUE, FALSE)) {
        results[[length(results) + 1L]] <- transform(
          journal_cohort_fit(d, post = post, poisson = poisson),
          source = source, sample = sample, window = window
        )
      }
    }
    for (year in 2011:2015) {
      annual[[length(annual) + 1L]] <- transform(
        journal_cohort_fit(d, post = year),
        source = source, sample = sample, year = year
      )
    }
  }
  results[[length(results) + 1L]] <- transform(
    journal_cohort_fit(x[x$cohort == 2009L, ], pre = 2009L, post = 2010L),
    source = source, sample = "published_2009", window = "publication_year_diagnostic"
  )
}
results <- do.call(rbind, results)
annual <- do.call(rbind, annual)
paths <- do.call(rbind, paths)
write_result(results, "estimates.csv")
write_result(annual, "annual_estimates.csv")
write_result(paths, "annual_paths.csv")

primary <- results[results$sample == "all" & results$window == "longer_followup", ]
format_value <- function(x) {
  unname(formatC(ifelse(abs(x) < .05, 0, x), digits = 1, format = "f"))
}
macros <- list()
for (source in c("wos", "openalex")) {
  prefix <- if (source == "wos") "JcWos" else "JcOa"
  p <- primary[primary$source == source & primary$model == "PPML", ]
  a <- primary[primary$source == source & primary$model == "OLS", ]
  values <- list(
    Percent = p$percent, Lower = p$percent_lower, Upper = p$percent_upper,
    Absolute = a$estimate, AbsoluteLower = a$lower, AbsoluteUpper = a$upper
  )
  for (name in names(values)) macros[[paste0(prefix, name)]] <- format_value(values[[name]])
}
jsonlite::write_json(macros, "tabs/journal_cohort_macros.json", auto_unbox = TRUE, pretty = TRUE)
writeLines(
  paste0("\\newcommand{\\", names(macros), "}{", unlist(macros), "}"),
  "tabs/journal_cohort_macros.tex"
)


table <- c(
  "\\begin{tabular}{lllrr}", "\\toprule",
  "Source & Publication years & Scale & Estimate & 95\\% interval \\\\", "\\midrule"
)
for (i in which(results$window == "longer_followup")) {
  r <- results[i, ]
  proportional <- r$model == "PPML"
  table <- c(table, paste0(
    if (r$source == "wos") "Web of Science" else "OpenAlex", " & ",
    if (r$sample == "all") "2009--2010" else "2009", " & ",
    if (proportional) "Percent" else "Citations", " & ",
    format_value(if (proportional) r$percent else r$estimate), " & [",
    format_value(if (proportional) r$percent_lower else r$lower), ", ",
    format_value(if (proportional) r$percent_upper else r$upper), "] \\\\"
  ))
}
writeLines(c(table, "\\bottomrule", "\\end{tabular}"), "tabs/journal_cohort_estimates.tex")

library(ggplot2)
d <- paths[paths$source == "wos", ]
d <- rbind(
  transform(d, value = mean, statistic = "Mean citations per paper"),
  transform(d, value = median, statistic = "Median citations per paper")
)
d$statistic <- factor(d$statistic,
  levels = c("Median citations per paper", "Mean citations per paper")
)
d$group <- ifelse(d$flag == 1L, "Flagged", "Comparison")
p <- ggplot(d, aes(year, value, color = group, linetype = group)) +
  geom_vline(xintercept = 2011.65, color = "grey55", linewidth = .4) +
  geom_line(linewidth = .7) +
  geom_point(size = 1.8) +
  facet_wrap(~statistic, nrow = 1) +
  scale_color_manual(values = c(Comparison = "#555555", Flagged = "#156082")) +
  scale_linetype_manual(values = c(Comparison = "dashed", Flagged = "solid")) +
  scale_x_continuous(breaks = 2009:2015) +
  scale_y_continuous(limits = c(0, NA)) +
  labs(x = "Citing publication year", y = NULL, color = NULL, linetype = NULL) +
  theme_minimal(base_size = 11) +
  theme(
    panel.grid.minor = element_blank(), panel.grid.major.x = element_blank(),
    axis.text = element_text(color = "black"), legend.position = "top",
    plot.margin = margin(8, 18, 8, 8)
  )
ggsave("figs/journal_cohort_paths.pdf", p, width = 6.5, height = 3.1, device = cairo_pdf)

lines <- c(
  "# Citation comparisons within journal and publication year", "",
  "All 153 original papers have comparison support within their journal and publication year.",
  "The ten groups contain 76 flagged and 77 comparison papers. No papers are dropped for lack",
  "of group support. The smallest group has three flagged papers and one comparison paper.", "",
  "Article fixed effects absorb baseline citation levels. Journal/publication-year groups",
  "have separate calendar-year effects, allowing different aging and journal citation paths.",
  "The comparison asks whether flagged papers' citations change differently within these groups.",
  "",
  "| Source | Sample | Window | Model | Estimate | 95% interval | Flagged / comparison |",
  "| --- | --- | --- | --- | ---: | ---: | ---: |"
)
for (i in seq_len(nrow(results))) {
  r <- results[i, ]
  proportional <- r$model == "PPML"
  b <- if (proportional) r$percent else r$estimate
  lo <- if (proportional) r$percent_lower else r$lower
  hi <- if (proportional) r$percent_upper else r$upper
  lines <- c(lines, sprintf(
    "| %s | %s | %s | %s | %.1f%s | [%.1f, %.1f]%s | %d / %d |",
    r$source, r$sample, r$window, r$model, b, if (proportional) "%" else "",
    lo, hi, if (proportional) "%" else "", r$n_flagged, r$n_comparison
  ))
}
lines <- c(
  lines, "",
  "The baseline is 2010; longer follow-up is 2012–2015, and first follow-up is 2012.",
  "The publication-year diagnostic compares 2009 with 2010 for 2009 originals only.",
  "Its baseline is a partial publication year. OLS estimates are citations per paper per year;",
  "PPML estimates are percentage changes in relative citation growth. Intervals cluster by",
  "article, with the recorded finite-sample adjustment and t(G−1) reference.", "",
  "The proportional and additive models impose common within-group effects. Causal interpretation",
  "requires comparable absent-publicity growth within the journal/publication-year groups,",
  "on the corresponding scale. Shared citing papers and publicity shocks can create dependence",
  "across originals not represented by article clustering.", "",
  "[Standardized trajectories](../../../figs/journal_cohort_paths.pdf) use the flagged papers'",
  "journal/publication-year composition for both groups. The comparison weights depend only on",
  "group membership, not citations. Medians describe the reweighted article distribution; they",
  "are not averages of group medians. These descriptive weights differ from the regression's",
  "implicit weighting, so the plotted growth ratio need not equal the PPML coefficient.", "",
  "The raw trajectories remain Figure 1 in the manuscript. Full support, weights, annual paths,",
  "pointwise annual estimates and model exclusions are saved beside this report.", "",
  "[Design and assumptions](../../../docs/nieuwenhuis/journal-cohort-design.md)."
)
writeLines(lines, file.path(output, "README.md"))
status <- list(
  strata = nrow(support$strata), supported = all(support$strata$supported),
  papers = nrow(support$papers), specifications = nrow(results), annual_estimates = nrow(annual),
  sources = c("wos", "openalex"), identical_source_population = TRUE,
  estimand = "Common within-journal/publication-year proportional or additive contrast",
  inference = "Article-clustered; nonnested FE adjustment; t(G-1)",
  original_synthesis_unchanged = TRUE
)
jsonlite::write_json(status, file.path(output, "status.json"), auto_unbox = TRUE, pretty = TRUE)
