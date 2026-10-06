i4r_weighted_median <- function(values, weights) {
  if (
    !length(values) || length(values) != length(weights) ||
      any(!is.finite(values)) || any(!is.finite(weights)) || any(weights <= 0)
  ) {
    stop("Invalid weighted-median inputs")
  }
  ordered <- order(values)
  values <- values[ordered]
  cumulative <- cumsum(weights[ordered]) / sum(weights)
  boundary <- which(cumulative >= 0.5 - 1e-12)[1]
  if (abs(cumulative[boundary] - 0.5) <= 1e-12 && boundary < length(values)) {
    return(mean(values[c(boundary, boundary + 1L)]))
  }
  values[boundary]
}

i4r_direct <- function(panel) {
  splits <- split(panel, panel$stack_id)
  contrasts <- vapply(splits, function(s) {
    treated <- s[s$treated == 1, ]
    controls <- s[s$treated == 0, ]
    sum(treated$citations * ifelse(treated$post == 1, 1, -1)) -
      sum(
        controls$citations * controls$weight * ifelse(controls$post == 1, 1, -1)
      )
  }, numeric(1))
  mean(contrasts)
}

i4r_estimate <- function(panel) {
  if (!nrow(panel)) stop("No complete matched panels")
  if (length(unique(panel$horizon)) != 1L) stop("Estimate one horizon at a time")
  if (anyDuplicated(panel[c("stack_id", "article_id", "post")])) {
    stop("Duplicate article-period within stack")
  }
  counts <- table(interaction(panel$stack_id, panel$article_id, drop = TRUE))
  if (any(counts != 2)) stop("Incomplete two-period panel")
  if (
    any(!is.finite(panel$citations)) || any(panel$citations < 0) ||
      any(!is.finite(panel$weight)) || any(panel$weight <= 0) ||
      !all(panel$treated %in% c(0, 1))
  ) {
    stop("Invalid outcomes or weights")
  }
  for (stack in split(panel, panel$stack_id)) {
    if (length(unique(stack$warning_id)) != 1L) stop("Inconsistent stack warning")
    for (period in split(stack, stack$post)) {
      if (
        sum(period$treated == 1) != 1L ||
          abs(sum(period$weight[period$treated == 1]) - 1) > 1e-8 ||
          abs(sum(period$weight[period$treated == 0]) - 1) > 1e-8
      ) {
        stop("Stack must have one treated article and unit weight per group")
      }
    }
  }
  pairs <- split(panel, interaction(panel$stack_id, panel$article_id, drop = TRUE))
  differences <- do.call(rbind, lapply(pairs, function(x) {
    if (
      !setequal(x$post, c(0, 1)) || length(unique(x$weight)) != 1L ||
        length(unique(x$treated)) != 1L || length(unique(x$warning_id)) != 1L
    ) {
      stop("Inconsistent article-period attributes")
    }
    row <- x[x$post == 1, ]
    row$change <- x$citations[x$post == 1] - x$citations[x$post == 0]
    row
  }))
  if (length(unique(differences$change)) == 1L) {
    return(data.frame(
      horizon = unique(panel$horizon), articles = length(unique(panel$article_id)),
      affected_articles = length(unique(panel$article_id[panel$treated == 1])),
      disclosure_events = length(unique(panel$warning_id)), estimate = i4r_direct(panel),
      standard_error = NA_real_, lower = NA_real_, upper = NA_real_,
      inference = "unavailable: no variation in observed citation changes"
    ))
  }
  model <- fixest::feols(
    change ~ treated | stack_id,
    data = differences, weights = ~weight, vcov = "iid", notes = FALSE
  )
  direct <- i4r_direct(panel)
  if (abs(unname(stats::coef(model)["treated"]) - direct) > 1e-7) {
    stop("Regression does not equal the declared matched contrast")
  }
  warnings <- length(unique(panel$warning_id))
  articles <- length(unique(panel$article_id))
  lower <- upper <- se <- NA_real_
  inference <- "unavailable: fewer than two independent disclosure events"
  if (warnings >= 2L && articles >= 2L) {
    summary_model <- summary(
      model,
      vcov = ~ article_id + warning_id,
      ssc = fixest::ssc(
        K.adj = TRUE, K.fixef = "nonnested", G.adj = TRUE,
        G.df = "min", t.df = "min"
      )
    )
    se <- unname(summary_model$se["treated"])
    critical <- stats::qt(0.975, min(warnings, articles) - 1)
    lower <- direct - critical * se
    upper <- direct + critical * se
    inference <- "two-way article/disclosure clusters, conditional on matches"
    if (!is.finite(se) || !is.finite(lower) || !is.finite(upper)) {
      se <- lower <- upper <- NA_real_
      inference <- "unavailable: nonfinite clustered variance or degrees of freedom"
    }
  }
  data.frame(
    horizon = unique(panel$horizon), articles = articles,
    affected_articles = length(unique(panel$article_id[panel$treated == 1])),
    disclosure_events = warnings, estimate = direct, standard_error = se,
    lower = lower, upper = upper, inference = inference
  )
}
