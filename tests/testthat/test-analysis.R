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
