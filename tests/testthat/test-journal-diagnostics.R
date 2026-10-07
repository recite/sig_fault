source(file.path(root, "R/journal_cohort.R"))
source(file.path(root, "R/design_diagnostics.R"))

test_that("unknown study populations are not recoded as animals", {
  x <- data.frame(
    animal = c("humans ", "mice", ""), within_between_ss = c("within", "between", "within"),
    country_authors = c("US ", "UK", "")
  )
  result <- design_characteristics(x)
  expect_equal(result$subject_type, c("human", "nonhuman", "unknown"))
  expect_equal(result$species_unknown, c(0L, 0L, 1L))
  expect_equal(result$country_unknown, c(0L, 0L, 1L))
})

test_that("equal-flagged contrasts retain their target with heterogeneous cell effects", {
  x <- expand.grid(article_id = 1:8, year = c(2010L, 2012:2015))
  x$journal <- ifelse(x$article_id <= 4L, "A", "B")
  x$cohort <- 2009L
  x$flag <- as.integer(x$article_id %in% c(1, 2, 3, 5))
  effect <- ifelse(x$journal == "A", 8, 0)
  noise <- c(-1, 0, 1, 0, 0, -1, 0, 1)[x$article_id]
  x$citations <- 10 + ifelse(x$year == 2010L, 0, 2 + x$flag * effect + noise)
  result <- equal_flagged_change(x)
  expect_equal(result$estimate$estimate, 6, tolerance = 1e-10)
  expect_equal(journal_cohort_fit(x, poisson = FALSE)$estimate, 4, tolerance = 1e-10)
  expect_equal(result$papers$outcome_weight[result$papers$flag == 1L], rep(.25, 4))
  expect_equal(sum(result$papers$outcome_weight), 0, tolerance = 1e-12)
  expect_equal(sum(result$papers$variance_share), 1, tolerance = 1e-10)
})

test_that("real-data weighting identities match direct cell calculations", {
  panel <- read.csv(file.path(root, "data/nieuwenhuis/paired_panel.csv"))
  weights <- read.csv(file.path(root, "data/nieuwenhuis/design/estimation_weights.csv"))
  for (source in c("wos", "openalex")) {
    x <- transform(panel, citations = panel[[source]])
    result <- equal_flagged_change(x)
    m <- result$papers
    direct <- do.call(rbind, lapply(split(m, m$stratum), function(g) {
      data.frame(
        difference = mean(g$change[g$flag == 1L]) - mean(g$change[g$flag == 0L]),
        n_flagged = sum(g$flag), n_comparison = sum(g$flag == 0L)
      )
    }))
    linear_weight <- with(direct, n_flagged * n_comparison / (n_flagged + n_comparison))
    linear <- weighted.mean(direct$difference, linear_weight)
    expect_equal(journal_cohort_fit(x, poisson = FALSE)$estimate, linear, tolerance = 1e-8)
    expect_equal(result$estimate$estimate,
      weighted.mean(direct$difference, direct$n_flagged),
      tolerance = 1e-8
    )
    w <- weights[weights$source == source & weights$design == "journal_year", ]
    expect_equal(sum(w$linear_weight), 1, tolerance = 1e-12)
    expect_equal(sum(w$information_share), 1, tolerance = 1e-12)
    expect_true(all(w$information_share > 0))
  }
})
