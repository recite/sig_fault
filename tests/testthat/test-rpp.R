source(file.path(root, "R", "rpp.R"))

test_that("journal standardization recovers the intended change and its variance", {
  d <- data.frame(
    journal = rep(c("A", "B"), each = 6),
    role = rep(rep(c("unsuccessful", "successful"), each = 3), 2),
    pre = rep(10, 12), post = c(10, 12, 14, 10, 11, 12, 13, 15, 17, 11, 12, 13)
  )
  w <- c(A = .25, B = .75)
  result <- rpp_contrast(d, w)
  expect_equal(result$estimate, .25 * 1 + .75 * 3)
  variance <- (.25^2 + .75^2) * (4 / 3 + 1 / 3)
  expect_equal(result$se^2, variance)
  expect_equal(result$log_ratio, .25 * log(12 / 11) + .75 * log(15 / 12))
})

test_that("undefined proportional bootstrap draws remain visible", {
  d <- data.frame(
    journal = rep("A", 6), role = rep(c("unsuccessful", "successful"), each = 3),
    pre = rep(0, 6), post = c(1, 2, 3, 1, 2, 3)
  )
  result <- rpp_bootstrap(d, c(A = 1), draws = 20)
  expect_equal(result$undefined, 20)
  expect_true(is.na(result$lower))
})
