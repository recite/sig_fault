source(file.path(root, "R/meta.R"))

test_that("fixed-audit inference agrees with an independent Welch calculation", {
  a <- c(-2, -1, 0, 1, 3, 5, 8)
  b <- c(-4, -3, -1, 0, 2)
  x <- data.frame(
    audit = c("a", "b"), estimate = c(mean(a), -mean(b)),
    se = c(sd(a) / sqrt(length(a)), sd(b) / sqrt(length(b))),
    df = c(length(a) - 1, length(b) - 1)
  )
  actual <- equal_audit_synthesis(x)
  expected <- t.test(a, b)
  expect_equal(actual$estimate, unname(diff(rev(expected$estimate))) / 2)
  expect_equal(actual$df, unname(expected$parameter))
  expect_equal(actual$lower, 100 * expm1(expected$conf.int[1] / 2))
  expect_equal(actual$upper, 100 * expm1(expected$conf.int[2] / 2))
})

test_that("geometric averages do not become arithmetic percentage averages", {
  x <- data.frame(audit = c("a", "b"), estimate = log(c(.5, 2)), se = c(.1, .2), df = c(20, 30))
  actual <- equal_audit_synthesis(x)
  expect_equal(actual$percent, 0, tolerance = 1e-12)
  expect_equal(actual$estimate, equal_audit_synthesis(x[2:1, ])$estimate)
  expect_error(equal_audit_synthesis(x[1, ]))
  x$audit <- "same_audit"
  expect_error(equal_audit_synthesis(x))
})

test_that("inverse-variance synthesis matches independent weighted-normal inference", {
  x <- data.frame(audit = c("a", "b", "c"), estimate = c(-.3, .1, .2), se = c(.1, .2, .4))
  actual <- precision_synthesis(x)
  w <- (1 / x$se^2) / sum(1 / x$se^2)
  b <- sum(w * x$estimate)
  se <- sqrt(sum(w^2 * x$se^2))
  expect_equal(actual$estimate, b)
  expect_equal(actual$se, se)
  expect_equal(actual$lower, 100 * expm1(b - qnorm(.975) * se))
  expect_equal(actual$lower_one_sided_95, 100 * expm1(b - qnorm(.95) * se))
  expect_equal(actual$q, sum((x$estimate - b)^2 / x$se^2))
  expect_equal(actual$estimate, precision_synthesis(x[3:1, ])$estimate)
  expect_error(precision_synthesis(x[1, ]))
  expect_error(precision_synthesis(transform(x, audit = "a")))
  expect_error(precision_synthesis(transform(x, se = 0)))
  expect_error(precision_synthesis(transform(x, estimate = NA_real_)))
})

test_that("modified Knapp-Hartung retains uncertainty when estimates coincide", {
  x <- data.frame(audit = c("a", "b", "c"), estimate = rep(.1, 3), se = rep(.2, 3))
  actual <- precision_synthesis(x, random = TRUE)
  expect_equal(actual$estimate, .1)
  expect_equal(actual$tau2, 0, tolerance = 1e-8)
  expect_equal(actual$se, .2 / sqrt(3), tolerance = 1e-7)
  expect_equal(actual$df, 2)
  expect_equal(actual$lower, 100 * expm1(.1 - qt(.975, 2) * .2 / sqrt(3)),
    tolerance = 1e-7
  )
})
