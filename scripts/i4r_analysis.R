source("R/i4r.R")
args <- commandArgs(trailingOnly = TRUE)
if (!length(args) %in% c(0L, 2L)) stop("Supply both data directory and report path")
aggregate <- length(args) == 2L
data_dir <- if (aggregate) args[1] else "data/i4r"
input <- file.path(data_dir, "analysis_panel.csv")
panel <- read.csv(input, stringsAsFactors = FALSE)
output <- if (aggregate) args[2] else "docs/i4r/results.md"
dir.create(dirname(output), recursive = TRUE, showWarnings = FALSE)
if (!nrow(panel)) {
  unlink(file.path(data_dir, c("estimates.csv", "descriptive.csv", "sensitivity_estimates.csv")))
  writeLines(c(
    "# Citation analysis status", "",
    paste(
      "No primary treatment-effect estimate is available. The current build has no",
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
      "[coverage](coverage.md) and [design](design.md).",
      "The separately matched [annual-total analysis](aggregate-results.md)",
      "uses a broader secondary outcome and does not complete this primary analysis."
    )
  ), output)
} else {
  estimates <- do.call(rbind, lapply(split(panel, panel$horizon), i4r_estimate))
  write.csv(estimates, file.path(data_dir, "estimates.csv"), row.names = FALSE)
  groups <- split(panel, interaction(panel$horizon, panel$treated, panel$event_time, drop = TRUE))
  descriptive <- do.call(rbind, lapply(groups, function(g) {
    median <- i4r_weighted_median(g$citations, g$weight)
    data.frame(
      horizon = g$horizon[1], treated = g$treated[1], event_time = g$event_time[1],
      mean = stats::weighted.mean(g$citations, g$weight), median = median,
      distinct_articles = length(unique(g$article_id)), weight = sum(g$weight)
    )
  }))
  write.csv(descriptive, file.path(data_dir, "descriptive.csv"), row.names = FALSE)
  sensitivities <- read.csv(file.path(data_dir, "sensitivity_panel.csv"), stringsAsFactors = FALSE)
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
  unlink(file.path(data_dir, "sensitivity_estimates.csv"))
  if (length(sensitivity_results)) {
    write.csv(
      do.call(rbind, sensitivity_results),
      file.path(data_dir, "sensitivity_estimates.csv"),
      row.names = FALSE
    )
  }
  lines <- c(
    if (aggregate) {
      "# Secondary citation contrasts from annual totals"
    } else {
      "# Citation changes after public error disclosure"
    }, "",
    paste(
      "Estimates apply to the dated, matched, observed subset; they are not",
      "estimates for every I4R article."
    ),
    "",
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
  if (aggregate) {
    horizon_lines <- lines[5:length(lines)]
    lines <- lines[1:4]
    titles <- read.csv("data/i4r/articles.csv", stringsAsFactors = FALSE)
    cases <- do.call(rbind, lapply(split(panel, panel$stack_id), function(s) {
      treated <- s[s$treated == 1, ]
      controls <- s[s$treated == 0, ]
      before <- controls[controls$post == 0, ]
      after <- controls[controls$post == 1, ]
      aid <- treated$article_id[1]
      data.frame(
        event_id = s$event_id[1], article_id = aid,
        title = titles$title[match(aid, titles$article_id)], horizon = s$horizon[1],
        baseline_year = treated$year[treated$post == 0],
        post_year = treated$year[treated$post == 1],
        treated_before = treated$citations[treated$post == 0],
        treated_after = treated$citations[treated$post == 1],
        control_before = stats::weighted.mean(before$citations, before$weight),
        control_after = stats::weighted.mean(after$citations, after$weight),
        matched_change = i4r_direct(s), controls = nrow(before)
      )
    }))
    write.csv(cases, file.path(data_dir, "case_contrasts.csv"), row.names = FALSE)
    first <- cases[cases$horizon == 1, ]
    headline <- estimates[estimates$horizon == 1, ]
    sensitivity <- do.call(rbind, sensitivity_results)
    pre <- sensitivity$estimate[sensitivity$specification == "placebo_pre2_pre1"]
    omit <- sensitivity$estimate[sensitivity$specification == "omit_disclosure_dp_292"]
    summary_value <- function(treated, event_time, statistic) {
      selected <- descriptive$horizon == 1 & descriptive$treated == treated &
        descriptive$event_time == event_time
      descriptive[selected, statistic]
    }
    macros <- list(
      IfrCases = nrow(first), IfrIncreased = sum(first$treated_after > first$treated_before),
      IfrMeanBefore = summary_value(1, -1, "mean"),
      IfrMeanAfter = summary_value(1, 1, "mean"),
      IfrMedianBefore = summary_value(1, -1, "median"),
      IfrMedianAfter = summary_value(1, 1, "median"),
      IfrControlMeanBefore = summary_value(0, -1, "mean"),
      IfrControlMeanAfter = summary_value(0, 1, "mean"),
      IfrControlMedianBefore = summary_value(0, -1, "median"),
      IfrControlMedianAfter = summary_value(0, 1, "median"),
      IfrChange = headline$estimate, IfrLower = headline$lower, IfrUpper = headline$upper,
      IfrPreChange = pre, IfrOmitInventors = omit,
      IfrMinimum = min(first$matched_change), IfrMaximum = max(first$matched_change)
    )
    macros <- lapply(macros, function(x) format(round(x, 1), trim = TRUE, scientific = FALSE))
    dir.create("tabs", showWarnings = FALSE)
    writeLines(
      paste0("\\newcommand{\\", names(macros), "}{", macros, "}"),
      "tabs/i4r_aggregate_macros.tex"
    )
    jsonlite::write_json(macros, "tabs/i4r_aggregate_macros.json", auto_unbox = TRUE, pretty = TRUE)
    labels <- c(
      dp_021_disclosure = "Parental leave", dp_148_disclosure = "Fast internet",
      dp_292_disclosure = "Inventor clusters", dp_294_disclosure = "Electrification"
    )
    stopifnot(all(first$event_id %in% names(labels)))
    rows <- vapply(seq_len(nrow(first)), function(i) {
      r <- first[i, ]
      sprintf(
        "%s & %s--%s & %.0f $\\to$ %.0f & %.1f $\\to$ %.1f & %+.1f \\\\",
        labels[r$event_id], r$baseline_year, r$post_year,
        r$treated_before, r$treated_after, r$control_before, r$control_after, r$matched_change
      )
    }, character(1))
    writeLines(c(
      "\\begin{tabular}{llrrr}", "\\toprule",
      "Paper & Years & Affected & Controls & Contrast \\\\", "\\midrule", rows,
      "\\bottomrule", "\\end{tabular}"
    ), "tabs/i4r_aggregate_cases.tex")
    trajectories <- read.csv(file.path(data_dir, "event_trajectories.csv"))
    selected <- trajectories$event_id %in% first$event_id &
      trajectories$event_time %in% -2:1
    trajectories <- trajectories[selected, ]
    stopifnot(all(trajectories$status == "complete"), !anyNA(trajectories$citations))
    paths <- do.call(rbind, lapply(
      split(trajectories, interaction(
        trajectories$event_id, trajectories$treated, trajectories$event_time,
        drop = TRUE
      )),
      function(g) {
        data.frame(
          event_id = g$event_id[1], treated = g$treated[1],
          event_time = g$event_time[1], citations = weighted.mean(g$citations, g$weight)
        )
      }
    ))
    paths$case <- factor(labels[paths$event_id], levels = unname(labels))
    paths$group <- ifelse(paths$treated == 1, "Affected", "Controls")
    write.csv(paths, file.path(data_dir, "figure_paths.csv"), row.names = FALSE)
    library(ggplot2)
    p <- ggplot(paths, aes(event_time, citations, color = group, linetype = group)) +
      geom_vline(xintercept = 0, color = "grey55", linewidth = .4) +
      geom_line(linewidth = .7) +
      geom_point(size = 1.8) +
      facet_wrap(~case, ncol = 2) +
      scale_color_manual(values = c(Affected = "#156082", Controls = "#555555")) +
      scale_linetype_manual(values = c(Affected = "solid", Controls = "dashed")) +
      scale_x_continuous(breaks = -2:1, labels = c("-2", "-1", "0", "+1")) +
      scale_y_continuous(limits = c(0, NA)) +
      labs(
        x = "Year relative to first public disclosure", y = "Annual citing works (all types)",
        color = NULL, linetype = NULL
      ) +
      theme_minimal(base_size = 11) +
      theme(
        panel.grid.minor = element_blank(), panel.grid.major.x = element_blank(),
        axis.title = element_text(color = "black"), axis.text = element_text(color = "black"),
        strip.text = element_text(hjust = 0, face = "bold"), legend.position = "top",
        plot.margin = margin(8, 18, 8, 8)
      )
    dir.create("figs", showWarnings = FALSE)
    ggsave("figs/i4r_aggregate_paths.pdf", p, width = 6.5, height = 4.1, device = cairo_pdf)
    lines <- c(
      lines, "", sprintf(
        paste(
          "Citations increased for %s of %s affected papers. Their mean rose from %.2f to %.2f",
          "and median from %.1f to %.1f; controls' mean rose from %.2f to %.2f",
          "and weighted median from %.1f to %.1f."
        ),
        macros$IfrIncreased, macros$IfrCases,
        summary_value(1, -1, "mean"), summary_value(1, 1, "mean"),
        summary_value(1, -1, "median"), summary_value(1, 1, "median"),
        summary_value(0, -1, "mean"), summary_value(0, 1, "mean"),
        summary_value(0, -1, "median"), summary_value(0, 1, "median")
      ), "", sprintf(
        paste(
          "The average first-year contrast is %+.2f citations. Omitting the inventor-clusters",
          "paper changes it to %+.2f. The preceding year already shows a matched growth",
          "difference of %+.2f citations. Continued citation is visible, but these mixed",
          "cases do not identify a stable causal response to disclosure."
        ), headline$estimate, omit, pre
      ), "",
      paste(
        "Longer horizons contain only the older disclosures. Compare them with the +1",
        "estimates for the same cohort in `sensitivity_estimates.csv`, not with the full",
        "first-year sample. The all-type absolute contrasts are kept separate from the",
        "proportional cross-audit synthesis."
      )
    )

    lines <- c(
      lines, "",
      paste(
        "This retrospective secondary analysis uses precomputed annual totals",
        "across citing document types and newly selected matches based on those",
        "same pre-period totals. It is not the primary article/review-link analysis.",
        "See [design](aggregate-design.md)."
      ), "",
      "## Individual first-year contrasts", "",
      "| Original article | Treated, before → after | Controls, before → after | Matched change |",
      "| --- | ---: | ---: | ---: |"
    )
    for (i in which(cases$horizon == 1)) {
      r <- cases[i, ]
      lines <- c(lines, sprintf(
        "| %s | %.0f → %.0f | %.1f → %.1f | %.2f |",
        r$title, r$treated_before, r$treated_after,
        r$control_before, r$control_after, r$matched_change
      ))
    }
    lines <- c(lines, "", paste(
      "Each row compares the full calendar year before disclosure with the full",
      "year afterward. Controls receive equal weight within a matched set.",
      "The pooled contrast gives each affected article equal weight.",
      "Few disclosures make clustered intervals exploratory and unstable;",
      "case contrasts and leave-one-disclosure-out results should guide interpretation."
    ))
  }
  if (aggregate) lines <- c(lines, "", "## Horizon summaries", "", horizon_lines)
  writeLines(c(lines, "", paste(
    if (aggregate) {
      "Units are additional indexed citing works of all types per affected article."
    } else {
      "Units are additional citing journal articles/reviews per affected article."
    },
    "Intervals use article and disclosure-event clusters, conditional on matches;",
    "few events make inference fragile. Causal interpretation requires parallel",
    "counterfactual citation trends. Counts do not establish reliance on the error."
  )), output)
}
