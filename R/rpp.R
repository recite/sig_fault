rpp_contrast <- function(d, weights) {
  pieces <- lapply(names(weights), function(j) {
    a <- d[d$journal == j & d$role == "unsuccessful", ]
    b <- d[d$journal == j & d$role == "successful", ]
    stopifnot(nrow(a) > 1, nrow(b) > 1)
    va <- var(a$post - a$pre) / nrow(a)
    vb <- var(b$post - b$pre) / nrow(b)
    data.frame(
      journal = j, weight = weights[[j]],
      estimate = mean(a$post - a$pre) - mean(b$post - b$pre),
      va = va, vb = vb, na = nrow(a), nb = nrow(b),
      log_ratio = if (all(c(mean(a$pre), mean(a$post), mean(b$pre), mean(b$post)) > 0)) {
        log(mean(a$post) / mean(a$pre)) - log(mean(b$post) / mean(b$pre))
      } else {
        NA_real_
      }
    )
  })
  pieces <- do.call(rbind, pieces)
  variance <- sum(pieces$weight^2 * (pieces$va + pieces$vb))
  df_terms <- pieces$va^2 / (pieces$na - 1) + pieces$vb^2 / (pieces$nb - 1)
  df <- variance^2 / sum(pieces$weight^4 * df_terms)
  estimate <- sum(pieces$weight * pieces$estimate)
  list(
    estimate = estimate, se = sqrt(variance), df = df,
    lower = estimate - qt(.975, df) * sqrt(variance),
    upper = estimate + qt(.975, df) * sqrt(variance),
    log_ratio = sum(pieces$weight * pieces$log_ratio), pieces = pieces
  )
}

rpp_periods <- function(panel, pre, post, outcome = "citations") {
  ids <- unique(panel$paper_id)
  do.call(rbind, lapply(ids, function(id) {
    x <- panel[panel$paper_id == id, ]
    before <- x[x$year %in% pre, outcome]
    after <- x[x$year %in% post, outcome]
    stopifnot(length(before) == length(pre), length(after) == length(post))
    data.frame(
      paper_id = id, journal = x$journal[1], role = x$role[1],
      pre = mean(before), post = mean(after)
    )
  }))
}

rpp_bootstrap <- function(d, weights, draws = 9999L, seed = 20261007L) {
  set.seed(seed)
  estimates <- rep(0, draws)
  for (journal in names(weights)) {
    for (role in c("unsuccessful", "successful")) {
      x <- d[d$journal == journal & d$role == role, ]
      indices <- matrix(sample.int(nrow(x), nrow(x) * draws, replace = TRUE), nrow(x))
      before <- colMeans(matrix(x$pre[indices], nrow(x)))
      after <- colMeans(matrix(x$post[indices], nrow(x)))
      sign <- if (role == "unsuccessful") 1 else -1
      estimates <- estimates + weights[[journal]] * sign * log(after / before)
    }
  }
  invalid <- sum(!is.finite(estimates))
  list(
    draws = draws, undefined = invalid,
    lower = if (invalid == 0) 100 * expm1(quantile(estimates, .025)) else NA_real_,
    upper = if (invalid == 0) 100 * expm1(quantile(estimates, .975)) else NA_real_,
    se_log = if (invalid == 0) sd(estimates) else NA_real_
  )
}

