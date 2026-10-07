journal_cohort_support <- function(panel, stratum_columns = c("journal", "cohort")) {
  required <- unique(c(
    "article_id", "year", "flag", "cohort", "journal", "citations",
    stratum_columns
  ))
  stopifnot(all(required %in% names(panel)), !anyNA(panel[required]))
  stopifnot(!anyDuplicated(panel[c("article_id", "year")]))
  stopifnot(all(panel$flag %in% 0:1), all(is.finite(panel$citations)), all(panel$citations >= 0))
  meta <- unique(panel[unique(c("article_id", "flag", "cohort", "journal", stratum_columns))])
  stopifnot(!anyDuplicated(meta$article_id))
  meta$stratum <- do.call(paste, c(meta[stratum_columns], sep = " / "))
  strata <- do.call(rbind, lapply(split(meta, meta$stratum), function(g) {
    data.frame(
      stratum = g$stratum[1], journal = g$journal[1], cohort = g$cohort[1],
      flagged = sum(g$flag == 1L), comparison = sum(g$flag == 0L)
    )
  }))
  strata$supported <- strata$flagged > 0L & strata$comparison > 0L
  index <- match(meta$stratum, strata$stratum)
  meta$supported <- strata$supported[index]
  meta$weight <- ifelse(meta$flag == 1L, 1, strata$flagged[index] / strata$comparison[index])
  list(papers = meta, strata = strata)
}

journal_cohort_model <- function(panel, post = 2012:2015, pre = 2010L, poisson = TRUE,
                                 stratum_columns = c("journal", "cohort")) {
  stopifnot(length(pre) == 1L, !pre %in% post, length(post) > 0L, !anyDuplicated(post))
  support <- journal_cohort_support(panel, stratum_columns)
  ids <- support$papers$article_id[support$papers$supported]
  x <- panel[panel$article_id %in% ids & panel$year %in% c(pre, post), ]
  stopifnot(setequal(x$article_id, ids), all(table(x$article_id) == length(post) + 1L))
  x$stratum <- support$papers$stratum[match(x$article_id, support$papers$article_id)]
  x$flag_post <- x$flag * as.integer(x$year %in% post)
  correction <- fixest::ssc(
    K.adj = TRUE, K.fixef = "nonnested", K.exact = FALSE,
    G.adj = TRUE, G.df = "min", t.df = "min"
  )
  formula <- citations ~ flag_post | article_id + stratum^year
  fitter <- if (poisson) fixest::fepois else fixest::feols
  options <- list(
    fml = formula, data = x, nthreads = 1,
    vcov = fixest::vcov_cluster(cluster = ~article_id, vcov_fix = FALSE), ssc = correction
  )
  if (poisson) options <- c(options, list(glm.tol = 1e-10, fixef.tol = 1e-10))
  fit <- do.call(fitter, options)
  if (poisson) stopifnot(isTRUE(fit$convStatus))
  stopifnot("flag_post" %in% names(coef(fit)))
  used <- x[fixest::obs(fit), ]
  meta <- unique(used[c("article_id", "flag")])
  b <- unname(coef(fit)["flag_post"])
  se <- sqrt(vcov(fit)["flag_post", "flag_post"])
  df <- nrow(meta) - 1L
  interval <- b + c(-1, 1) * qt(.975, df) * se
  estimate <- data.frame(
    model = if (poisson) "PPML" else "OLS", pre = pre, post = paste(post, collapse = ";"),
    n_flagged = sum(meta$flag), n_comparison = sum(meta$flag == 0L),
    observations = nrow(used), estimate = b, se = se, df = df,
    lower = interval[1], upper = interval[2],
    percent = if (poisson) 100 * expm1(b) else NA_real_,
    percent_lower = if (poisson) 100 * expm1(interval[1]) else NA_real_,
    percent_upper = if (poisson) 100 * expm1(interval[2]) else NA_real_,
    excluded_papers = paste(setdiff(ids, meta$article_id), collapse = ";"),
    unsupported_papers = paste(setdiff(support$papers$article_id, ids), collapse = ";"),
    vcov_parameters = attr(vcov(fit, attr = TRUE), "df.K")
  )
  list(estimate = estimate, model = fit, panel = used)
}

journal_cohort_fit <- function(...) journal_cohort_model(...)$estimate

weighted_median_count <- function(value, weight) {
  stopifnot(length(value) == length(weight), length(value) > 0L)
  stopifnot(!anyNA(value), !anyNA(weight), all(weight > 0), all(is.finite(weight)))
  order <- order(value)
  value[order][which(cumsum(weight[order]) >= sum(weight) / 2)[1]]
}

journal_cohort_paths <- function(panel) {
  support <- journal_cohort_support(panel)
  meta <- support$papers[support$papers$supported, ]
  x <- panel[panel$article_id %in% meta$article_id, ]
  x$weight <- meta$weight[match(x$article_id, meta$article_id)]
  stopifnot(!anyNA(x$weight))
  do.call(rbind, lapply(split(x, list(x$flag, x$year), drop = TRUE), function(g) {
    data.frame(
      flag = g$flag[1], year = g$year[1], papers = nrow(g), sum_weights = sum(g$weight),
      mean = weighted.mean(g$citations, g$weight),
      median = weighted_median_count(g$citations, g$weight)
    )
  }))
}
