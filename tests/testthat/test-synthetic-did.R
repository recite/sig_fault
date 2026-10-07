source(file.path("..", "..", "R", "synthetic_did.R"))

sdid_fixture <- function() {
  set.seed(51)
  y <- matrix(rpois(24 * 7, 12), 24, 7)
  y[17:24, 5:7] <- y[17:24, 5:7] + 6
  list(y = y, n0 = 16L, t0 = 4L, years = 2010:2016)
}

test_that("synthetic DiD uses held-out treated outcomes only in the effect", {
  setup <- sdid_fixture()
  fitted <- sdid_fit(setup)
  changed <- setup
  changed$y[17:24, 5:7] <- changed$y[17:24, 5:7] + 100
  second <- sdid_fit(changed)
  expect_equal(as.numeric(second$fit - fitted$fit), 100, tolerance = 1e-8)
  expect_equal(attr(second$fit, "weights"), attr(fitted$fit, "weights"))
  expect_lt(fitted$diagnostics$identity_error, 1e-8)
  expect_equal(mean(tail(fitted$paths$gap, 3)), as.numeric(fitted$fit))
})

test_that("recorded bootstrap reproduces the official refitted-weight variance", {
  fit <- sdid_fit(sdid_fixture())$fit
  draws <- sdid_bootstrap(fit, 25L, 67L)
  set.seed(67)
  official <- sqrt(as.numeric(vcov(fit, method = "bootstrap", replications = 25L)))
  expect_equal(draws$se, official, tolerance = 1e-10)
  expect_equal(nrow(draws$draws), 25L)
  expect_equal(nrow(draws$indices), 25L)
  expect_true(all(lengths(strsplit(draws$indices$indices, ";", fixed = TRUE)) == 24L))
})

test_that("equal-paper DiD agrees with an explicit balanced fixed-effects regression", {
  setup <- sdid_fixture()
  panel <- expand.grid(article = seq_len(24), year = seq_len(7))
  panel$outcome <- as.vector(setup$y)
  panel$exposure <- as.integer(panel$article > 16 & panel$year > 4)
  fit <- lm(outcome ~ exposure + factor(article) + factor(year), panel)
  expect_equal(sdid_did(setup)$estimate, unname(coef(fit)["exposure"]), tolerance = 1e-8)
})

test_that("panel construction rejects missing years and prepublication baselines", {
  panel <- expand.grid(article_id = letters[1:4], year = 2010:2013, stringsAsFactors = FALSE)
  panel$citations <- 2
  panel$status <- "complete"
  roster <- data.frame(article_id = letters[1:4], flag = c(0, 0, 1, 1), publication_year = 2009L)
  setup <- sdid_matrix(panel, roster, 2010:2012, 2013L)
  expect_equal(dim(setup$y), c(4L, 4L))
  expect_error(sdid_matrix(panel[-1, ], roster, 2010:2012, 2013L))
  roster$publication_year[1] <- 2010L
  expect_error(sdid_matrix(panel, roster, 2010:2012, 2013L))
})
