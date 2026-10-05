source("R/data.R")

path <- "data/pilot"
dir.create(path, recursive = TRUE, showWarnings = FALSE)
source_path <- file.path(path, "sources/iv_replicate.rds")
expected_hash <- "0fdda663357d8e03c0c89ac7a6e54654c6a1b9123f27806ce37da71ef690aafc"
stopifnot(digest::digest(file = source_path, algo = "sha256") == expected_hash)

# The deposited .rds is an R workspace, despite its extension.
environment <- new.env()
load(source_path, envir = environment)
iv <- environment$d
stopifnot(nrow(iv) == 70L, length(unique(iv$title)) == 67L)
stopifnot(!anyDuplicated(iv$name), !anyNA(iv$f_effective))
iv$weak_screen <- iv$f_effective < 10
iv$inference_sensitive <- with(iv, {
  iv_analy_p < 0.05 & (AR_p >= 0.05 | (!is.na(tF_p) & tF_p >= 0.05))
})
iv$screen_positive <- iv$weak_screen | iv$inference_sensitive

nw <- read_classification()
RNGkind("Mersenne-Twister", "Inversion", "Rejection")
set.seed(20261004)
nw_ids <- sort(sample(nw$article_id[nw$flag == 1L], 10L))
set.seed(20261004)
iv_titles <- sort(sample(sort(unique(iv$title[iv$screen_positive])), 10L))

nw_frame <- data.frame(
  audit_id = "nieuwenhuis2011", paper_id = paste0("nw_", nw$article_id),
  claim_id = paste0("nw_", nw$article_id), source_id = nw$article_id,
  title = "", journal = nw$journal, source_year = nw$cohort,
  source_locator = paste("page", nw$page, "link", nw$link),
  claim_description = paste(nw$type_of_state_manipulation, nw$dependent_variable, sep = "; "),
  source_assessment = nw$seriousness_of_mistake,
  assessment_type = ifelse(nw$flag == 1L, "reported_interaction_error", "not_flagged"),
  screen_positive = nw$flag == 1L, selected = nw$article_id %in% nw_ids,
  paper_inclusion_probability = ifelse(nw$flag == 1L, 10 / sum(nw$flag == 1L), 0),
  stringsAsFactors = FALSE
)
title_ids <- setNames(iv$name[!duplicated(iv$title)], unique(iv$title))
iv_frame <- data.frame(
  audit_id = "lal2024", paper_id = paste0("iv_", title_ids[iv$title]),
  claim_id = paste0("iv_", iv$name), source_id = iv$name,
  title = iv$title, journal = iv$journal, source_year = iv$year,
  source_locator = iv$iv_model,
  claim_description = paste(iv$treat, "->", iv$outcome),
  source_assessment = paste0(
    "effective F=", iv$f_effective, "; analytic p=", iv$iv_analy_p,
    "; AR p=", iv$AR_p, "; tF p=", iv$tF_p
  ),
  assessment_type = "diagnostic_not_proof_of_false_claim",
  screen_positive = iv$screen_positive, selected = iv$title %in% iv_titles,
  paper_inclusion_probability = ifelse(
    iv$title %in% iv$title[iv$screen_positive],
    10 / length(unique(iv$title[iv$screen_positive])), 0
  ), stringsAsFactors = FALSE
)
frame <- rbind(nw_frame, iv_frame)
stopifnot(!anyDuplicated(frame$claim_id))
stopifnot(length(unique(frame$paper_id[frame$selected])) == 20L)
write.csv(frame, file.path(path, "registry.csv"), row.names = FALSE, na = "")
write.csv(iv, file.path(path, "iv_diagnostics.csv"), row.names = FALSE, na = "")
cat(
  "Registry:", nrow(frame), "reviewed comparisons; selected:",
  length(unique(frame$paper_id[frame$selected])), "papers\n"
)
