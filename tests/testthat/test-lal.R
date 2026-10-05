source(file.path(root, "R/lal.R"))

test_that("Lal PPML equals the independently calculated two-period growth ratio", {
  dat <- expand.grid(paper_id = paste0("p", 1:12), citation_year = c(2023L, 2025L))
  dat$publication_year <- 2018L
  dat$journal <- "J"
  dat$weak <- as.integer(as.integer(sub("p", "", dat$paper_id)) > 6L)
  dat$citations <- c(2:13, 3, 5, 5, 8, 8, 8, 14, 17, 16, 19, 18, 22)
  x <- lal_subset(dat, "weak")
  means <- tapply(x$citations, list(x$flag, x$post), mean)
  expected <- log(means[2, 2] / means[2, 1]) - log(means[1, 2] / means[1, 1])
  result <- lal_ppml(x, "Synthetic")
  expect_equal(result$estimate, expected, tolerance = 1e-8)
  difference <- (means[2, 2] - means[2, 1]) - (means[1, 2] - means[1, 1])
  expect_equal(lal_absolute(x, "Synthetic")$estimate, difference, tolerance = 1e-10)
  expect_error(lal_subset(dat[-1, ], "weak"))
})

test_that("Lal reported primary results use article and review counts", {
  panel <- read.csv(file.path(root, "data/lal/panel.csv"))
  edges <- read.csv(file.path(root, "data/lal/citation_edges.csv"))
  keep <- edges$type %in% c("article", "review") & edges$duplicate_of == "" &
    edges$citing_work_id != edges$target_work_id & edges$publication_year %in% c(2023, 2025)
  edges <- edges[keep, ]
  expected <- table(edges$paper_id, edges$publication_year)
  actual <- panel[panel$citation_year %in% c(2023, 2025), ]
  for (i in seq_len(nrow(actual))) {
    r <- actual[i, ]
    n <- if (r$paper_id %in% rownames(expected)) {
      as.integer(expected[r$paper_id, as.character(r$citation_year)])
    } else {
      0L
    }
    expect_equal(r$citations, n)
  }
  estimates <- read.csv(file.path(root, "data/lal/estimates.csv"))
  for (diagnostic in c("weak", "sensitive", "screen", "ar_loss")) {
    x <- lal_subset(panel, diagnostic)
    totals <- tapply(x$citations, list(x$flag, x$post), sum)
    expected <- log(totals[2, 2] / totals[2, 1]) - log(totals[1, 2] / totals[1, 1])
    keep <- estimates$diagnostic == diagnostic & estimates$specification == "2023 to 2025"
    row <- estimates[keep, ]
    expect_equal(row$estimate, expected, tolerance = 1e-8)
  }
})
