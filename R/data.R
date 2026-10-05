read_classification <- function(root = ".") {
  base <- file.path(root, "data/01_nieuwenhuis/from_nieuwenhuis")
  x <- read.csv(file.path(base, "nieuwenhuis_with_id.csv"), fileEncoding = "latin1")
  stopifnot(nrow(x) == 157L, !anyDuplicated(x$article_id))
  original <- readxl::read_excel(file.path(base, "nieuwenhuis_with_id.xls"),
    col_types = "text"
  )
  for (j in c(2L, 3L)) {
    for (i in seq_len(nrow(original))[-1L]) {
      if (is.na(original[[j]][i])) original[[j]][i] <- original[[j]][i - 1L]
    }
  }
  original <- original[!is.na(original[[1]]), ]
  index <- match(as.character(x$article_id), original[[1]])
  stopifnot(!anyNA(index), all(x$main_q == original[[9]][index]))
  stopifnot(all(x$journal == original[[2]][index]))
  stopifnot(all(substr(x$year_volume, 1, 4) == substr(original[[3]][index], 1, 4)))
  stopifnot(all(as.character(x$page) == original[[5]][index]))
  notes <- original[[14]][index]
  notes[is.na(notes)] <- ""
  stopifnot(all(trimws(x$seriousness_of_mistake) == trimws(notes)))
  x$flag <- as.integer(x$main_q == "YES")
  x$serious <- x$flag == 1L & grepl("potentially serious", x$seriousness_of_mistake)
  x$cohort <- as.integer(substr(x$year_volume, 1, 4))
  x$journal[x$journal %in% c("JN", "JoN")] <- "Journal of Neuroscience"
  x$journal[x$journal == "NN"] <- "Nature Neuroscience"
  x
}

repair_export_row <- function(row) {
  row <- as.character(row)
  row[is.na(row)] <- ""
  if (!any(grepl("\t", row, fixed = TRUE))) {
    return(row)
  }
  expanded <- unlist(lapply(row, function(cell) {
    if (cell == "") {
      ""
    } else {
      strsplit(paste0(cell, "\tEND"), "\t", fixed = TRUE)[[1]][
        -length(strsplit(paste0(cell, "\tEND"), "\t", fixed = TRUE)[[1]])
      ]
    }
  }), use.names = FALSE)
  stopifnot(length(expanded) >= length(row))
  if (length(expanded) > length(row)) {
    stopifnot(all(expanded[(length(row) + 1L):length(expanded)] == ""))
  }
  expanded[seq_along(row)]
}

read_citations <- function(root = ".") {
  base <- file.path(root, "data/01_nieuwenhuis")
  files <- c("citations_to_articles_wo_sig_fault.xlsx", "citations_to_articles_with_sig_fault.xlsx")
  pieces <- list()
  for (flag in 0:1) {
    path <- file.path(base, files[flag + 1L])
    for (sheet in readxl::excel_sheets(path)) {
      x <- as.data.frame(readxl::read_excel(path, sheet = sheet, col_types = "text"))
      stopifnot(ncol(x) == 55L)
      names(x)[1] <- "PT"
      bad <- which(is.na(x$PY) | !grepl("^[0-9]{4}$", x$PY))
      repaired <- rep(FALSE, nrow(x))
      for (i in bad) {
        x[i, ] <- repair_export_row(x[i, ])
        repaired[i] <- TRUE
      }
      stopifnot(all(grepl("^[0-9]{4}$", x$PY)), !anyNA(x$UT), !any(x$UT == ""))
      pieces[[length(pieces) + 1L]] <- data.frame(
        article_id = as.integer(sheet), flag = flag, source_row = seq_len(nrow(x)),
        year = as.integer(x$PY), accession = x$UT, doi = tolower(trimws(x$DI)),
        title = x$TI, journal = x$SO, first_page = x$BP,
        database_times_cited = suppressWarnings(as.integer(x$TC)),
        repaired = repaired, stringsAsFactors = FALSE
      )
    }
  }
  x <- do.call(rbind, pieces)
  x$doi[x$doi == ""] <- NA_character_
  x$key <- ifelse(is.na(x$doi), paste0("ut:", x$accession), paste0("doi:", x$doi))
  stopifnot(!anyDuplicated(x[c("article_id", "accession")]))
  years <- aggregate(year ~ article_id + key, x, function(y) length(unique(y)))
  stopifnot(all(years$year == 1L))
  x$duplicate <- duplicated(x[c("article_id", "key")])
  x
}

read_coding <- function(root = ".") {
  x <- read.csv(file.path(
    root,
    "data/02_are_nw_citations_approving/post_nw_pub_citation_100_approving.csv"
  ), fileEncoding = "latin1", check.names = FALSE, na.strings = "")
  data.frame(
    sample_id = x$citing_100_ID, article_id = x[["orig_article_article.id"]],
    accession = x$accession_num, year = x$pub_year, original_code = x$approving,
    status = ifelse(!is.na(x$approving),
      ifelse(x$approving == "yes", "No concern recorded", "Concern recorded"),
      ifelse(grepl("doesn't cite", x$notes, fixed = TRUE), "False citation link",
        ifelse(grepl("not found", x$notes, fixed = TRUE), "Article unavailable", "Uncoded")
      )
    ), stringsAsFactors = FALSE
  )
}

clean_citations <- function(x, coding) {
  false <- coding[coding$status == "False citation link", ]
  x$false_link <- paste(x$article_id, x$accession) %in% paste(false$article_id, false$accession)
  x$questionable_history <- x$article_id %in% c(23L, 25L)
  x
}

make_panel <- function(classification, citations, ids, years = 2009:2015) {
  stopifnot(all(ids %in% citations$article_id), !anyDuplicated(ids))
  meta <- classification[match(ids, classification$article_id), ]
  stopifnot(!anyNA(meta$article_id))
  grid <- merge(meta[c("article_id", "flag", "serious", "cohort", "journal")],
    data.frame(year = years),
    by = NULL
  )
  counts <- aggregate(
    list(citations = rep(1L, nrow(citations))),
    citations[c("article_id", "year")], sum
  )
  stopifnot(!anyDuplicated(counts[c("article_id", "year")]))
  panel <- merge(grid, counts, by = c("article_id", "year"), all.x = TRUE)
  stopifnot(nrow(panel) == length(ids) * length(years))
  panel$citations[is.na(panel$citations)] <- 0L
  panel[order(panel$article_id, panel$year), ]
}
