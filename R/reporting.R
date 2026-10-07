format_number <- function(x, digits = 1L) {
  stopifnot(is.numeric(x), all(is.finite(x)), digits >= 0L)
  unname(formatC(x, format = "f", digits = digits, big.mark = ",", decimal.mark = "."))
}

format_count <- function(x) {
  stopifnot(is.numeric(x), all(is.finite(x)), all(x == trunc(x)))
  format_number(x, digits = 0L)
}