rpp_main <- function(path) {
  panel <- read.csv(file.path(path, "panel.csv"), stringsAsFactors = FALSE)
  identities <- read.csv(file.path(path, "identities.csv"), stringsAsFactors = FALSE)
  coverage <- read.csv(file.path(path, "citation_coverage.csv"), stringsAsFactors = FALSE)
  matches <- read.csv(file.path(path, "matches.csv"), stringsAsFactors = FALSE)
  synthetic <- read.csv(file.path(path, "synthetic_weights.csv"), stringsAsFactors = FALSE)
  targets <- panel[panel$role != "external_control", ]
  stopifnot(
    length(unique(targets$paper_id)) == 98, all(targets$status == "complete"),
    !anyNA(targets$citations), !anyDuplicated(targets[c("paper_id", "year")]),
    all(targets$citations >= 0), all(identities$paper_id %in% matches$paper_id)
  )
  weights <- table(identities$journal) / nrow(identities)
  write <- function(x, name) write.csv(x, file.path(path, name), row.names = FALSE, na = "")
  outputs <- list()
  specifications <- list(
    primary = list(pre = 2012:2014, post = 2016:2018, outcome = "citations"),
    longer_followup = list(pre = 2012:2014, post = 2016:2025, outcome = "citations"),
    all_document_types = list(pre = 2012:2014, post = 2016:2018, outcome = "all_types"),
    pre_period_placebo = list(pre = 2010:2011, post = 2012:2014, outcome = "citations")
  )
  primary <- rpp_periods(targets, 2012:2014, 2016:2018)
  write(primary, "paper_periods.csv")
  levels <- do.call(rbind, lapply(split(primary, primary$role), function(x) {
    data.frame(
      role = x$role[1], papers = nrow(x), pre_mean = mean(x$pre), post_mean = mean(x$post),
      pre_median = median(x$pre), post_median = median(x$post)
    )
  }))
  write(levels, "period_summary.csv")
  for (name in names(specifications)) {
    s <- specifications[[name]]
    d <- rpp_periods(targets, s$pre, s$post, s$outcome)
    fit <- rpp_contrast(d, weights)
    boot <- rpp_bootstrap(d, weights)
    outputs[[name]] <- data.frame(
      specification = name, unsuccessful = sum(d$role == "unsuccessful"),
      successful = sum(d$role == "successful"), estimate_citations = fit$estimate,
      se = fit$se, df = fit$df, lower_citations = fit$lower, upper_citations = fit$upper,
      log_relative_growth = fit$log_ratio, se_log_bootstrap = boot$se_log,
      percent = 100 * expm1(fit$log_ratio), lower_percent = boot$lower,
      upper_percent = boot$upper, bootstrap_draws = boot$draws,
      undefined_draws = boot$undefined
    )
    if (name == "primary") write(fit$pieces, "journal_contrasts.csv")
  }
  estimates <- do.call(rbind, outputs)
  write(estimates, "estimates.csv")
  influence <- do.call(rbind, lapply(primary$paper_id, function(id) {
    fit <- rpp_contrast(primary[primary$paper_id != id, ], weights)
    data.frame(
      omitted = id, estimate_citations = fit$estimate, percent = 100 * expm1(fit$log_ratio)
    )
  }))
  write(influence, "leave_one_out.csv")
  ssc <- fixest::ssc(
    K.adj = TRUE, K.fixef = "nonnested", G.adj = TRUE, G.df = "min", t.df = "min"
  )
  d <- targets[targets$year %in% c(2012:2014, 2016:2018), ]
  d$failed_post <- as.integer(d$role == "unsuccessful" & d$year >= 2016)
  fits <- list(
    article_year = fixest::feols(citations ~ failed_post | paper_id + year,
      d,
      vcov = ~paper_id, ssc = ssc, fixef.rm = "none"
    ),
    article_journal_year = fixest::feols(citations ~ failed_post | paper_id + journal^year,
      d,
      vcov = ~paper_id, ssc = ssc, fixef.rm = "none"
    )
  )
  change <- primary$post - primary$pre
  raw <- mean(change[primary$role == "unsuccessful"]) -
    mean(change[primary$role == "successful"])
  stopifnot(abs(coef(fits$article_year)[[1]] - raw) < 1e-8)
  model_rows <- function(fit, name, term = names(coef(fit))[1]) {
    ci <- confint(fit)[term, ]
    data.frame(
      specification = name, term = term, estimate = coef(fit)[[term]],
      se = sqrt(vcov(fit)[term, term]), lower = unname(ci[1]), upper = unname(ci[2]),
      observations = nobs(fit)
    )
  }
  fixed <- do.call(rbind, lapply(names(fits), function(name) model_rows(fits[[name]], name)))
  write(fixed, "fixed_effects.csv")
  event <- targets[targets$year >= 2010 & targets$year != 2015, ]
  event$failed <- as.integer(event$role == "unsuccessful")
  fit <- fixest::feols(citations ~ i(year, failed, ref = 2014) | paper_id + journal^year,
    event,
    vcov = ~paper_id, ssc = ssc, fixef.rm = "none"
  )
  event_rows <- do.call(rbind, lapply(names(coef(fit)), function(term) {
    model_rows(fit, "article_journal_year", term)
  }))
  event_rows$year <- as.integer(sub("year::([0-9]+):failed", "\\1", event_rows$term))
  write(event_rows, "event_study.csv")
  annual_groups <- split(targets, interaction(targets$role, targets$year))
  annual <- do.call(rbind, lapply(annual_groups, function(x) {
    by_j <- tapply(x$citations, x$journal, mean)
    data.frame(
      role = x$role[1], year = x$year[1], papers = nrow(x), mean = mean(x$citations),
      median = median(x$citations), journal_standardized_mean = sum(weights[names(by_j)] * by_j)
    )
  }))
  write(annual, "annual_summary.csv")
  get_path <- function(id, years) {
    x <- panel[panel$paper_id == id, ]
    result <- x$citations[match(years, x$year)]
    stopifnot(!anyNA(result))
    result
  }
  external <- external_annual <- list()
  for (role in c("unsuccessful", "successful")) {
    ids <- identities$paper_id[identities$classification == role]
    for (method in c("nearest", "synthetic")) {
      links <- if (method == "nearest") matches else synthetic
      changes <- lapply(ids, function(id) {
        rows <- links[links$paper_id == id, ]
        stopifnot(abs(sum(rows$weight) - 1) < 1e-8)
        years <- 2010:2025
        y <- get_path(id, years)
        donor_paths <- vapply(rows$control_id, get_path, numeric(length(years)), years = years)
        control <- drop(donor_paths %*% rows$weight)
        external_annual[[length(external_annual) + 1L]] <<- data.frame(
          paper_id = id, role = role, method = method, year = years, citations = y,
          comparison_citations = control
        )
        pre <- years %in% 2012:2014
        post <- years %in% 2016:2018
        contrast <- mean(y[post] - control[post]) - mean(y[pre] - control[pre])
        data.frame(paper_id = id, contrast = contrast)
      })
      effect <- mean(do.call(rbind, changes)$contrast)
      external[[paste(role, method)]] <- data.frame(
        role = role, method = method, targets = length(ids), estimate = effect,
        se = NA_real_, lower = NA_real_, upper = NA_real_
      )
      if (method == "nearest") {
        stack <- do.call(rbind, lapply(ids, function(id) {
          rows <- matches[matches$paper_id == id, ]
          unit_ids <- c(id, rows$control_id)
          w <- c(1, rows$weight)
          do.call(rbind, lapply(seq_along(unit_ids), function(k) {
            years <- c(2012:2014, 2016:2018)
            data.frame(
              set = id, paper_id = unit_ids[k], stack_unit = paste(id, unit_ids[k]),
              year = years, citations = get_path(unit_ids[k], years), weight = w[k],
              exposed_post = as.integer(k == 1 & years >= 2016)
            )
          }))
        }))
        fit <- fixest::feols(citations ~ exposed_post | stack_unit + set^year,
          stack,
          weights = ~weight, vcov = ~ paper_id + set, ssc = ssc, fixef.rm = "none"
        )
        stopifnot(abs(coef(fit)[[1]] - effect) < 1e-7)
        row <- model_rows(fit, paste(role, method))
        external[[paste(role, method)]][c("se", "lower", "upper")] <- row[c("se", "lower", "upper")]
      }
    }
  }
  write(do.call(rbind, external), "external_estimates.csv")
  write(do.call(rbind, external_annual), "external_paths.csv")
  p <- ggplot2::ggplot(annual[annual$year >= 2010, ], ggplot2::aes(
    year, journal_standardized_mean,
    color = role
  )) +
    ggplot2::geom_line(linewidth = .6) +
    ggplot2::geom_point(size = 1.3) +
    ggplot2::geom_vline(xintercept = 2015, linetype = "dashed", color = "grey50") +
    ggplot2::scale_color_manual(values = c(successful = "#2878a5", unsuccessful = "#555555")) +
    ggplot2::labs(
      x = "Citation year", y = "Mean annual citations, standardized by journal", color = NULL
    ) +
    ggplot2::theme_minimal(base_size = 10) +
    ggplot2::theme(legend.position = "top")
  ggplot2::ggsave(file.path(path, "citation_paths.pdf"), p, width = 7, height = 4)
  ggplot2::ggsave(file.path(path, "citation_paths.png"), p, width = 7, height = 4, dpi = 150)
  writeLines(trimws(capture.output(sessionInfo()), which = "right"),
    con = file.path(path, "R-session.txt")
  )
  jsonlite::write_json(list(
    papers = nrow(identities), journal_weights = as.list(weights),
    citation_history_complete = all(targets$status == "complete"),
    bootstrap_undefined = sum(estimates$undefined_draws),
    raw_fe_identity_error = abs(coef(fits$article_year)[[1]] - raw),
    currently_retracted_targets = sum(coverage$is_retracted[
      coverage$paper_id %in% identities$paper_id
    ] == "True", na.rm = TRUE),
    pooled_with_statistical_error_audits = FALSE
  ), file.path(path, "analysis_checks.json"), pretty = TRUE, auto_unbox = TRUE)
}

if (sys.nframe() == 0L) rpp_main(commandArgs(trailingOnly = TRUE)[1])
