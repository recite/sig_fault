source(file.path(root, "R/cohorts.R"))

test_that("cohort metadata joins preserve repeated claims and original row order", {
  left <- data.frame(id = c("b", "a", "b"), claim = 1:3)
  right <- data.frame(id = c("a", "b"), doi = c("10/a", "10/b"))
  actual <- cohort_join(left, right, "id")
  expect_equal(actual$claim, 1:3)
  expect_equal(actual$doi, c("10/b", "10/a", "10/b"))
  expect_error(cohort_join(left, rbind(right, right[1, ]), "id"))
  expect_error(cohort_join(left, right[1, ], "id"))
  expect_error(cohort_join(left, transform(right, claim = 0), "id"))
})

test_that("native missing and mixed outcomes remain distinct", {
  x <- cohort_assessments(c("a", "a", "b"), 1:3, "diagnostic", c("", "0", "main effect"), "source")
  expect_equal(x$source_outcome, c("", "0", "main effect"))
  expect_equal(x$paper_id, c("a", "a", "b"))
})
