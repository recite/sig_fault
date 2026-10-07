cohort_join <- function(left, right, key) {
  stopifnot(!anyNA(right[[key]]), !anyDuplicated(right[[key]]))
  idx <- match(left[[key]], right[[key]])
  stopifnot(!anyNA(idx))
  fields <- setdiff(names(right), key)
  stopifnot(!any(fields %in% names(left)))
  cbind(left, right[idx, fields, drop = FALSE], row.names = NULL)
}

cohort_papers <- function(id, title, doi = "", link = "", identity_status = "identified",
                          reference = "") {
  data.frame(
    paper_id = as.character(id), title = title, doi = doi, source_link = link,
    identity_status = identity_status, source_reference = reference, stringsAsFactors = FALSE
  )
}

cohort_assessments <- function(paper_id, id, type, outcome, source, p_value = "") {
  data.frame(
    paper_id = as.character(paper_id), assessment_id = as.character(id),
    assessment_type = type, source_outcome = as.character(outcome), source_file = source,
    p_value = as.character(p_value), stringsAsFactors = FALSE
  )
}

validate_cohort_inventory <- function(path) {
  p <- read.csv(file.path(path, "papers.csv"), colClasses = "character", na.strings = NULL)
  a <- read.csv(file.path(path, "assessments.csv"), colClasses = "character", na.strings = NULL)
  stopifnot(
    !anyDuplicated(p[c("cohort", "paper_id")]),
    !anyDuplicated(a[c("cohort", "assessment_id")]),
    all(paste(a$cohort, a$paper_id) %in% paste(p$cohort, p$paper_id)),
    all(p$identity_status %in% c("identified", "bibliographic_reference", "crosswalk_pending")),
    all(nzchar(p$title[p$identity_status == "identified"]))
  )
  summary <- do.call(rbind, lapply(unique(p$cohort), function(cohort) {
    paper <- p[p$cohort == cohort, ]
    result <- a[a$cohort == cohort, ]
    data.frame(
      cohort = cohort, roster_papers = nrow(paper),
      assessed_papers = length(unique(result$paper_id)), assessment_rows = nrow(result),
      known_dois = sum(nzchar(paper$doi)), identities_pending = sum(!nzchar(paper$title))
    )
  }))
  write.csv(summary, file.path(path, "coverage.csv"), row.names = FALSE)
  for (cohort in unique(p$cohort)) {
    directory <- file.path(path, cohort)
    for (name in c("papers", "assessments")) {
      combined <- if (name == "papers") p else a
      part <- read.csv(file.path(directory, paste0(name, ".csv")),
        colClasses = "character", na.strings = NULL
      )
      expected <- combined[combined$cohort == cohort, ]
      rownames(expected) <- rownames(part) <- NULL
      stopifnot(identical(lapply(part, as.character), lapply(expected, as.character)))
    }
    info <- jsonlite::read_json(file.path(directory, "study.json"))
    counts <- summary[summary$cohort == cohort, ]
    notes <- c(
      paste0("# ", info$title), "", info$authors, "", info$assessment, "",
      sprintf(
        "The inventory preserves %d paper records and %d assessment rows concerning %d papers.",
        counts$roster_papers, counts$assessment_rows, counts$assessed_papers
      ), "", "## Files", "",
      "- `papers.csv`: one row per source paper ID, including unassessed roster entries.",
      "- `assessments.csv`: source-level outcomes; multiple rows may belong to one paper.",
      "- `source_records/`: selected original columns or an exact source-table extraction.",
      "- `sources.csv`: exact download URLs, original-file checksums and local source paths.",
      "- `study.json`: study-specific definitions, timing evidence and remaining work.", "",
      paste0("Original downloads are preserved in `private-data/cohorts/", cohort, "/source/`."),
      "The [shared dictionary](../dictionary.md) defines the normalized columns.", "",
      "## Construction and outcomes", "", info$construction, "", info$outcomes, "",
      "## Disclosure timing", "", info$timing, "",
      "## Sources and next step", "",
      paste0("[Study] (", info$reference, "); [archive] (", info$archive, ")."), "",
      info[["next"]], "", "## Rebuild", "",
      "From the repository root, run `make cohorts-import` using saved originals, or",
      "`make cohorts-fetch` to download the recorded source URLs and verify their hashes.",
      "Run `make cohorts` for offline consistency checks and regeneration of this index."
    )
    writeLines(gsub("] (", "](", notes, fixed = TRUE), file.path(directory, "README.md"))
  }
  lines <- c(
    "# Methodological audits and replication cohorts", "",
    "Each study has its own folder with paper identities, source assessments,",
    "provenance and notes.",
    "These inventories preserve complete source records. The [psychology replication",
    "analysis](rpp/pipeline/README.md) and",
    "[interaction-audit analysis](hmx/pipeline/README.md) enter the",
    "[five-study synthesis](../../docs/meta/assessments.md);",
    "other new cohorts await citation comparisons.",
    "Paper counts include unassessed roster entries where the source supplies them.",
    "Assessment rows",
    "can represent claims, diagnostics or repeated analysts, not independent papers.",
    "Shared originals",
    "are recorded in `overlap.csv`; counts across cohorts must not simply be added.", "",
    "| Study | Roster papers | Assessed papers | Assessment rows | Known DOIs |",
    "| --- | ---: | ---: | ---: | ---: |"
  )
  for (i in seq_len(nrow(summary))) {
    x <- summary[i, ]
    lines <- c(lines, sprintf(
      "| [%s](%s/README.md) | %d | %d | %d | %d |", x$cohort,
      x$cohort, x$roster_papers, x$assessed_papers, x$assessment_rows, x$known_dois
    ))
  }
  lines <- c(
    lines, "",
    "Next priorities are the interaction and panel-method audits and the cancer",
    "replication cohort. The RPP pipeline verifies all 98 DOIs; the table above",
    "retains the initial discovery inventory, which had 76 DOI links.",
    "SCORE's large rosters are preserved now, but its 2026 summary publications are",
    "after the current 2025 citation cutoff;",
    "earlier report dates require verification. The mediation identity crosswalk",
    "remains unresolved.", "",
    "The [discovery queue](discovery.csv) records further methodological audits and",
    "replication projects.",
    "The [dictionary](dictionary.md) explains keys, outcome meanings, missingness and joins."
  )
  writeLines(lines, file.path(path, "README.md"))
  print(summary, row.names = FALSE)
  invisible(summary)
}
