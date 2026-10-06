bridge_changes <- function(panel, post = 2012:2015,
                           sources = c("wos", "openalex", "openalex_broad")) {
  years <- c(2010L, post)
  stopifnot(length(post) > 0L, !anyDuplicated(years), !anyNA(panel$article_id))
  x <- panel[panel$year %in% years, ]
  stopifnot(!anyDuplicated(x[c("article_id", "year")]))
  meta <- unique(x[c("article_id", "flag", "cohort", "journal")])
  stopifnot(!anyDuplicated(meta$article_id), !anyNA(meta), all(meta$flag %in% 0:1))
  groups <- split(x, x$article_id)
  complete <- vapply(groups, function(g) {
    setequal(g$year, years) && all(g$status == "complete")
  }, logical(1))
  x <- x[x$article_id %in% names(groups)[complete], ]
  stopifnot(!anyNA(x[sources]))
  counts <- as.matrix(x[sources])
  stopifnot(all(is.finite(counts)), all(counts >= 0), all(counts == floor(counts)))
  result <- meta[meta$article_id %in% x$article_id, ]
  result <- result[order(result$article_id), ]
  for (source in sources) {
    before <- x[x$year == 2010L, c("article_id", source)]
    after <- vapply(
      split(x[x$year %in% post, source], x$article_id[x$year %in% post]), mean, numeric(1)
    )
    matched <- match(result$article_id, before$article_id)
    result[[paste0(source, "_before")]] <- before[[source]][matched]
    result[[paste0(source, "_after")]] <- unname(after[as.character(result$article_id)])
  }
  result
}

bridge_contrasts <- function(x, source) {
  if (!all(0:1 %in% x$flag)) {
    return(c(absolute = NA_real_, log_ratio = NA_real_))
  }
  before <- vapply(0:1, function(g) mean(x[[paste0(source, "_before")]][x$flag == g]), numeric(1))
  after <- vapply(0:1, function(g) mean(x[[paste0(source, "_after")]][x$flag == g]), numeric(1))
  c(
    absolute = (after[2] - before[2]) - (after[1] - before[1]),
    log_ratio = if (all(c(before, after) > 0)) {
      log(after[2] / before[2]) - log(after[1] / before[1])
    } else {
      NA_real_
    }
  )
}

bridge_comparison <- function(x, source, draws = 9999L, seed = 20261006L) {
  stopifnot(
    source != "wos", all(paste0(source, c("_before", "_after")) %in% names(x)),
    draws >= 2L, draws == as.integer(draws)
  )
  n <- tabulate(x$flag + 1L, nbins = 2L)
  left <- bridge_contrasts(x, "wos")
  right <- bridge_contrasts(x, source)
  result <- data.frame(
    source = source, estimand = names(left), n_flagged = n[2], n_comparison = n[1],
    wos = unname(left), alternative = unname(right), difference = unname(right - left),
    se = NA_real_, lower = NA_real_, upper = NA_real_,
    bootstrap_draws = 0L, undefined_draws = 0L, seed = seed,
    status = if (any(n == 0L)) {
      "missing_group"
    } else if (any(n < 2L)) {
      "insufficient_papers"
    } else {
      "complete"
    }
  )
  if (any(n < 2L)) {
    return(result)
  }
  set.seed(seed)
  indices <- lapply(0:1, function(g) which(x$flag == g))
  boot <- replicate(draws, {
    selected <- unlist(lapply(indices, function(i) {
      i[sample.int(length(i), length(i), replace = TRUE)]
    }))
    sampled <- x[selected, ]
    bridge_contrasts(sampled, source) - bridge_contrasts(sampled, "wos")
  })
  result$bootstrap_draws <- draws
  result$undefined_draws <- rowSums(!is.finite(boot))
  for (i in seq_len(nrow(result))) {
    if (!is.finite(result$difference[i])) {
      result$status[i] <- "undefined_point_estimate"
    } else if (result$undefined_draws[i] > 0L) {
      result$status[i] <- "undefined_bootstrap_draws"
    } else {
      result$se[i] <- sd(boot[i, ])
      result[i, c("lower", "upper")] <- quantile(boot[i, ], c(.025, .975), names = FALSE)
    }
  }
  result
}
