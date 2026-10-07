test_that("annual means and contrast agree with an independent matrix calculation", {
  panel <- read_derived("panel")
  matrix <- xtabs(citations ~ article_id + year, panel)
  ids <- as.integer(rownames(matrix))
  flag <- panel$flag[match(ids, panel$article_id)]
  delta <- rowMeans(matrix[, as.character(2012:2015)]) - matrix[, "2010"]
  a <- delta[flag == 1L]
  b <- delta[flag == 0L]
  result <- read_derived("estimates")[1, ]
  expect_equal(result$estimate, mean(a) - mean(b), tolerance = 1e-12)
  expect_equal(result$se, sqrt(var(a) / length(a) + var(b) / length(b)), tolerance = 1e-12)
  reference <- t.test(a, b)
  expect_equal(c(result$lower, result$upper), as.numeric(reference$conf.int), tolerance = 1e-12)
  changes <- read_derived("changes")
  fit <- lm(change ~ flag, changes)
  expect_equal(unname(coef(fit)["flag"]), result$estimate, tolerance = 1e-12)
  expect_equal(sqrt(unname(sandwich::vcovHC(fit, type = "HC2")["flag", "flag"])),
    result$se,
    tolerance = 1e-12
  )
})

test_that("a planted change is recovered with the correct sign and unit", {
  panel <- expand.grid(article_id = 1:12, year = c(2010L, 2012:2015))
  panel$flag <- as.integer(panel$article_id > 6L)
  panel$serious <- FALSE
  panel$cohort <- 2009L
  panel$journal <- "Journal"
  panel$citations <- panel$article_id + ifelse(panel$year == 2010L, 0,
    7 + 3 * panel$flag + (panel$article_id - 1L) %% 6L
  )
  changes <- article_changes(panel)
  estimate <- estimate_change(changes, "Synthetic")
  expect_equal(estimate$estimate, 3)
  expect_equal(changes$change, 7 + 3 * changes$flag + (changes$article_id - 1L) %% 6L)
  expect_gt(estimate$se, 0)
  expect_error(article_changes(panel, pre = 2010L, post = 2010:2012))
})

test_that("sensitivity comparisons preserve their stated groups and timing", {
  estimates <- read_derived("estimates")
  expect_equal(estimates$n_flagged[1], 76L)
  expect_equal(estimates$n_comparison[1], 77L)
  serious <- estimates[estimates$specification == "Potentially serious errors only", ]
  expect_equal(serious$n_flagged, 43L)
  expect_equal(serious$n_comparison, 77L)
  panel <- read_derived("panel")
  early <- article_changes(panel)
  later <- article_changes(panel, post = 2014:2015)
  expect_equal(early$before, later$before)
  expect_equal(early$article_id, later$article_id)
  years <- read_derived("year_changes")
  expect_true(all(years$lower_simultaneous < years$lower))
  expect_true(all(years$upper_simultaneous > years$upper))
})

test_that("Wilson bounds behave at the boundaries and contain the observed proportion", {
  expect_equal(unname(wilson_interval(0L, 100L)[1]), 0, tolerance = 1e-12)
  expect_equal(unname(wilson_interval(100L, 100L)[2]), 1, tolerance = 1e-12)
  ci <- wilson_interval(1L, 96L)
  expect_lt(ci[1], 1 / 96)
  expect_gt(ci[2], 1 / 96)
})

