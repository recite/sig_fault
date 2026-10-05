results <- readRDS("data/derived/results.rds")
m <- results$metrics
fmt <- function(x) unname(formatC(x, format = "f", digits = 1))
interval <- function(x) paste0("[", fmt(x$lower), ", ", fmt(x$upper), "]")
write_table <- function(header, rows, alignment, path) {
  writeLines(c(
    paste0("\\begin{tabular}{", alignment, "}"), "\\toprule",
    paste0(paste(header, collapse = " & "), " \\\\"), "\\midrule",
    apply(rows, 1, function(row) paste0(paste(row, collapse = " & "), " \\\\")),
    "\\bottomrule", "\\end{tabular}"
  ), path)
}
levels <- m$levels
write_table(
  c("Article group", "Papers", "2010", "2012--2015", "Change"),
  rbind(
    c("Flagged", m$flagged, fmt(levels$before[2]), fmt(levels$after[2]), fmt(levels$change[2])),
    c(
      "Comparison", m$comparison,
      fmt(levels$before[1]), fmt(levels$after[1]), fmt(levels$change[1])
    )
  ), "lrrrr", "tabs/levels.tex"
)
e <- results$estimates
write_table(
  c("Comparison", "Flagged / other", "Difference", "95\\% interval"),
  cbind(
    e$specification, paste(e$n_flagged, e$n_comparison, sep = " / "),
    fmt(e$estimate), interval(e)
  ), "p{7.0cm}rrr", "tabs/estimates.tex"
)
write_table(
  c("Recorded status", "Citation relationships"),
  as.matrix(results$coding_counts), "lr", "tabs/coding.tex"
)
macros <- c(
  Classified = m$classified, ClassifiedFlagged = m$classified_flagged,
  ClassifiedComparison = m$classified - m$classified_flagged,
  Covered = m$covered, Analyzed = m$analyzed, Flagged = m$flagged,
  Comparison = m$comparison, Serious = m$serious, ZeroYears = m$zero_years,
  Records = format(m$records, big.mark = ",", trim = TRUE), Repaired = m$repaired,
  Duplicates = m$duplicates, FalseLinks = m$false_links,
  Prepublication = m$prepublication_records,
  MainEstimate = fmt(m$main$estimate), MainLower = fmt(m$main$lower), MainUpper = fmt(m$main$upper),
  MainLoss = fmt(abs(m$main$lower)),
  MainInterval = interval(m$main), FlaggedBefore = fmt(levels$before[2]),
  FlaggedAfter = fmt(levels$after[2]), ComparisonBefore = fmt(levels$before[1]),
  ComparisonAfter = fmt(levels$after[1]), FlaggedChange = fmt(levels$change[2]),
  ComparisonChange = fmt(levels$change[1]),
  AdjustedEstimate = fmt(e$estimate[2]), AdjustedInterval = interval(e[2, ]),
  InclusiveEstimate = fmt(e$estimate[3]), InclusiveInterval = interval(e[3, ]),
  SeriousEstimate = fmt(e$estimate[10]), SeriousInterval = interval(e[10, ]),
  PretrendEstimate = fmt(e$estimate[11]), PretrendInterval = interval(e[11, ]),
  BootstrapLower = fmt(m$bootstrap[1]), BootstrapUpper = fmt(m$bootstrap[2]),
  BootstrapDraws = format(m$bootstrap_draws, big.mark = ",", trim = TRUE),
  BootstrapSeed = m$bootstrap_seed,
  LeaveMin = fmt(m$leave_one_out[1]), LeaveMax = fmt(m$leave_one_out[2]),
  SharedPercent = fmt(m$citing_overlap_percent),
  CodingN = m$coding_n, Rated = m$rated, Ack = m$acknowledgment,
  Nonack = m$nonacknowledgment, AckPercent = fmt(m$acknowledgment_percent),
  AckLower = fmt(m$acknowledgment_ci[1]), AckUpper = fmt(m$acknowledgment_ci[2]),
  AckBoundLower = fmt(m$acknowledgment_bounds[1]), AckBoundUpper = fmt(m$acknowledgment_bounds[2]),
  Uncoded = m$coding_uncoded, Unavailable = m$coding_unavailable,
  CodingFalse = m$coding_false, PartialYear = m$coding_partial_year
)
stopifnot(all(grepl("^[A-Za-z]+$", names(macros))), !anyDuplicated(names(macros)))
writeLines(paste0("\\newcommand{\\", names(macros), "}{", macros, "}"), "tabs/macros.tex")
readme <- paste(readLines("docs/README.in.md"), collapse = "\n")
for (name in names(macros)) {
  readme <- gsub(paste0("{{", name, "}}"), macros[[name]], readme, fixed = TRUE)
}
stopifnot(!grepl("{{", readme, fixed = TRUE))
writeLines(readme, "README.md")
