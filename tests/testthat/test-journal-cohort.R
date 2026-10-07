source(file.path(root, "R/journal_cohort.R"))

journal_fixture <- function() {
  x <- expand.grid(article_id = 1:32, year = c(2010L, 2012L))
  x$journal <- ifelse(x$article_id <= 16L, "A", "B")
  x$cohort <- ifelse((x$article_id - 1L) %% 16L < 8L, 2009L, 2010L)
  x$flag <- as.integer((x$article_id - 1L) %% 8L >= 4L)
  baseline <- 10 + 2 * x$article_id
  growth <- ifelse(x$journal == "A", 2, 4) * ifelse(x$cohort == 2009L, 1, 2)
  noise <- rep(c(-1, 1), length.out = nrow(x))
  x$citations <- ifelse(x$year == 2010L, baseline,
    baseline * growth * (1 + .5 * x$flag) + noise
  )
  x
}

test_that("journal/cohort effects recover a planted within-group proportional change", {
  x <- journal_fixture()
  result <- journal_cohort_fit(x, post = 2012L)
  expect_equal(result$estimate, log(1.5), tolerance = 1e-7)
  expect_gt(result$se, 0)
  x$stratum_year <- interaction(x$journal, x$cohort, x$year)
  x$flag_post <- x$flag * as.integer(x$year == 2012L)
  explicit <- glm(citations ~ flag_post + factor(article_id) + stratum_year,
    data = x, family = poisson()
  )
  expect_equal(result$estimate, unname(coef(explicit)["flag_post"]), tolerance = 1e-7)
  scaled <- transform(x, citations = citations * 10)
  larger <- journal_cohort_fit(scaled, post = 2012L)
  expect_equal(result$estimate, larger$estimate, tolerance = 1e-7)
  expect_equal(result$se, larger$se, tolerance = 1e-7)
})

test_that("descriptive weights balance every stratum without using citations", {
  x <- journal_fixture()
  x <- x[!x$article_id %in% c(1, 9), ]
  s <- journal_cohort_support(x)
  sums <- xtabs(weight ~ stratum + flag, s$papers)
  expect_equal(unname(sums[, 1]), unname(sums[, 2]))
  shifted <- journal_cohort_support(transform(x, citations = citations + 100))
  expect_equal(s$papers$weight, shifted$papers$weight)
  expect_equal(weighted_median_count(c(1, 2, 100), c(1, 1, 3)), 100)
  expect_equal(weighted_median_count(c(1, 2), c(1, 1)), 1)
})

test_that("missing histories and changing classifications cannot enter a model", {
  x <- journal_fixture()
  expect_error(journal_cohort_fit(x[-1, ], post = 2012L))
  expect_error(journal_cohort_fit(rbind(x, x[1, ]), post = 2012L))
  x$flag[1] <- 1L - x$flag[1]
  expect_error(journal_cohort_fit(x, post = 2012L))
})

test_that("unsupported strata are explicitly excluded", {
  x <- journal_fixture()
  x <- x[!x$article_id %in% 1:4, ]
  fit <- journal_cohort_fit(x, post = 2012L)
  expect_setequal(strsplit(fit$unsupported_papers, ";")[[1]], as.character(5:8))
  expect_equal(fit$n_flagged, 12L)
  expect_equal(fit$n_comparison, 12L)
})

test_that("real-data coefficients and clustered uncertainty match explicit dummy regressions", {
  panel <- read.csv(file.path(root, "data/nieuwenhuis/paired_panel.csv"))
  for (source in c("wos", "openalex")) {
    for (cohort in c("all", "2009")) {
      x <- panel[panel$year %in% c(2010L, 2012:2015), ]
      if (cohort == "2009") x <- x[x$cohort == 2009L, ]
      x$citations <- x[[source]]
      x$group_year <- interaction(x$journal, x$cohort, x$year, drop = TRUE)
      x$flag_post <- x$flag * as.integer(x$year != 2010L)
      full <- model.matrix(~ flag_post + factor(article_id) + group_year, data = x)
      decomposition <- qr(full)
      matrix <- full[, decomposition$pivot[seq_len(decomposition$rank)], drop = FALSE]
      for (poisson in c(TRUE, FALSE)) {
        fit <- if (poisson) {
          glm.fit(matrix, x$citations,
            family = poisson(),
            control = glm.control(epsilon = 1e-10, maxit = 100)
          )
        } else {
          lm.fit(matrix, x$citations)
        }
        residual <- if (poisson) x$citations - fit$fitted.values else fit$residuals
        bread <- solve(crossprod(matrix, matrix * if (poisson) fit$fitted.values else 1))
        scores <- rowsum(matrix * residual, x$article_id)
        covariance <- bread %*% crossprod(scores) %*% bread
        actual <- journal_cohort_fit(x, poisson = poisson)
        n <- nrow(x)
        clusters <- length(unique(x$article_id))
        adjustment <- clusters / (clusters - 1) * (n - 1) / (n - actual$vcov_parameters)
        se <- sqrt(covariance["flag_post", "flag_post"] * adjustment)
        expect_equal(unname(fit$coefficients["flag_post"]), actual$estimate, tolerance = 1e-7)
        expect_equal(se, actual$se, tolerance = 1e-7)
      }
    }
  }
})
