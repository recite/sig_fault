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
