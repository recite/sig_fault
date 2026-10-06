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
