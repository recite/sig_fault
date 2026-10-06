lazic_changes <- function(panel, pre = 2016L, post = 2019L) {
  stopifnot(!length(intersect(pre, post)))
  x <- panel[panel$year %in% c(pre, post), ]
  stopifnot(setequal(x$article_id, panel$article_id))
  stopifnot(!anyDuplicated(x[c("article_id", "year")]))
  stopifnot(all(table(x$article_id) == length(c(pre, post))))
  stopifnot(!anyNA(x$citations), all(x$status == "complete"))
  x$post <- as.integer(x$year %in% post)
  x$paper_id <- x$article_id
  x$flag <- x$flagged
  lal_changes(x)
}

lazic_absolute <- function(changes, label) {
  treated <- changes$change[changes$flag == 1L]
  comparison <- changes$change[changes$flag == 0L]
  stopifnot(length(treated) > 1L, length(comparison) > 1L)
  v1 <- var(treated) / length(treated)
  v0 <- var(comparison) / length(comparison)
  se <- sqrt(v1 + v0)
  df <- (v1 + v0)^2 / (v1^2 / (length(treated) - 1) + v0^2 / (length(comparison) - 1))
  b <- mean(treated) - mean(comparison)
  data.frame(
    specification = label, n_flagged = length(treated), n_comparison = length(comparison),
    estimate = b, se = se, df = df,
    lower = b - qt(.975, df) * se, upper = b + qt(.975, df) * se
  )
}

lazic_bootstrap <- function(changes, repetitions = 5000L, seed = 2017L) {
  set.seed(seed)
  groups <- split(changes, changes$flag)
  draws <- replicate(repetitions, {
    samples <- lapply(groups, function(x) x[sample.int(nrow(x), nrow(x), replace = TRUE), ])
    means <- lapply(samples, function(x) c(before = mean(x$before), after = mean(x$after)))
    b <- means[["1"]]
    control <- means[["0"]]
    c(
      absolute = unname((b["after"] - b["before"]) - (control["after"] - control["before"])),
      log_ratio = if (all(c(b, control) > 0)) {
        unname(
          log(b["after"] / b["before"]) - log(control["after"] / control["before"])
        )
      } else {
        NA_real_
      }
    )
  })
  t(apply(draws, 1L, function(x) {
    c(
      finite_draws = sum(is.finite(x)), lower = unname(quantile(x, .025, na.rm = TRUE)),
      upper = unname(quantile(x, .975, na.rm = TRUE))
    )
  }))
}
