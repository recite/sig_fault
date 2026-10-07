article_changes <- function(panel, pre = 2010L, post = 2012:2015) {
  stopifnot(length(intersect(pre, post)) == 0L, all(c(pre, post) %in% panel$year))
  before <- aggregate(citations ~ article_id, panel[panel$year %in% pre, ], mean)
  after <- aggregate(citations ~ article_id, panel[panel$year %in% post, ], mean)
  meta <- unique(panel[c("article_id", "flag", "serious", "cohort", "journal")])
  stopifnot(!anyDuplicated(meta$article_id))
  meta$before <- before$citations[match(meta$article_id, before$article_id)]
  meta$after <- after$citations[match(meta$article_id, after$article_id)]
  meta$change <- meta$after - meta$before
  stopifnot(!anyNA(meta))
  meta
}

estimate_change <- function(x, label, adjusted = FALSE) {
  if (adjusted) {
    fit <- lm(change ~ flag + factor(cohort) + factor(journal), data = x)
    stopifnot(fit$rank == ncol(model.matrix(fit)))
    estimate <- unname(coef(fit)["flag"])
    se <- sqrt(sandwich::vcovHC(fit, type = "HC3")["flag", "flag"])
    df <- df.residual(fit)
  } else {
    a <- x$change[x$flag == 1L]
    b <- x$change[x$flag == 0L]
    test <- t.test(a, b)
    estimate <- mean(a) - mean(b)
    se <- sqrt(var(a) / length(a) + var(b) / length(b))
    df <- unname(test$parameter)
  }
  data.frame(
    specification = label, n_flagged = sum(x$flag == 1L),
    n_comparison = sum(x$flag == 0L), estimate = estimate, se = se, df = df,
    lower = estimate - qt(.975, df) * se, upper = estimate + qt(.975, df) * se,
    method = if (adjusted) "OLS; HC3; residual t" else "Welch t"
  )
}

annual_summary <- function(panel) {
  do.call(rbind, lapply(split(panel, list(panel$flag, panel$year), drop = TRUE), function(x) {
    data.frame(
      flag = x$flag[1], year = x$year[1], n = nrow(x),
      total = sum(x$citations), mean = mean(x$citations), median = median(x$citations),
      zero = sum(x$citations == 0L), maximum = max(x$citations)
    )
  }))
}

wilson_interval <- function(successes, n, level = .95) {
  z <- qnorm(1 - (1 - level) / 2)
  p <- successes / n
  center <- (p + z^2 / (2 * n)) / (1 + z^2 / n)
  half <- z * sqrt(p * (1 - p) / n + z^2 / (4 * n^2)) / (1 + z^2 / n)
  c(lower = center - half, upper = center + half)
}

panel_model <- function(panel, label, post = 2012:2015, effects = "basic", poisson = TRUE,
                        pre = 2010L) {
  stopifnot(length(pre) == 1L, !pre %in% post, all(c(pre, post) %in% panel$year))
  x <- panel[panel$year %in% c(pre, post), ]
  stopifnot(!anyDuplicated(x[c("article_id", "year")]))
  stopifnot(all(table(x$article_id) == length(post) + 1L))
  requested_n <- nrow(x)
  excluded_ids <- integer()
  if (poisson) {
    totals <- aggregate(citations ~ article_id, x, sum)
    excluded_ids <- totals$article_id[totals$citations == 0]
    x <- x[!x$article_id %in% excluded_ids, ]
  }
  stopifnot(length(unique(x$flag)) == 2L)
  x$flag_post <- x$flag * as.integer(x$year %in% post)
  fe <- switch(effects,
    basic = "article_id + year",
    journal = "article_id + journal^year",
    cohort = "article_id + cohort^year",
    both = "article_id + journal^year + cohort^year",
    stop("Unknown fixed effects")
  )
  formula <- as.formula(paste("citations ~ flag_post |", fe))
  correction <- fixest::ssc(
    K.adj = TRUE, K.fixef = "nonnested", K.exact = FALSE,
    G.adj = TRUE, G.df = "min", t.df = "min"
  )
  fit <- if (poisson) {
    fixest::fepois(formula, x,
      vcov = ~article_id, ssc = correction,
      glm.tol = 1e-10, fixef.tol = 1e-10, nthreads = 1
    )
  } else {
    fixest::feols(formula, x, vcov = ~article_id, ssc = correction, nthreads = 1)
  }
  stopifnot(nobs(fit) == nrow(x), "flag_post" %in% names(coef(fit)))
  if (poisson) stopifnot(isTRUE(fit$convStatus))
  b <- unname(coef(fit)["flag_post"])
  se <- sqrt(vcov(fit)["flag_post", "flag_post"])
  g <- length(unique(x$article_id))
  df <- g - 1L
  lower <- b - qt(.975, df) * se
  upper <- b + qt(.975, df) * se
  lower_one <- b - qt(.95, df) * se
  meta <- unique(x[c("article_id", "flag")])
  data.frame(
    specification = label, model = if (poisson) "PPML" else "OLS",
    scale = if (poisson) "log relative post/pre citation ratio" else "citations per paper per year",
    n_flagged = sum(meta$flag), n_comparison = sum(meta$flag == 0L),
    observations = nrow(x), clusters = g, excluded_observations = requested_n - nobs(fit),
    excluded_papers = paste(excluded_ids, collapse = ","),
    vcov_parameters = attr(vcov(fit, attr = TRUE), "df.K"),
    estimate = b, se = se, df = df, lower = lower, upper = upper, lower_one_sided = lower_one,
    ratio = if (poisson) exp(b) else NA_real_,
    percent = if (poisson) 100 * expm1(b) else NA_real_,
    percent_lower = if (poisson) 100 * expm1(lower) else NA_real_,
    percent_upper = if (poisson) 100 * expm1(upper) else NA_real_,
    percent_lower_one_sided = if (poisson) 100 * expm1(lower_one) else NA_real_,
    method = "Article-clustered; nonnested FE adjustment; t(G-1)"
  )
}

log_growth_ratio <- function(x) {
  group <- aggregate(cbind(before, after) ~ flag, x, mean)
  stopifnot(identical(group$flag, c(0L, 1L)), all(group$before > 0), all(group$after > 0))
  log(group$after[2] / group$before[2]) - log(group$after[1] / group$before[1])
}
