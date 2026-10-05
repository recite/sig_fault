test_that("classification joins preserve the intended source papers", {
  classification <- read_classification(root)
  expect_equal(nrow(classification), 157L)
  expect_equal(sum(classification$flag), 79L)
  expect_false(anyDuplicated(classification$article_id) > 0L)
  raw <- read_derived("raw")
  expect_equal(sort(setdiff(classification$article_id, raw$article_id)), c(95L, 124L))
  expect_identical(raw$flag, classification$flag[match(raw$article_id, classification$article_id)])
})

test_that("malformed export fields are recovered without dropping a citation", {
  expect_equal(
    repair_export_row(c("title\tjournal\t2009", "", "")),
    c("title", "journal", "2009")
  )
  expect_error(repair_export_row(c("title\tjournal", "not empty")))
  raw <- read_derived("raw")
  repaired <- raw[raw$repaired, ]
  expect_equal(nrow(repaired), 1L)
  expect_equal(repaired$article_id, 146L)
  expect_equal(repaired$doi, "10.1073/pnas.0905549106")
  expect_equal(repaired$year, 2009L)
  expect_equal(repaired$accession, "WOS:000269806600087")
})

test_that("deduplication counts citing relationships rather than global documents", {
  raw <- read_derived("raw")
  expect_equal(nrow(raw), 16437L)
  expect_equal(sum(raw$duplicate), 15L)
  unique_edges <- raw[!raw$duplicate, ]
  expect_equal(anyDuplicated(unique_edges[c("article_id", "key")]), 0L)
  expect_gt(anyDuplicated(unique_edges$key), 0L)
  expect_equal(sum(raw$false_link), 2L)
  expect_setequal(raw$article_id[raw$before_target_year], c(23L, 25L))
  expect_setequal(raw$article_id[raw$is_target_itself], c(23L, 25L))
})

test_that("zero completion never substitutes zeros for missing whole histories", {
  panel <- read_derived("panel")
  expect_equal(nrow(panel), 153L * 7L)
  expect_equal(anyDuplicated(panel[c("article_id", "year")]), 0L)
  expect_false(any(panel$article_id %in% c(23L, 25L, 95L, 124L)))
  expect_true(all(table(panel$article_id) == 7L))
  expect_equal(sum(panel$citations == 0L & panel$year >= 2010L), 29L)
  expect_true(all(panel$citations >= 0L & panel$citations == as.integer(panel$citations)))
  raw <- read_derived("raw")
  use <- !raw$duplicate & !raw$false_link &
    raw$article_id %in% panel$article_id & raw$year %in% panel$year
  retained <- raw[use, ]
  expect_equal(sum(panel$citations), nrow(retained))
  classification <- read_classification(root)
  expect_error(make_panel(classification, raw, 95L))
})

test_that("missing codes and false matches are not counted as ordinary citations", {
  coding <- read_coding(root)
  expect_equal(nrow(coding), 100L)
  expect_equal(sum(coding$status == "No concern recorded"), 95L)
  expect_equal(sum(coding$status == "Concern recorded"), 1L)
  expect_equal(sum(coding$status == "Uncoded"), 1L)
  expect_equal(sum(coding$status == "Article unavailable"), 1L)
  expect_equal(sum(coding$status == "False citation link"), 2L)
  expect_equal(sum(coding$year == 2016L), 7L)
  expect_false(anyNA(coding$status))
})
