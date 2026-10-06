source(file.path("..", "..", "R", "lal.R"))
source(file.path("..", "..", "R", "lazic.R"))

test_that("absolute changes use the Welch variance and degrees of freedom", {
  changes <- data.frame(flag = c(1, 1, 1, 0, 0, 0, 0), change = c(1, 2, 9, 2, 3, 3, 4))
  got <- lazic_absolute(changes, "test")
  expected <- t.test(changes$change[changes$flag == 1], changes$change[changes$flag == 0])
  expect_equal(got$estimate, 1)
  expect_equal(got$df, unname(expected$parameter))
  expect_equal(c(got$lower, got$upper), unname(expected$conf.int[1:2]))
})

test_that("missing citation years cannot be silently averaged", {
  panel <- expand.grid(article_id = c("a", "b"), year = c(2016L, 2019L))
  panel$flagged <- rep(c(1L, 0L), 2)
  panel$citations <- c(1, 2, 5, 3)
  panel$status <- "complete"
  changes <- lazic_changes(panel)
  expect_equal(changes$change[match(c("a", "b"), changes$paper_id)], c(4, 1))
  expect_error(lazic_changes(panel[-1L, ]))
  other <- panel[1L, ]
  other$article_id <- "c"
  other$year <- 2017L
  expect_error(lazic_changes(rbind(panel, other)))
  panel$citations[1] <- NA
  expect_error(lazic_changes(panel))
})

test_that("whole-paper bootstrap preserves paired periods", {
  changes <- data.frame(flag = rep(0:1, each = 3), before = c(2, 4, 8, 1, 3, 7))
  changes$after <- changes$before + ifelse(changes$flag == 1, 3, 1)
  got <- lazic_bootstrap(changes, repetitions = 100L)
  expect_equal(rownames(got), c("absolute", "log_ratio"))
  expect_equal(unname(got["absolute", c("lower", "upper")]), c(2, 2))
  expect_true(all(got[, "finite_draws"] == 100L))
})