test_that("Poisson fixed effects agree with dummy regression and direct growth ratios", {
  panel <- read_derived("panel")
  result <- panel_model(panel, "Check")
  changes <- article_changes(panel)
  expect_equal(result$estimate, log_growth_ratio(changes), tolerance = 1e-8)
  x <- panel[panel$year %in% c(2010L, 2012:2015), ]
  x$flag_post <- x$flag * as.integer(x$year >= 2012L)
  fit <- glm(citations ~ flag_post + factor(article_id) + factor(year),
    data = x, family = poisson(), control = glm.control(epsilon = 1e-10)
  )
  expect_true(fit$converged)
  expect_equal(result$estimate, unname(coef(fit)["flag_post"]), tolerance = 1e-8)
  g <- length(unique(x$article_id))
  n <- nrow(x)
  v <- sandwich::vcovCL(fit, cluster = x$article_id, type = "HC0", cadjust = FALSE)
  v <- v * g / (g - 1) * (n - 1) / (n - 6)
  expect_equal(result$se, sqrt(v["flag_post", "flag_post"]), tolerance = 1e-6)
  expect_equal(result$observations, 765L)
  expect_equal(result$clusters, 153L)
  expect_equal(result$excluded_observations, 0L)
  expect_equal(result$percent, 100 * expm1(result$estimate))
  expect_equal(
    result$percent_lower_one_sided,
    100 * expm1(result$estimate - qt(.95, g - 1) * result$se)
  )
  expect_gt(result$percent_lower_one_sided, result$percent_lower)
  linear <- panel_model(panel, "Linear check", poisson = FALSE)
  expect_equal(linear$estimate, estimate_change(changes, "Difference")$estimate, tolerance = 1e-8)
})

test_that("a planted multiplicative change is recovered and zero histories are reported", {
  panel <- expand.grid(article_id = 1:12, year = c(2010L, 2012:2015))
  panel$flag <- as.integer(panel$article_id > 6)
  panel$cohort <- 2009L
  panel$journal <- "Journal"
  panel$citations <- 4 * panel$article_id * ifelse(panel$year == 2010L, 1,
    (panel$year - 2010L) * ifelse(panel$flag == 1L, .5, 1)
  )
  shock <- ifelse(panel$article_id %in% c(1L, 7L), 1,
    ifelse(panel$article_id %in% c(2L, 8L), -1, 0)
  )
  panel$citations <- panel$citations + shock * (panel$year - 2010L)
  fit <- panel_model(panel, "Planted")
  expect_equal(fit$estimate, log(.5), tolerance = 1e-8)
  expect_equal(fit$percent, -50, tolerance = 1e-6)
  zero <- transform(panel[panel$article_id == 1L, ], article_id = 13L, citations = 0)
  with_zero <- panel_model(rbind(panel, zero), "Zero history")
  expect_equal(with_zero$estimate, fit$estimate, tolerance = 1e-8)
  expect_equal(with_zero$excluded_observations, 5L)
  expect_equal(with_zero$excluded_papers, "13")
  expect_error(panel_model(panel[-1L, ], "Missing year"))
  expect_error(panel_model(panel, "Overlap", post = 2010:2012))
})

test_that("proportional variants preserve support and uncertainty definitions", {
  q <- read_derived("proportional")
  expect_equal(nrow(q), 12L)
  expect_true(all(q$model == "PPML"))
  expect_true(all(q$df == q$clusters - 1L))
  expect_true(all(q$percent_lower_one_sided > q$percent_lower))
  expect_equal(q$n_flagged[1:4], rep(76L, 4))
  expect_equal(q$n_comparison[1:4], rep(77L, 4))
  y <- read_derived("proportional_years")
  expect_true(all(y$lower_simultaneous < y$percent_lower))
  expect_true(all(y$upper_simultaneous > y$percent_upper))
  expect_true(all(y$observations + y$excluded_observations == 153L * 2L))
  metrics <- jsonlite::read_json(file.path(root, "tabs/results.json"), simplifyVector = TRUE)
  expect_equal(metrics$proportional_bootstrap$draws, 9999L)
  expect_equal(metrics$proportional_bootstrap$failed_draws, 0L)
  expect_equal(metrics$descriptive$flagged_median_before, 5)
  expect_equal(metrics$descriptive$flagged_median_post_range, c(13, 17))
  expect_equal(metrics$descriptive$flagged_increased, 69L)
})

test_that("explicit baseline years preserve estimates after a calendar shift", {
  panel <- read_derived("panel")
  expected <- panel_model(panel, "Calendar check")
  panel$year <- panel$year + 7L
  shifted <- panel_model(panel, "Calendar check", pre = 2017L, post = 2019:2022)
  expect_equal(shifted, expected, tolerance = 1e-8)
  expect_error(panel_model(panel, "Overlapping baseline", pre = 2019L, post = 2019:2022))
})
