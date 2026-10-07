source("R/cohorts.R")
args <- commandArgs(trailingOnly = TRUE)
cache <- "private-data/cohorts"
out <- "data/cohorts"
if ("--validate" %in% args) {
  validate_cohort_inventory(out)
  quit(status = 0)
}
if ("--fetch" %in% args) {
  manifest <- read.csv(file.path(out, "sources.csv"), stringsAsFactors = FALSE)
  dir.create(cache, recursive = TRUE, showWarnings = FALSE)
  for (i in seq_len(nrow(manifest))) {
    stopifnot(basename(manifest$file[i]) == manifest$file[i])
    path <- manifest$local_path[i]
    dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
    if (!file.exists(path)) download.file(manifest$url[i], path, mode = "wb")
  }
  jsonlite::write_json(manifest, file.path(cache, "manifest.json"), pretty = TRUE)
}
manifest <- jsonlite::read_json(file.path(cache, "manifest.json"), simplifyVector = TRUE)
for (i in seq_len(nrow(manifest))) {
  path <- manifest$local_path[i]
  stopifnot(digest::digest(file = path, algo = "sha256") == manifest$sha256[i])
}
dir.create(out, recursive = TRUE, showWarnings = FALSE)
write.csv(manifest, file.path(out, "sources.csv"), row.names = FALSE, na = "")
read_source <- function(name, ...) {
  read.csv(source_path(name), stringsAsFactors = FALSE, check.names = FALSE, ...)
}
source_path <- function(name) {
  take <- manifest$file == name
  stopifnot(sum(take) == 1L)
  manifest$local_path[take]
}
save_source <- function(x, name) {
  cohort <- sub("_(papers|reanalyses|effects|candidates)$", "", name)
  directory <- file.path(out, cohort, "source_records")
  dir.create(directory, recursive = TRUE, showWarnings = FALSE)
  write.csv(x, file.path(directory, paste0(name, ".csv")), row.names = FALSE, na = "")
}
load_score <- function(name) {
  files <- unzip(source_path(paste0(name, ".zip")), list = TRUE)
  stopifnot(sum(files$Name == "analyst data.RData") == 1L)
  directory <- tempfile()
  dir.create(directory)
  on.exit(unlink(directory, recursive = TRUE))
  unzip(source_path(paste0(name, ".zip")), files = "analyst data.RData", exdir = directory)
  e <- new.env()
  load(file.path(directory, "analyst data.RData"), envir = e)
  e
}
collected <- new.env(parent = emptyenv())
collected$papers <- collected$assessments <- list()
add <- function(id, p, a) {
  stopifnot(!anyDuplicated(p$paper_id), all(a$paper_id %in% p$paper_id))
  p$cohort <- id
  a$cohort <- id
  collected$papers[[length(collected$papers) + 1L]] <- p
  collected$assessments[[length(collected$assessments) + 1L]] <- a
}

rpp <- read_source("rpp.csv", fileEncoding = "CP1252")
rpp <- rpp[!is.na(rpp$Completion.R) & rpp$Completion.R == 1, ]
stopifnot(nrow(rpp) == 100L, !anyDuplicated(rpp$Local.ID))
paper_key <- do.call(paste, c(rpp[c(
  "Study.Title.O", "Authors.O", "Journal.O", "Volume.O", "Issue.O", "Pages.O"
)], sep = "|"))
paper_id <- rpp$Local.ID[match(paper_key, paper_key)]
keep <- !duplicated(paper_id)
stopifnot(sum(keep) == 98L)
dir.create(file.path(out, "rpp"), recursive = TRUE, showWarnings = FALSE)
write.csv(data.frame(source_study_id = rpp$Local.ID, paper_id = paper_id),
  file.path(out, "rpp", "paper_crosswalk.csv"),
  row.names = FALSE
)

