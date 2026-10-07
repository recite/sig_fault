source("R/reporting.R")
results <- readRDS("data/derived/results.rds")
m <- results$metrics
fmt <- function(x) format_number(x, digits = 1L)
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
    c(
      "Flagged", format_count(m$flagged),
      fmt(levels$before[2]), fmt(levels$after[2]), fmt(levels$change[2])
    ),
    c(
      "Comparison", format_count(m$comparison),
      fmt(levels$before[1]), fmt(levels$after[1]), fmt(levels$change[1])
    )
  ), "lrrrr", "tabs/levels.tex"
)
e <- results$estimates
write_table(
  c("Comparison", "Flagged / other", "Difference", "95\\% interval"),
  cbind(
    sub("Later window:", "Post period:", e$specification),
    paste(format_count(e$n_flagged), format_count(e$n_comparison), sep = " / "),
    fmt(e$estimate), interval(e)
  ), "p{7.0cm}rrr", "tabs/estimates.tex"
)
write_table(
  c("Recorded status", "Citation relationships"),
  cbind(results$coding_counts[[1]], format_count(results$coding_counts[[2]])),
  "lr", "tabs/coding.tex"
)
q <- results$proportional
write_table(
  c("Specification", "Flagged / other", "Change (\\%)", "95\\% interval", "Lower bound"),
  cbind(
    q$specification, paste(format_count(q$n_flagged), format_count(q$n_comparison), sep = " / "),
    fmt(q$percent), paste0("[", fmt(q$percent_lower), ", ", fmt(q$percent_upper), "]"),
    fmt(q$percent_lower_one_sided)
  ), "p{5.5cm}rrrr", "tabs/proportional.tex"
)
p <- m$main
d <- m$descriptive
macros <- c(
  ProportionalEstimate = fmt(p$percent),
  ProportionalReduction = fmt(-p$percent),
  ProportionalLower = fmt(p$percent_lower),
  ProportionalUpper = fmt(p$percent_upper),
  ProportionalBound = fmt(-p$percent_lower_one_sided),
  ProportionalRatio = unname(formatC(p$ratio, format = "f", digits = 3)),
  ProportionalBootLower = fmt(m$proportional_bootstrap$percent_ci[1]),
  ProportionalBootUpper = fmt(m$proportional_bootstrap$percent_ci[2]),
  ProportionalBootBound = fmt(-m$proportional_bootstrap$percent_lower_one_sided),
  AdjustedPercentMin = fmt(min(q$percent[2:4])),
  AdjustedPercentMax = fmt(max(q$percent[2:4])),
  AdjustedBoundMin = fmt(min(-q$percent_lower_one_sided[2:4])),
  AdjustedBoundMax = fmt(max(-q$percent_lower_one_sided[2:4])),
  MedianFlaggedBefore = d$flagged_median_before,
  MedianComparisonBefore = d$comparison_median_before,
  MedianFlaggedMin = d$flagged_median_post_range[1],
  MedianFlaggedMax = d$flagged_median_post_range[2],
  MedianComparisonMin = d$comparison_median_post_range[1],
  MedianComparisonMax = d$comparison_median_post_range[2],
  IncreasedFlagged = format_count(d$flagged_increased),
  IncreasedComparison = format_count(d$comparison_increased),
  IncreasedPercent = unname(formatC(d$flagged_increased_percent, format = "f", digits = 0)),
  Classified = format_count(m$classified),
  ClassifiedFlagged = format_count(m$classified_flagged),
  ClassifiedComparison = format_count(m$classified - m$classified_flagged),
  Covered = format_count(m$covered),
  Analyzed = format_count(m$analyzed),
  Flagged = format_count(m$flagged),
  Comparison = format_count(m$comparison),
  Serious = format_count(m$serious),
  ZeroYears = format_count(m$zero_years),
  Records = format_count(m$records),
  Repaired = format_count(m$repaired),
  Duplicates = format_count(m$duplicates),
  FalseLinks = format_count(m$false_links),
  Prepublication = format_count(m$prepublication_records),
  MainEstimate = fmt(m$absolute_comparison$estimate),
  MainLower = fmt(m$absolute_comparison$lower),
  MainUpper = fmt(m$absolute_comparison$upper),
  MainLoss = fmt(abs(m$absolute_comparison$lower)),
  MainInterval = interval(m$absolute_comparison),
  FlaggedBefore = fmt(levels$before[2]),
  FlaggedAfter = fmt(levels$after[2]),
  ComparisonBefore = fmt(levels$before[1]),
  ComparisonAfter = fmt(levels$after[1]),
  FlaggedChange = fmt(levels$change[2]),
  ComparisonChange = fmt(levels$change[1]),
  AdjustedEstimate = fmt(e$estimate[2]),
  AdjustedInterval = interval(e[2, ]),
  InclusiveEstimate = fmt(e$estimate[3]),
  InclusiveInterval = interval(e[3, ]),
  SeriousEstimate = fmt(e$estimate[10]),
  SeriousInterval = interval(e[10, ]),
  PretrendEstimate = fmt(e$estimate[11]),
  PretrendInterval = interval(e[11, ]),
  BootstrapLower = fmt(m$bootstrap[1]),
  BootstrapUpper = fmt(m$bootstrap[2]),
  BootstrapDraws = format_count(m$bootstrap_draws),
  BootstrapSeed = m$bootstrap_seed,
  LeaveMin = fmt(m$leave_one_out[1]),
  LeaveMax = fmt(m$leave_one_out[2]),
  SharedPercent = fmt(m$citing_overlap_percent),
  CodingN = format_count(m$coding_n),
  Rated = format_count(m$rated),
  Ack = format_count(m$acknowledgment),
  Nonack = format_count(m$nonacknowledgment),
  AckPercent = fmt(m$acknowledgment_percent),
  AckLower = fmt(m$acknowledgment_ci[1]),
  AckUpper = fmt(m$acknowledgment_ci[2]),
  AckBoundLower = fmt(m$acknowledgment_bounds[1]),
  AckBoundUpper = fmt(m$acknowledgment_bounds[2]),
  Uncoded = format_count(m$coding_uncoded),
  Unavailable = format_count(m$coding_unavailable),
  CodingFalse = format_count(m$coding_false),
  PartialYear = format_count(m$coding_partial_year)
)
stopifnot(all(grepl("^[A-Za-z]+$", names(macros))), !anyDuplicated(names(macros)))
writeLines(paste0("\\newcommand{\\", names(macros), "}{", macros, "}"), "tabs/macros.tex")
readme <- paste(readLines("docs/README.in.md"), collapse = "\n")
readme_macros <- c(
  macros, jsonlite::read_json("tabs/journal_cohort_macros.json"),
  jsonlite::read_json("tabs/design_diagnostics_macros.json"),
  jsonlite::read_json("tabs/i4r_aggregate_macros.json"),
  jsonlite::read_json("tabs/lal_macros.json"),
  jsonlite::read_json("tabs/lazic_macros.json"),
  jsonlite::read_json("tabs/lazic_sdid_macros.json"),
  jsonlite::read_json("tabs/nieuwenhuis_source_macros.json"),
  jsonlite::read_json("tabs/methodological_macros.json"),
  jsonlite::read_json("tabs/hmx_macros.json")
)
for (name in names(readme_macros)) {
  readme <- gsub(paste0("{{", name, "}}"), readme_macros[[name]], readme, fixed = TRUE)
}
stopifnot(!grepl("{{", readme, fixed = TRUE))
writeLines(readme, "README.md")
