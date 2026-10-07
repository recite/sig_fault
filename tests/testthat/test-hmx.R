source(file.path(root, "R/hmx.R"))

test_that("interaction samples retain unknowns and exclusions as specified", {
  panel <- hmx_panel(file.path(root, "data/cohorts/hmx/pipeline"))
  primary <- hmx_sample(panel)
  nonoverlap <- hmx_sample(panel, selection = "nonoverlap")
  expect_equal(length(unique(primary$paper_id)), 22L)
  expect_equal(length(unique(nonoverlap$paper_id)), 21L)
  expect_false("hmx_21" %in% nonoverlap$paper_id)
  expect_true("hmx_22" %in% nonoverlap$paper_id)
  linearity <- hmx_sample(panel, "linearity_rejected")
  expect_equal(length(unique(linearity$paper_id)), 20L)
  expect_false(any(linearity$linearity_rejected == "unknown"))
  supported <- hmx_sample(panel, selection = "journal_support")
  expect_equal(length(unique(supported$paper_id)), 19L)
  expect_false("IO" %in% supported$journal)
})

test_that("interaction PPML agrees with direct ratios and a dummy-variable model", {
  panel <- hmx_sample(hmx_panel(file.path(root, "data/cohorts/hmx/pipeline")))
  x <- panel[panel$year %in% c(2017L, 2019L), ]
  before <- tapply(x$citations[x$year == 2017L], x$flag[x$year == 2017L], sum)
  after <- tapply(x$citations[x$year == 2019L], x$flag[x$year == 2019L], sum)
  expected <- log((after[2] / before[2]) / (after[1] / before[1]))
  actual <- panel_model(panel, "primary", pre = 2017L, post = 2019L)
  expect_equal(actual$estimate, unname(expected), tolerance = 1e-10)
  expect_equal(actual$excluded_papers, "hmx_22")
  expect_equal(actual$n_comparison, 7L)
  x <- x[x$article_id != "hmx_22", ]
  x$flag_post <- x$flag * as.integer(x$year == 2019L)
  fit <- glm(citations ~ flag_post + factor(article_id) + factor(year),
    data = x, family = poisson(), control = glm.control(epsilon = 1e-10)
  )
  expect_equal(actual$estimate, unname(coef(fit)["flag_post"]), tolerance = 1e-8)
  covariance <- sandwich::vcovCL(fit, cluster = x$article_id, type = "HC0", cadjust = FALSE)
  covariance <- covariance * 21 / 20 * 41 / 39
  expect_equal(actual$se, sqrt(covariance["flag_post", "flag_post"]), tolerance = 1e-7)
})
