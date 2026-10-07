base <- "data/lazic/sdid"
read <- function(name) read.csv(file.path(base, name), stringsAsFactors = FALSE)
estimates <- read("estimates.csv")
placebos <- read("placebos.csv")
paths <- read("paths.csv")
fmt <- function(x) sprintf("%.2f", ifelse(abs(x) < .005, 0, x))
labels <- c(
  main = "Main", older_longer = "Older, four pre-years",
  older_same = "Older, three pre-years", shorter_post = "Two post-years"
)
tex <- c(
  "\\begin{tabular}{lrrr}", "\\toprule",
  "Sample/window & Flagged / controls & Synthetic DiD [95\\% CI] & Ordinary DiD [95\\% CI] \\\\",
  "\\midrule"
)
for (i in seq_len(nrow(estimates))) {
  r <- estimates[i, ]
  tex <- c(tex, sprintf(
    "%s & %s / %s & %s [%s, %s] & %s [%s, %s] \\\\",
    labels[r$specification], r$n_flagged, r$n_comparison,
    fmt(r$estimate), fmt(r$lower), fmt(r$upper),
    fmt(r$did), fmt(r$did_lower), fmt(r$did_upper)
  ))
}
writeLines(c(tex, "\\bottomrule", "\\end{tabular}"), "tabs/lazic_sdid.tex")
main <- estimates[estimates$specification == "main", ]
validation <- placebos[placebos$specification == "main", ]
post_paths <- paths[paths$specification == "main" & paths$year >= 2018, ]
macros <- c(
  LazicSdidEstimate = fmt(main$estimate), LazicSdidLower = fmt(main$lower),
  LazicSdidUpper = fmt(main$upper), LazicSdidDid = fmt(main$did),
  LazicSdidPlacebo = fmt(validation$sdid), LazicSdidPlaceboDid = fmt(validation$did),
  LazicSdidObserved = fmt(mean(post_paths$flagged_mean)),
  LazicSdidCounterfactual = fmt(mean(post_paths$synthetic_adjusted)),
  LazicSdidControls = main$n_comparison,
  LazicSdidDonors = fmt(main$donor_effective_n),
  LazicSdidMaxWeight = fmt(100 * main$donor_max)
)
writeLines(
  paste0("\\newcommand{\\", names(macros), "}{", macros, "}"),
  "tabs/lazic_sdid_macros.tex"
)
jsonlite::write_json(as.list(macros), "tabs/lazic_sdid_macros.json",
  pretty = TRUE, auto_unbox = TRUE
)
pdf("figs/lazic_sdid.pdf", width = 7, height = 3.7, family = "Helvetica")
par(mar = c(4, 4, 1, 1), las = 1)
p <- paths[paths$specification == "main", ]
ylim <- range(c(0, p$flagged_mean, p$synthetic_adjusted))
plot(p$year, p$flagged_mean,
  type = "n", ylim = ylim, xlab = "Citation year",
  ylab = "Mean citations per paper", bty = "l", xaxt = "n"
)
axis(1, 2014:2020)
abline(v = 2017, lty = 3, col = "grey50")
for (years in list(2014:2016, 2018:2020)) {
  z <- p[p$year %in% years, ]
  lines(z$year, z$flagged_mean, type = "o", pch = 16, lwd = 1.8, col = "#156082")
  lines(z$year, z$synthetic_adjusted, type = "o", pch = 1, lty = 2, lwd = 1.8, col = "#555555")
}
legend("bottomleft", c("Flagged papers", "Synthetic comparison, level adjusted"),
  col = c("#156082", "#555555"), lty = c(1, 2), pch = c(16, 1), bty = "n", cex = .85
)
invisible(dev.off())
report <- c(
  "# Synthetic DiD for the pseudoreplication audit", "",
  "Citations are distinct OpenCitations works per original article per year, all indexed types.",
  "Negative estimates mean fewer citations than the weighted comparison trajectory predicts.", "",
  paste0(
    "| Sample/window | Flagged/control | Synthetic DiD (95% interval) | ",
    "Ordinary DiD (95% interval) |"
  ),
  "|---|---:|---:|---:|"
)
for (i in seq_len(nrow(estimates))) {
  r <- estimates[i, ]
  report <- c(report, sprintf(
    "| %s | %s/%s | %s [%s, %s] | %s [%s, %s] |",
    labels[r$specification], r$n_flagged, r$n_comparison,
    fmt(r$estimate), fmt(r$lower), fmt(r$upper),
    fmt(r$did), fmt(r$did_lower), fmt(r$did_upper)
  ))
}
report <- c(
  report, "", sprintf(
    "Main synthetic comparison: effective donor count %s of %s; largest donor weight %s%%.",
    fmt(main$donor_effective_n), main$n_comparison, fmt(100 * main$donor_max)
  ), "",
  "| Sample/window | Held-out 2016 actual | Predicted | Synthetic DiD gap | Ordinary DiD gap |",
  "|---|---:|---:|---:|---:|"
)
for (i in seq_len(nrow(placebos))) {
  r <- placebos[i, ]
  report <- c(report, sprintf(
    "| %s | %s | %s | %s | %s |", labels[r$specification],
    fmt(r$actual), fmt(r$predicted), fmt(r$sdid), fmt(r$did)
  ))
}
report <- c(
  report, "", "## Interpretation and reproduction", "",
  "These are additive comparisons for older classified papers, not new independent audits.",
  "The main sample uses 2014–2016 and 2018–2020. The older four-year baseline starts in 2013;",
  "the older three-year fit holds its population fixed. The shorter follow-up ends in 2019.",
  "Intervals use 1,999 whole-article bootstrap draws with paper/time weights refitted,",
  "conditional on original regularization. Ordinary DiD uses Welch uncertainty on article changes.",
  "Neither interval is randomization inference or covers variation across publicity events.",
  "The held-out check fits anew without flagged 2016 or post-disclosure outcomes in weights.",
  "Comparison 2016 counts do enter its time weights. Donor weights remain broadly spread.",
  "The synthetic comparison does not improve the main held-out prediction over ordinary DiD.",
  "The older four-year fit assigns zero time weight to 2013 in its baseline adjustment,",
  "although that year still informs donor fitting. Its similarity to the three-year fit",
  "therefore supplies limited additional reassurance. Publication-cohort and split-unit-design",
  "balance also change little after weighting. All specified comparisons remain reported.", "",
  "Run `make lazic-sdid` from the repository root after restoring `renv.lock`.",
  "The numbered stages verify original identities, complete counts and sample dispositions.",
  "`paper_weights.csv` and `time_weights.csv` contain all estimation weights; `balance.csv`",
  "reports cohort and split-unit composition. `bootstrap_indices.csv` refers to article order",
  "in `models.rds`, also reproduced by `paper_weights.csv` within each specification.",
  "`bootstrap.csv` retains all accepted estimates. Seeds, rejected attempt counts, pinned software",
  "and transitive input/code/output hashes are recorded. Missing counts never become zero.", "",
  "[Design and sources](../../../docs/lazic/synthetic-did-design.md)."
)
writeLines(report, file.path(base, "README.md"))
