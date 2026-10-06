source(file.path(root, "R/nieuwenhuis.R"))

bridge_fixture <- function() {
  x <- expand.grid(article_id = 1:8, year = c(2010L, 2012:2015))
  x$flag <- as.integer(x$article_id > 4)
  x$cohort <- 2009L
  x$journal <- "Journal"
  x$status <- "complete"
  x$wos <- (x$article_id + 1L) * (x$year - 2008L) + x$flag * (x$year > 2010L)
  x$openalex <- x$wos
  x$openalex_broad <- 2L * x$wos
  x
}

test_that("paired bootstrap preserves exact agreement despite heterogeneous counts", {
  x <- bridge_changes(bridge_fixture())
  result <- bridge_comparison(x, "openalex", draws = 199L)
  expect_equal(result$difference, c(0, 0))
  expect_equal(result$se, c(0, 0))
  expect_equal(result$lower, c(0, 0))
  expect_equal(result$upper, c(0, 0))
  expect_equal(result$undefined_draws, c(0L, 0L))
  expect_identical(result, bridge_comparison(x, "openalex", draws = 199L))
  result <- bridge_comparison(x, "openalex_broad", draws = 199L)
  expect_equal(result$difference[1], result$wos[1])
  expect_equal(result$difference[2], 0, tolerance = 1e-12)
})

test_that("balanced-panel closed form agrees with article/year fixed-effects Poisson", {
  x <- bridge_fixture()
  x$wos[x$article_id == 1L] <- 0L
  x$wos[x$article_id == 2L & x$year == 2013L] <- 0L
  for (post in list(2012L, 2012:2015)) {
    changes <- bridge_changes(x, post)
    actual <- bridge_contrasts(changes, "wos")
    expected <- suppressMessages(panel_model(transform(x, citations = wos), "test", post = post))
    expect_equal(unname(actual["log_ratio"]), expected$estimate, tolerance = 1e-7)
    ols <- panel_model(transform(x, citations = wos), "test", post = post, poisson = FALSE)
    expect_equal(unname(actual["absolute"]), ols$estimate, tolerance = 1e-10)
  }
})

test_that("known source changes have the correct sign and scale", {
  x <- bridge_fixture()
  x$openalex[x$flag == 1L & x$year > 2010L] <- 2L * x$wos[x$flag == 1L & x$year > 2010L]
  result <- bridge_comparison(bridge_changes(x), "openalex", draws = 199L)
  expect_equal(result$difference[2], log(2))
  expect_equal(result$lower[2], log(2))
  expect_equal(result$upper[2], log(2))
  expected <- mean(x$wos[x$flag == 1L & x$year > 2010L])
  expect_equal(result$difference[1], expected)
})

test_that("incomplete histories are excluded from both sources, never filled with zero", {
  x <- bridge_fixture()
  x$status[x$article_id == 1L & x$year == 2012L] <- "missing_history"
  x$openalex[x$article_id == 1L & x$year == 2012L] <- NA
  x <- x[!(x$article_id == 2L & x$year == 2013L), ]
  expect_equal(bridge_changes(x)$article_id, 3:8)
  expect_equal(bridge_changes(x, 2012L)$article_id, 2:8)
  empty <- x
  empty$status <- "missing_history"
  expect_equal(nrow(bridge_changes(empty)), 0L)
  expect_error(bridge_changes(rbind(x, x[1, ])))
  x$openalex[x$article_id == 3L] <- NA
  expect_error(bridge_changes(x))
})

test_that("missing groups and degenerate proportional resamples remain explicit", {
  x <- bridge_changes(bridge_fixture())
  result <- bridge_comparison(x[x$flag == 1L, ], "openalex", draws = 99L)
  expect_true(all(result$status == "missing_group"))
  expect_true(all(is.na(result$difference)))
  expect_equal(result$bootstrap_draws, c(0L, 0L))
  result <- bridge_comparison(x[FALSE, ], "openalex", draws = 99L)
  expect_true(all(result$status == "missing_group"))
  x$openalex_before[x$flag == 1L] <- c(0, 0, 0, 1)
  result <- bridge_comparison(x, "openalex", draws = 199L)
  expect_true(is.finite(result$difference[2]))
  expect_gt(result$undefined_draws[2], 0)
  expect_true(is.na(result$lower[2]))
  expect_equal(result$status[2], "undefined_bootstrap_draws")
  expect_equal(result$status[1], "complete")
})

test_that("flagged-only real histories cannot identify a source contrast", {
  panel <- read.csv(file.path(root, "data/nieuwenhuis/paired_panel.csv"))
  x <- bridge_changes(panel[panel$flag == 1L, ])
  result <- bridge_comparison(x, "openalex")
  expect_equal(result$n_comparison, c(0L, 0L))
  expect_true(all(result$status == "missing_group"))
})