save_source(rpp[c(
  "Local.ID", "Study.Title.O", "Authors.O", "Journal.O", "Volume.O", "Issue.O", "Pages.O",
  "Project.URL", "Completion.R", "Replicate.R", "T.pval.USE.R", "T.sign.R.125", "T.r.O", "T.r.R"
)], "rpp")
add(
  "rpp", cohort_papers(paper_id[keep], rpp$Study.Title.O[keep], link = rpp$Project.URL[keep]),
  cohort_assessments(paper_id, rpp$Local.ID, "replication_judgment", rpp$Replicate.R,
    "rpp.csv",
    p_value = rpp$T.pval.USE.R
  )
)

replication <- load_score("score_replication")
r <- cohort_join(replication$repli_binary, replication$repli_outcomes, "report_id")
r <- cohort_join(r, replication$paper_metadata[c("paper_id", "title", "DOI")], "paper_id")
stopifnot(
  nrow(r) == 274L, length(unique(r$paper_id)) == 164L,
  sum(r$repli_score_criteria_met) == 151L, all(nzchar(r$DOI))
)
save_source(r[c(
  "paper_id", "claim_id", "report_id", "title", "DOI", "repli_type", "repli_score_criteria_met",
  "repli_binary_analyst", "repli_p_value", "repli_effect_size_type", "repli_effect_size_value"
)], "score_replication")
p <- r[!duplicated(r$paper_id), ]
add(
  "score_replication", cohort_papers(p$paper_id, p$title, p$DOI),
  cohort_assessments(r$paper_id, r$report_id, "replication_score_criterion",
    ifelse(r$repli_score_criteria_met, "met", "not_met"), "score_replication.zip",
    p_value = r$repli_p_value
  )
)

reproduction <- load_score("score_reproduction")
r <- reproduction$repro_outcomes
r <- r[!r$is_covid & r$repro_version_of_record & r$repro_outcome_overall != "none", ]
stopifnot(nrow(r) == 551L, length(unique(r$paper_id)) == 143L)
r <- cohort_join(r, reproduction$paper_metadata[c("paper_id", "title", "DOI")], "paper_id")
save_source(
  r[c("paper_id", "claim_id", "report_id", "title", "DOI", "repro_outcome_overall")],
  "score_reproduction"
)
p <- reproduction$pr_outcomes[!reproduction$pr_outcomes$covid, ]
p <- cohort_join(p, reproduction$paper_metadata[c("paper_id", "title", "DOI")], "paper_id")
stopifnot(nrow(p) == 600L)
save_source(p[c(
  "paper_id", "title", "DOI", "data_available", "code_available",
  "public_source_data_and_code", "process_reproducible"
)], "score_reproduction_candidates")
add(
  "score_reproduction", cohort_papers(p$paper_id, p$title, p$DOI),
  cohort_assessments(
    r$paper_id, r$report_id, "computational_reproduction",
    r$repro_outcome_overall, "score_reproduction.zip"
  )
)

p <- read_source("multi100_papers.csv")
r <- read_source("multi100_reanalyses.csv")
stopifnot(nrow(p) == 100L, nrow(r) == 509L)
meta <- replication$paper_metadata
score_id <- sub(".*_", "", p$paper_id)
idx <- match(score_id, meta$paper_id)
normalize_title <- function(x) gsub("[^[:alnum:]]", "", tolower(x))
matched <- !is.na(idx) & normalize_title(p$original_title) == normalize_title(meta$title[idx])
p$doi <- ifelse(matched, meta$DOI[idx], "")
p$score_paper_id <- ifelse(matched, score_id, "")
save_source(p, "multi100_papers")
save_source(r[c(
  "paper_id", "analyst_id", "analysis_id", "task1_categorisation",
  "original_reproduction_outcome", "p_value_report", "direction_of_result",
  "reanalysis_cohens_d", "peer_eval_pass", "incomplete_response_pass"
)], "multi100_reanalyses")
add(
  "multi100", cohort_papers(p$paper_id, p$original_title, p$doi, p$general_osf_link),
  cohort_assessments(r$paper_id, r$analysis_id, "analyst_task1_judgment",
    r$task1_categorisation, "multi100_reanalyses.csv",
    p_value = r$p_value_report
  )
)

