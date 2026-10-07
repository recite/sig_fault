hmx_panel <- function(directory) {
  panel <- read.csv(file.path(directory, "panel.csv"))
  papers <- read.csv(file.path(directory, "paper_assessments.csv"))
  stopifnot(
    !anyDuplicated(papers$paper_id), !anyDuplicated(panel[c("paper_id", "year")]),
    setequal(panel$paper_id, papers$paper_id), all(panel$status == "complete"),
    !anyNA(panel$citations), !anyNA(panel$all_types)
  )
  for (name in c("meta_eligible", "earlier_critique")) {
    stopifnot(all(papers[[name]] %in% c("True", "False")))
    papers[[name]] <- papers[[name]] == "True"
  }
  index <- match(panel$paper_id, papers$paper_id)
  stopifnot(identical(panel$journal, papers$journal[index]))
  for (name in setdiff(names(papers), c("paper_id", "journal"))) {
    panel[[name]] <- papers[[name]][index]
  }
  panel$article_id <- panel$paper_id
  panel$serious <- FALSE
  panel$cohort <- 2018L
  panel
}

hmx_sample <- function(panel, diagnostic = "severe_extrapolation", selection = "full",
                       outcome = "citations") {
  x <- panel[panel[[diagnostic]] != "unknown", ]
  x$flag <- as.integer(x[[diagnostic]] == "flagged")
  if (selection == "nonoverlap") x <- x[x$meta_eligible, ]
  if (selection == "no_earlier_critique") x <- x[!x$earlier_critique, ]
  if (selection == "journal_support") {
    groups <- tapply(x$flag, x$journal, function(z) length(unique(z)))
    x <- x[x$journal %in% names(groups)[groups == 2L], ]
  }
  stopifnot(selection %in% c("full", "nonoverlap", "no_earlier_critique", "journal_support"))
  x$citations <- x[[outcome]]
  x
}

hmx_bootstrap <- function(periods, draws = 9999L, seed = 20261007L) {
  set.seed(seed)
  groups <- split(seq_len(nrow(periods)), periods$flag)
  samples <- replicate(draws, {
    indices <- unlist(lapply(groups, function(i) sample(i, length(i), replace = TRUE)))
    x <- periods[indices, ]
    means <- aggregate(cbind(before, after, change) ~ flag, x, mean)
    c(
      absolute = diff(means$change),
      log_ratio = if (all(means$before > 0) && all(means$after > 0)) {
        diff(log(means$after / means$before))
      } else {
        NA_real_
      }
    )
  })
  stopifnot(all(is.finite(samples)))
  ci <- apply(samples, 1, quantile, c(.025, .975))
  data.frame(
    draws = draws, seed = seed, undefined = sum(!is.finite(samples["log_ratio", ])),
    absolute_lower = ci[1, "absolute"], absolute_upper = ci[2, "absolute"],
    se_log = sd(samples["log_ratio", ]),
    percent_lower = 100 * expm1(ci[1, "log_ratio"]),
    percent_upper = 100 * expm1(ci[2, "log_ratio"])
  )
}

hmx_analyze <- function(directory) {
  panel <- hmx_panel(directory)
  write <- function(x, name) write.csv(x, file.path(directory, name), row.names = FALSE, na = "")
  specs <- data.frame(
    specification = c(
      "primary", "nonoverlap", "longer_followup", "all_types", "prior_trend",
      "linearity", "low_high", "journal_support", "no_earlier_critique"
    ),
    pre = c(2017L, 2017L, 2017L, 2017L, 2015L, 2017L, 2017L, 2017L, 2017L),
    post_end = c(2019L, 2019L, 2021L, 2019L, 2017L, 2019L, 2019L, 2019L, 2019L),
    diagnostic = c(
      rep("severe_extrapolation", 5), "linearity_rejected", "low_high_not_rejected",
      rep("severe_extrapolation", 2)
    ),
    selection = c("full", "nonoverlap", rep("full", 5), "journal_support", "no_earlier_critique"),
    outcome = c(rep("citations", 3), "all_types", rep("citations", 5))
  )
  estimates <- absolute <- periods_all <- bootstraps <- list()
  identity_error <- numeric()
  for (i in seq_len(nrow(specs))) {
    s <- specs[i, ]
    x <- hmx_sample(panel, s$diagnostic, s$selection, s$outcome)
    post <- seq(s$pre + 2L, s$post_end)
    periods <- article_changes(x, pre = s$pre, post = post)
    model <- panel_model(x, s$specification,
      pre = s$pre, post = post,
      effects = if (s$selection == "journal_support") "journal" else "basic"
    )
    if (s$selection != "journal_support") {
      identity_error <- c(identity_error, abs(model$estimate - log_growth_ratio(periods)))
      bootstraps[[s$specification]] <- cbind(
        specification = s$specification, hmx_bootstrap(periods)
      )
    }
    estimates[[s$specification]] <- model
    absolute[[s$specification]] <- estimate_change(periods, s$specification)
    periods_all[[s$specification]] <- cbind(specification = s$specification, periods)
  }
  stopifnot(max(identity_error) < 1e-8)
  estimates <- do.call(rbind, estimates)
  write(specs, "specifications.csv")
  write(estimates, "estimates.csv")
  write(do.call(rbind, absolute), "absolute_estimates.csv")
  write(do.call(rbind, periods_all), "paper_periods.csv")
  write(do.call(rbind, bootstraps), "bootstrap.csv")
  main <- periods_all$primary
  levels <- do.call(rbind, lapply(split(main, main$flag), function(x) {
    data.frame(
      flag = x$flag[1], papers = nrow(x), before_mean = mean(x$before),
      after_mean = mean(x$after), before_median = median(x$before), after_median = median(x$after),
      change_mean = mean(x$change), change_median = median(x$change),
      before_total = sum(x$before), after_total = sum(x$after)
    )
  }))
  write(levels, "period_summary.csv")
  x <- hmx_sample(panel)
  write(annual_summary(x), "annual_summary.csv")
  write(
    as.data.frame(table(unique(x[c("article_id", "flag", "journal")])[c("journal", "flag")])),
    "journal_support.csv"
  )
  loo <- do.call(rbind, lapply(main$article_id, function(id) {
    reduced <- main[main$article_id != id, ]
    data.frame(
      omitted = id, log_ratio = log_growth_ratio(reduced),
      percent = 100 * expm1(log_growth_ratio(reduced)),
      absolute = mean(reduced$change[reduced$flag == 1L]) - mean(reduced$change[reduced$flag == 0L])
    )
  }))
  write(loo, "leave_one_out.csv")
  checks <- list(
    papers = nrow(main), flagged = sum(main$flag), comparison = sum(main$flag == 0L),
    complete = all(panel$status == "complete"), raw_fe_identity_error = max(identity_error),
    bootstrap_undefined = sum(vapply(bootstraps, function(z) z$undefined, numeric(1))),
    nonoverlap_papers = nrow(periods_all$nonoverlap),
    journal_supported_papers = nrow(periods_all$journal_support)
  )
  jsonlite::write_json(checks, file.path(directory, "analysis_checks.json"),
    pretty = TRUE, auto_unbox = TRUE
  )
  writeLines(
    trimws(capture.output(sessionInfo()), which = "right"), file.path(directory, "R-session.txt")
  )
  invisible(checks)
}

if (sys.nframe() == 0L) {
  source("R/analysis.R")
  args <- commandArgs(trailingOnly = TRUE)
  hmx_analyze(if (length(args)) args[1] else "data/cohorts/hmx/pipeline")
}
