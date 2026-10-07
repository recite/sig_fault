equal_audit_synthesis <- function(x) {
  stopifnot(
    nrow(x) >= 2L, !anyDuplicated(x$audit),
    all(is.finite(x$estimate)), all(is.finite(x$se)), all(x$se > 0),
    all(is.finite(x$df)), all(x$df > 0)
  )
  weight <- rep(1 / nrow(x), nrow(x))
  component_variance <- (weight * x$se)^2
  estimate <- sum(weight * x$estimate)
  variance <- sum(component_variance)
  df <- variance^2 / sum(component_variance^2 / x$df)
  se <- sqrt(variance)
  critical <- qt(.975, df)
  data.frame(
    audits = nrow(x), estimate = estimate, se = se, df = df,
    percent = 100 * expm1(estimate),
    lower = 100 * expm1(estimate - critical * se),
    upper = 100 * expm1(estimate + critical * se)
  )
}

precision_synthesis <- function(x, random = FALSE) {
  stopifnot(
    nrow(x) >= 2L, !anyNA(x$audit), !anyDuplicated(x$audit),
    all(nzchar(x$audit)), all(is.finite(x$estimate)),
    all(is.finite(x$se)), all(x$se > 0)
  )
  fit <- metafor::rma.uni(
    yi = x$estimate, sei = x$se,
    method = if (random) "REML" else "FE",
    test = if (random) "adhoc" else "z"
  )
  df <- if (random) nrow(x) - 1L else Inf
  critical <- if (random) qt(.95, df) else qnorm(.95)
  data.frame(
    audits = nrow(x), estimate = as.numeric(coef(fit)), se = fit$se, df = df,
    percent = 100 * expm1(as.numeric(coef(fit))),
    lower = 100 * expm1(fit$ci.lb), upper = 100 * expm1(fit$ci.ub),
    lower_one_sided_95 = 100 * expm1(as.numeric(coef(fit)) - critical * fit$se),
    tau2 = fit$tau2, q = fit$QE, q_df = nrow(x) - 1L, q_p = fit$QEp, i2 = fit$I2
  )
}