p <- read_source("cancer_papers.csv")
r <- read_source("cancer_effects.csv")
stopifnot(nrow(p) == 53L, nrow(r) == 188L, length(unique(r[["Paper #"]])) == 23L)
save_source(p[c(
  "Paper #", "Original paper title", "Year", "Original paper journal",
  "OSF project link", "Replication study fully completed", "Link to Replication study"
)], "cancer_papers")
save_source(r[c(
  "Paper #", "Experiment #", "Effect #", "Internal replication #",
  "Expected difference based on the original paper?", "Observed difference in replication?",
  "Original p value", "Replication p value", "Effect size type", "Original effect size",
  "Replication effect size", "Original standard error", "Replication standard error"
)], "cancer_effects")
add(
  "cancer", cohort_papers(p[["Paper #"]], p[["Original paper title"]],
    link = p[["Link to Replication study"]]
  ), cohort_assessments(r[["Paper #"]],
    paste(r[["Paper #"]], r[["Experiment #"]], r[["Effect #"]],
      r[["Internal replication #"]],
      sep = ":"
    ),
    "replication_observed_difference", r[["Observed difference in replication?"]],
    "cancer_effects.csv",
    p_value = r[["Replication p value"]]
  )
)

r <- read.csv2(source_path("mediation.csv"), stringsAsFactors = FALSE, check.names = FALSE)
stopifnot(nrow(r) == 174L, !anyDuplicated(r$ID))
save_source(r, "mediation")
# Source IDs and bibliography numbering differ; do not invent a crosswalk.
add(
  "mediation", cohort_papers(r$ID, rep("", nrow(r)), identity_status = "crosswalk_pending"),
  cohort_assessments(r$ID, r$ID, "mediation_method", as.character(r$method_num), "mediation.csv")
)

table_file <- tempfile(fileext = ".txt")
status <- system2("pdftotext", c(
  "-layout", "-f", "27", "-l", "27",
  source_path("hmx_published.pdf"), table_file
))
stopifnot(status == 0L)
lines <- readLines(table_file, warn = FALSE)
unlink(table_file)
lines <- lines[grepl("\\([12][0-9]{3}[ab]?\\).* (AJPS|APSR|IO|JOP|CPS) ", lines)]
study <- trimws(substr(lines, 1, 133))
journal <- trimws(substr(lines, 134, 144))
hmx <- data.frame(
  study = study, journal = journal,
  low_high_not_rejected = trimws(substr(lines, 145, 159)),
  severe_extrapolation = trimws(substr(lines, 160, 171)),
  linearity_rejected = trimws(substr(lines, 172, 183)),
  overall_score = trimws(substr(lines, 184, 195))
)
stopifnot(nrow(hmx) == 46L, length(unique(study)) == 22L)
for (field in names(hmx)[3:6]) {
  stopifnot(all(hmx[[field]] %in% c("", as.character(0:3))))
}
save_source(hmx, "hmx")
id <- sprintf("hmx_%02d", match(study, unique(study)))
native <- do.call(rbind, lapply(names(hmx)[3:5], function(field) {
  cohort_assessments(
    id, paste(seq_along(id), field, sep = ":"), field, hmx[[field]],
    "hmx_published.pdf:Table A1, page 27"
  )
}))
keep <- !duplicated(id)
add(
  "hmx", cohort_papers(id[keep], rep("", sum(keep)),
    link = "https://doi.org/10.1017/pan.2018.46", identity_status = "bibliographic_reference",
    reference = paste(study[keep], journal[keep])
  ), native
)

