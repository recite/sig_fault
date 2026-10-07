design_characteristics <- function(classification) {
  x <- classification
  original <- tolower(trimws(x$animal))
  x$species <- "other"
  x$species[original %in% c("human", "humans")] <- "human"
  x$species[original == "mice"] <- "mouse"
  x$species[original %in% c("rat", "rats")] <- "rat"
  x$species[original %in% c("monkey", "monkeys")] <- "primate"
  x$species[original == ""] <- "unknown"
  x$subject_type <- ifelse(x$species == "human", "human",
    ifelse(x$species == "unknown", "unknown", "nonhuman")
  )
  stopifnot(all(x$within_between_ss %in% c("within", "between")))
  for (species in c("human", "mouse", "rat", "primate", "other", "unknown")) {
    x[[paste0("species_", species)]] <- as.integer(x$species == species)
  }
  x$between <- as.integer(x$within_between_ss == "between")
  x$country_us <- as.integer(trimws(x$country_authors) == "US")
  x$country_unknown <- as.integer(trimws(x$country_authors) == "")
  x
}

design_balance <- function(baseline, variables, supported, reference) {
  x <- baseline[baseline$article_id %in% supported$papers$article_id, ]
  x$weight <- supported$papers$weight[match(x$article_id, supported$papers$article_id)]
  do.call(rbind, lapply(variables, function(name) {
    treated <- reference[[name]][reference$flag == 1L]
    comparison <- reference[[name]][reference$flag == 0L]
    scale <- sqrt((var(treated) + var(comparison)) / 2)
    means <- vapply(0:1, function(flag) {
      g <- x[x$flag == flag, ]
      weighted.mean(g[[name]], g$weight)
    }, numeric(1))
    data.frame(
      variable = name, flagged_mean = means[2], comparison_mean = means[1],
      difference = means[2] - means[1], reference_sd = scale,
      standardized_difference = if (scale > 0) (means[2] - means[1]) / scale else NA_real_
    )
  }))
}

equal_flagged_change <- function(panel, stratum_columns = c("journal", "cohort")) {
  support <- journal_cohort_support(panel, stratum_columns)
  m <- support$papers[support$papers$supported, ]
  pre <- panel[panel$year == 2010L, ]
  post <- aggregate(citations ~ article_id, panel[panel$year %in% 2012:2015, ], mean)
  years <- panel[panel$year %in% c(2010L, 2012:2015) & panel$article_id %in% m$article_id, ]
  stopifnot(all(table(years$article_id) == 5L))
  m$before <- pre$citations[match(m$article_id, pre$article_id)]
  m$after <- post$citations[match(m$article_id, post$article_id)]
  stopifnot(!anyNA(m[c("before", "after")]))
  m$change <- m$after - m$before
  index <- match(m$stratum, support$strata$stratum)
  m$computation_weight <- with(support$strata, (flagged + comparison) / comparison)[index]
  m$outcome_weight <- ifelse(m$flag == 1L, 1, -m$weight) / sum(m$flag)
  direct <- sum(m$outcome_weight * m$change)
  fit <- lm(change ~ flag + factor(stratum), data = m, weights = computation_weight)
  stopifnot(fit$rank == ncol(model.matrix(fit)))
  b <- unname(coef(fit)["flag"])
  stopifnot(abs(b - direct) < 1e-8)
  variance <- sandwich::vcovHC(fit, type = "HC3")["flag", "flag"]
  se <- sqrt(variance)
  df <- df.residual(fit)
  matrix <- model.matrix(fit)
  bread <- solve(crossprod(matrix, matrix * m$computation_weight))
  scores <- matrix * (m$computation_weight * residuals(fit) / (1 - hatvalues(fit)))
  influence <- drop(scores %*% bread[, "flag"])
  stopifnot(abs(sum(influence^2) - variance) < 1e-8)
  m$leverage <- unname(hatvalues(fit))
  m$variance_share <- influence^2 / variance
  list(
    estimate = data.frame(
      n_flagged = sum(m$flag), n_comparison = sum(m$flag == 0L),
      estimate = b, se = se, df = df,
      lower = b - qt(.975, df) * se, upper = b + qt(.975, df) * se,
      max_leverage = max(m$leverage), top_variance_share = max(m$variance_share),
      single_control_cells = sum(support$strata$comparison == 1L & support$strata$supported),
      single_flagged_cells = sum(support$strata$flagged == 1L & support$strata$supported)
    ),
    papers = m
  )
}

design_information <- function(model_result) {
  x <- model_result$panel
  x$fitted_mean <- fitted(model_result$model)
  x$group_year <- interaction(x$stratum, x$year, drop = TRUE)
  residual_model <- lm(flag_post ~ factor(article_id) + group_year,
    data = x, weights = fitted_mean
  )
  x$information <- x$fitted_mean * residuals(residual_model)^2
  information <- aggregate(information ~ stratum, x, sum)
  information$information_share <- information$information / sum(information$information)
  information
}
