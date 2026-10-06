source(file.path("..", "..", "R", "i4r.R"))

make_i4r_panel <- function(effect = 5, events = 20) {
  out <- list()
  for (g in seq_len(events)) {
    for (j in 0:3) {
      for (post in 0:1) {
        base <- 10 + g + j
        out[[length(out) + 1L]] <- data.frame(
          stack_id = paste0("s", g), warning_id = paste0("w", g),
          article_id = paste0("p", g, "_", j), horizon = 1,
          treated = as.integer(j == 0), post = post,
          weight = if (j == 0) 1 else 1 / 3,
          citations = base + post * (2 + effect * (j == 0))
        )
      }
    }
  }
  do.call(rbind, out)
}

testthat::test_that("stacked estimator equals known effect and hand differences", {
  for (effect in c(-4, 0, 7)) {
    p <- make_i4r_panel(effect)
    testthat::expect_equal(i4r_direct(p), effect)
    testthat::expect_equal(i4r_estimate(p)$estimate, effect, tolerance = 1e-7)
  }
})

testthat::test_that("heterogeneous effects average equally across affected articles", {
  p <- make_i4r_panel(0)
  p$citations[p$stack_id == "s1" & p$treated == 1 & p$post == 1] <-
    p$citations[p$stack_id == "s1" & p$treated == 1 & p$post == 1] + 20
  testthat::expect_equal(i4r_estimate(p)$estimate, 1, tolerance = 1e-7)
})

testthat::test_that("invalid panels fail and a single event has no cluster interval", {
  p <- make_i4r_panel()
  testthat::expect_error(i4r_estimate(p[-1, ]), "Incomplete")
  testthat::expect_error(i4r_estimate(rbind(p, p[1, ])), "Duplicate")
  one <- make_i4r_panel(events = 1)
  testthat::expect_true(is.na(i4r_estimate(one)$lower))
})

testthat::test_that("one control per stack retains valid residual degrees of freedom", {
  p <- expand.grid(stack_id = paste0("s", 1:4), treated = 0:1, post = 0:1)
  p$stack_id <- as.character(p$stack_id)
  p$warning_id <- p$stack_id
  p$article_id <- paste0(p$stack_id, "_", p$treated)
  p$weight <- 1
  p$horizon <- 1
  p$citations <- 10 + as.numeric(sub("s", "", p$stack_id)) * p$treated * p$post
  result <- i4r_estimate(p)
  testthat::expect_equal(result$estimate, 2.5)
  testthat::expect_true(is.finite(result$standard_error))
  testthat::expect_gt(result$standard_error, 0)
})


testthat::test_that("reused-control inference equals independent sandwich arithmetic", {
  p <- expand.grid(stack_id = paste0("s", 1:4), treated = 0:1, post = 0:1)
  p$stack_id <- as.character(p$stack_id)
  p$warning_id <- p$stack_id
  p$article_id <- ifelse(p$treated == 1, paste0(p$stack_id, "_t"), "shared")
  p$weight <- 1
  p$horizon <- 1
  p$citations <- 10 + as.numeric(sub("s", "", p$stack_id)) * p$treated * p$post
  result <- i4r_estimate(p)
  testthat::expect_equal(result$estimate, 2.5)
  testthat::expect_equal(result$standard_error, sqrt(35 / 96), tolerance = 1e-8)
  p$weight[p$treated == 0] <- 0.5
  testthat::expect_error(i4r_estimate(p), "unit weight")
})
testthat::test_that("weighted medians agree with ordinary medians at equal weights", {
  testthat::expect_equal(i4r_weighted_median(c(7, 1, 5, 3), rep(1, 4)), 4)
  testthat::expect_equal(i4r_weighted_median(c(7, 1, 5), rep(1, 3)), 5)
  testthat::expect_equal(i4r_weighted_median(c(1, 4, 9), c(0.6, 0.2, 0.2)), 1)
  testthat::expect_equal(i4r_weighted_median(c(1, 4, 9), c(0.5, 0.25, 0.25)), 2.5)
  testthat::expect_error(i4r_weighted_median(c(1, NA), c(1, 1)), "Invalid")
})