table_file <- tempfile(fileext = ".txt")
status <- system2("pdftotext", c("-layout", source_path("panel_a.pdf"), table_file))
stopifnot(status == 0L)
lines <- readLines(table_file, warn = FALSE)
unlink(table_file)
start <- grep("Table A1. Summary of Findings", lines, fixed = TRUE)
stopifnot(length(start) == 1L)
lines <- lines[start:length(lines)]
lines <- lines[seq_len(grep("Note:", lines, fixed = TRUE)[1] - 1L)]
lines <- lines[grepl("\\(20[0-9]{2}[ab]?\\).* (AJPS|APSR|JOP) ", lines)]
panel <- data.frame(
  study = trimws(substr(lines, 1, 55)), journal = trimws(substr(lines, 56, 66)),
  att_p_below_05 = trimws(substr(lines, 156, 172)),
  pretrend_p_above_05 = trimws(substr(lines, 173, 188)),
  placebo_p_above_05 = trimws(substr(lines, 189, 204)),
  carryover_p_above_05 = trimws(substr(lines, 205, 220)),
  breakdown_m = trimws(substr(lines, 221, 240))
)
stopifnot(nrow(panel) == 49L, !anyDuplicated(panel$study))
for (field in names(panel)[3:6]) {
  stopifnot(all(panel[[field]] %in% c("", "✓", "n.a.")))
  panel[[field]] <- ifelse(panel[[field]] == "✓", "true",
    ifelse(panel[[field]] == "n.a.", "not_applicable", "false")
  )
}
save_source(panel, "panel")
id <- sprintf("panel_%02d", seq_len(nrow(panel)))
native <- do.call(rbind, lapply(names(panel)[3:7], function(field) {
  cohort_assessments(
    id, paste(id, field, sep = ":"), field, panel[[field]],
    "panel_a.pdf:Table A1"
  )
}))
add(
  "panel", cohort_papers(id, rep("", length(id)),
    link = "https://doi.org/10.7910/DVN/9RJFZF", identity_status = "bibliographic_reference",
    reference = paste(panel$study, panel$journal)
  ), native
)

p <- do.call(rbind, collected$papers)
a <- do.call(rbind, collected$assessments)
flora <- read.csv("data/inventories/flora_inventory.csv", stringsAsFactors = FALSE)
flora$title_key <- normalize_title(flora$original_title)
links <- list()
for (i in which(!nzchar(p$doi) & nzchar(p$title))) {
  matches <- flora[flora$title_key == normalize_title(p$title[i]) & nzchar(flora$original_doi), ]
  if (length(unique(matches$original_doi)) == 1L) {
    p$doi[i] <- matches$original_doi[1]
    links[[length(links) + 1L]] <- data.frame(
      cohort = p$cohort[i], paper_id = p$paper_id[i], doi = p$doi[i],
      source_record_ids = paste(matches$record_id, collapse = ";"),
      method = "unique DOI among exact normalized FLoRA title matches"
    )
  }
}
write.csv(do.call(rbind, links), file.path(out, "identity_links.csv"), row.names = FALSE)
p$doi <- tolower(sub("^https?://(dx\\.)?doi.org/", "", trimws(p$doi)))
p$assessments <- tabulate(
  match(paste(a$cohort, a$paper_id), paste(p$cohort, p$paper_id)),
  nbins = nrow(p)
)
write.csv(p, file.path(out, "papers.csv"), row.names = FALSE, na = "")
write.csv(a, file.path(out, "assessments.csv"), row.names = FALSE, na = "")
known <- p[nzchar(p$doi), c("cohort", "paper_id", "doi")]
overlap <- known[duplicated(known$doi) | duplicated(known$doi, fromLast = TRUE), ]
write.csv(overlap[order(overlap$doi, overlap$cohort), ], file.path(out, "overlap.csv"),
  row.names = FALSE, na = ""
)
for (cohort in unique(p$cohort)) {
  directory <- file.path(out, cohort)
  dir.create(directory, recursive = TRUE, showWarnings = FALSE)
  write.csv(p[p$cohort == cohort, ], file.path(directory, "papers.csv"), row.names = FALSE, na = "")
  write.csv(a[a$cohort == cohort, ], file.path(directory, "assessments.csv"),
    row.names = FALSE, na = ""
  )
  write.csv(manifest[manifest$cohort == cohort, ], file.path(directory, "sources.csv"),
    row.names = FALSE, na = ""
  )
}
validate_cohort_inventory(out)
