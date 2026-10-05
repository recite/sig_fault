source("R/data.R")
source("R/analysis.R")
dir.create("data/derived", recursive = TRUE, showWarnings = FALSE)
dir.create("tabs", showWarnings = FALSE)

classification <- read_classification()
coding <- read_coding()
raw <- clean_citations(read_citations(), coding)
stopifnot(all(raw$flag == classification$flag[match(raw$article_id, classification$article_id)]))
stopifnot(all(paste(coding$article_id, coding$accession) %in% paste(raw$article_id, raw$accession)))
target <- classification[match(raw$article_id, classification$article_id), ]
raw$before_target_year <- raw$year < target$cohort
raw$is_target_itself <- raw$year == target$cohort &
  toupper(trimws(raw$journal)) == toupper(trimws(target$journal)) &
  suppressWarnings(as.numeric(raw$first_page) == as.numeric(target$page))
raw$is_target_itself[is.na(raw$is_target_itself)] <- FALSE
stopifnot(setequal(raw$article_id[raw$before_target_year], c(23L, 25L)))
stopifnot(setequal(raw$article_id[raw$is_target_itself], c(23L, 25L)))
edges <- raw[!raw$duplicate & !raw$false_link, ]
covered <- sort(unique(raw$article_id))
ids <- setdiff(covered, c(23L, 25L))
panel <- make_panel(classification, edges, ids)
all_panel <- make_panel(classification, edges, covered)
changes <- article_changes(panel)
main <- estimate_change(changes, "Main comparison")
estimates <- rbind(
  main,
  estimate_change(changes, "Journal and publication-year adjustment", adjusted = TRUE),
  estimate_change(article_changes(all_panel), "Retain both questionable citation histories"),
  estimate_change(article_changes(make_panel(
    classification,
    raw[!raw$false_link, ], ids
  )), "Retain duplicate database records"),
  estimate_change(article_changes(make_panel(
    classification,
    raw[!raw$duplicate, ], ids
  )), "Retain known false citation links"),
  estimate_change(changes[changes$cohort == 2009L, ], "Papers published in 2009"),
  estimate_change(changes[changes$cohort == 2010L, ], "Papers published in 2010"),
  estimate_change(article_changes(panel, post = 2013:2015), "Later window: 2013-2015"),
  estimate_change(article_changes(panel, post = 2014:2015), "Later window: 2014-2015"),
  estimate_change(
    changes[changes$flag == 0L | changes$serious, ], "Potentially serious errors only"
  ),
  estimate_change(article_changes(
    panel[panel$cohort == 2009L, ],
    pre = 2009L, post = 2010L
  ), "Pre-critique change: 2009 cohort, 2009 to 2010")
)
annual <- annual_summary(panel)
year_changes <- do.call(rbind, lapply(2011:2015, function(year) {
  cbind(year = year, estimate_change(article_changes(panel, post = year), as.character(year)))
}))
# The five displayed year contrasts form one family; Bonferroni gives simultaneous intervals.
year_changes$lower_simultaneous <- year_changes$estimate - qt(
  1 - .05 / 10,
  year_changes$df
) * year_changes$se
year_changes$upper_simultaneous <- year_changes$estimate + qt(
  1 - .05 / 10,
  year_changes$df
) * year_changes$se
leave_one_out <- do.call(rbind, lapply(changes$article_id, function(id) {
  cbind(omitted_article = id, estimate_change(changes[changes$article_id != id, ], "Leave one out"))
}))
bootstrap_seed <- 31415L
bootstrap_draws <- 9999L
set.seed(bootstrap_seed)
boot <- replicate(bootstrap_draws, {
  a <- changes$change[changes$flag == 1L]
  b <- changes$change[changes$flag == 0L]
  mean(sample(a, replace = TRUE)) - mean(sample(b, replace = TRUE))
})
levels <- aggregate(cbind(before, after, change) ~ flag, changes, mean)
coding_counts <- as.data.frame(table(coding$status), stringsAsFactors = FALSE)
names(coding_counts) <- c("status", "n")
eligible_edges <- edges[edges$article_id %in% ids & edges$year %in% 2010:2015, ]
shared <- table(eligible_edges$key)
ack <- sum(coding$status == "Concern recorded")
rated <- sum(coding$status %in% c("Concern recorded", "No concern recorded"))
interval <- wilson_interval(ack, rated)
metrics <- list(
  classified = nrow(classification), classified_flagged = sum(classification$flag),
  covered = length(covered), missing = setdiff(classification$article_id, covered),
  questioned = c(23L, 25L), analyzed = length(ids),
  flagged = sum(changes$flag), comparison = sum(changes$flag == 0L),
  serious = sum(changes$serious), records = nrow(raw), repaired = sum(raw$repaired),
  duplicates = sum(raw$duplicate), false_links = sum(raw$false_link),
  zero_years = sum(panel$citations == 0L & panel$year >= 2010L),
  prepublication_records = sum(raw$year < classification$cohort[
    match(raw$article_id, classification$article_id)
  ]),
  main = main, levels = levels, bootstrap = unname(quantile(boot, c(.025, .975))),
  bootstrap_draws = bootstrap_draws, bootstrap_seed = bootstrap_seed,
  leave_one_out = range(leave_one_out$estimate),
  citing_documents = length(shared), shared_citing_documents = sum(shared > 1L),
  citing_overlap_percent = 100 * mean(shared > 1L),
  coding_n = nrow(coding), rated = rated, acknowledgment = ack, nonacknowledgment = rated - ack,
  acknowledgment_percent = 100 * ack / rated, acknowledgment_ci = 100 * interval,
  coding_partial_year = sum(coding$year == 2016L),
  coding_uncoded = sum(coding$status == "Uncoded"),
  coding_unavailable = sum(coding$status == "Article unavailable"),
  coding_false = sum(coding$status == "False citation link"),
  acknowledgment_bounds = 100 * c(ack, ack + nrow(coding) - rated - sum(
    coding$status == "False citation link"
  )) / (nrow(coding) - sum(coding$status == "False citation link")),
  source_sha256 = setNames(lapply(c(
    "data/01_nieuwenhuis/citations_to_articles_with_sig_fault.xlsx",
    "data/01_nieuwenhuis/citations_to_articles_wo_sig_fault.xlsx",
    "data/01_nieuwenhuis/from_nieuwenhuis/nieuwenhuis_with_id.csv",
    "data/02_are_nw_citations_approving/post_nw_pub_citation_100_approving.csv"
  ), function(path) digest::digest(file = path, algo = "sha256")), c(
    "flagged_citations", "comparison_citations", "classification", "coding"
  ))
)
for (name in c(
  "classification", "raw", "coding", "panel", "changes", "annual",
  "estimates", "year_changes", "leave_one_out"
)) {
  write.csv(get(name), file.path("data/derived", paste0(name, ".csv")),
    row.names = FALSE, na = ""
  )
}
for (name in c("annual", "estimates", "year_changes", "coding_counts", "levels")) {
  write.csv(get(name), file.path("tabs", paste0(name, ".csv")), row.names = FALSE, na = "")
}
jsonlite::write_json(metrics, "tabs/results.json", auto_unbox = TRUE, pretty = TRUE, digits = NA)
saveRDS(list(
  metrics = metrics, estimates = estimates, annual = annual,
  year_changes = year_changes, coding_counts = coding_counts, changes = changes
), "data/derived/results.rds")
print(main)
print(levels)
print(coding_counts)
