lal_subset <- function(panel, diagnostic, pre = 2023L, post = 2025L) {
  stopifnot(!length(intersect(pre, post)), diagnostic %in% names(panel))
  x <- panel[panel$citation_year %in% c(pre, post) & panel$publication_year < min(pre), ]
  if (diagnostic %in% c("sensitive", "ar_loss")) x <- x[x$analytic_positive == 1L, ]
  stopifnot(!anyDuplicated(x[c("paper_id", "citation_year")]))
  stopifnot(all(table(x$paper_id) == length(c(pre, post))))
  x$flag <- x[[diagnostic]]
  x$post <- as.integer(x$citation_year %in% post)
  x$flag_post <- x$flag * x$post
  stopifnot(length(unique(x$flag)) == 2L, !anyNA(x$citations))
  x
}

lal_ppml <- function(x, label, effects = "basic", outcome = "citations") {
  x$count <- x[[outcome]]
  requested <- unique(x$paper_id)
  fixed <- switch(effects,
    basic = "paper_id + citation_year",
    journal = "paper_id + journal^citation_year",
    cohort = "paper_id + publication_year^citation_year",
    stop("Unknown effects")
  )
  correction <- fixest::ssc(
    K.adj = TRUE, K.fixef = "nonnested", K.exact = FALSE,
    G.adj = TRUE, G.df = "min", t.df = "min"
  )
  model <- fixest::fepois(
    as.formula(paste("count ~ flag_post |", fixed)), x,
    vcov = fixest::vcov_cluster(cluster = ~paper_id, vcov_fix = FALSE), ssc = correction,
    glm.tol = 1e-10, fixef.tol = 1e-10, nthreads = 1
  )
  stopifnot(isTRUE(model$convStatus), "flag_post" %in% names(coef(model)))
  used <- x[fixest::obs(model), ]
  meta <- unique(used[c("paper_id", "flag")])
  b <- unname(coef(model)["flag_post"])
  se <- sqrt(vcov(model)["flag_post", "flag_post"])
  df <- nrow(meta) - 1L
  data.frame(
    specification = label, n_flagged = sum(meta$flag), n_comparison = sum(meta$flag == 0),
    observations = nrow(used), estimate = b, se = se, df = df,
    percent = 100 * expm1(b),
    lower = 100 * expm1(b - qt(.975, df) * se),
    upper = 100 * expm1(b + qt(.975, df) * se),
    excluded_papers = paste(setdiff(requested, meta$paper_id), collapse = ";"),
    stringsAsFactors = FALSE
  )
}

lal_changes <- function(x) {
  values <- aggregate(citations ~ paper_id + flag + post, x, mean)
  before <- values[values$post == 0L, c("paper_id", "flag", "citations")]
  after <- values[values$post == 1L, c("paper_id", "citations")]
  before$after <- after$citations[match(before$paper_id, after$paper_id)]
  names(before)[names(before) == "citations"] <- "before"
  before$change <- before$after - before$before
  stopifnot(!anyNA(before), !anyDuplicated(before$paper_id))
  before
}

lal_absolute <- function(x, label) {
  changes <- lal_changes(x)
  fit <- lm(change ~ flag, changes)
  b <- unname(coef(fit)["flag"])
  se <- sqrt(sandwich::vcovHC(fit, type = "HC3")["flag", "flag"])
  df <- df.residual(fit)
  data.frame(
    specification = label, n_flagged = sum(changes$flag),
    n_comparison = sum(changes$flag == 0L), estimate = b, se = se, df = df,
    lower = b - qt(.975, df) * se, upper = b + qt(.975, df) * se
  )
}
