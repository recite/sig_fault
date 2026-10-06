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
