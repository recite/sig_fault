specifications <- jsonlite::fromJSON("data/pilot/iv_specs.json", simplifyVector = FALSE)
environment <- new.env()
load("data/pilot/sources/iv_replicate.rds", envir = environment)
published <- environment$d
fixest::setFixest_nthreads(1)

results <- lapply(specifications, function(specification) {
  numerical_warnings <- character()
  result <- withCallingHandlers(
    {
      specification <- lapply(specification, unlist)
      s <- specification
      d <- readRDS(file.path("data/pilot/sources/iv_raw", s$file))
      needed <- unique(c(s$Y, s$D, s$Z, s$controls, s$cl, s$FE, s$weights))
      d <- d[complete.cases(d[needed]), ]
      rhs <- if (length(s$controls)) paste(unique(s$controls), collapse = " + ") else "1"
      fixed <- if (length(s$FE)) paste(s$FE, collapse = " + ") else "0"
      instruments <- paste(s$Z, collapse = " + ")
      covariance <- if (length(s$cl)) {
        fixest::vcov_cluster(cluster = reformulate(s$cl), vcov_fix = FALSE)
      } else {
        "hetero"
      }
      weight <- if (length(s$weights)) reformulate(s$weights) else NULL
      iv_formula <- as.formula(paste(s$Y, "~", rhs, "|", fixed, "|", s$D, "~", instruments))
      rf_formula <- as.formula(paste(s$Y, "~", instruments, "+", rhs, "|", fixed))
      fs_formula <- as.formula(paste(s$D, "~", instruments, "+", rhs, "|", fixed))
      iv <- fixest::feols(iv_formula, d, vcov = covariance, weights = weight, fixef.rm = "none")
      reduced <- fixest::feols(
        rf_formula, d, vcov = covariance, weights = weight, fixef.rm = "none"
      )
      first <- fixest::feols(fs_formula, d, vcov = covariance, weights = weight, fixef.rm = "none")
      design <- model.matrix(reformulate(c(s$Z, s$controls)), d)
      assignment <- attr(design, "assign")
      terms <- attr(terms(reformulate(c(s$Z, s$controls))), "term.labels")
      instrument_columns <- colnames(design)[assignment %in% match(s$Z, terms)]
      pattern <- paste0("^(", paste(instrument_columns, collapse = "|"), ")$")
      ar <- fixest::wald(reduced, keep = pattern, print = FALSE)
      fs <- fixest::wald(first, keep = pattern, print = FALSE)
      original <- published[match(sub("^iv_", "", s$paper_id), published$name), ]
      stopifnot(nrow(original) == 1L, !is.na(original$name), nobs(iv) == nobs(reduced))
      coefficient <- unname(coef(iv)[paste0("fit_", s$D)])
      data.frame(
        paper_id = s$paper_id, n = nobs(iv), source_n = original$N,
        excluded_columns = length(instrument_columns), source_p_iv = original$p_iv,
        iv_coefficient = coefficient, source_iv_coefficient = original$iv_coef,
        coefficient_difference = coefficient - original$iv_coef,
        ar_f = ar$stat, ar_df1 = ar$df1, ar_df2 = ar$df2, ar_p = ar$p,
        source_ar_p = original$AR_p, first_stage_joint_f = fs$stat,
        source_effective_f = original$f_effective,
        check_status = ifelse(
          length(instrument_columns) != original$p_iv,
          "instrument_encoding_discrepancy",
          "same_point_estimate_check_inference_conventions"
        ), stringsAsFactors = FALSE
      )
    },
    warning = function(warning) {
      numerical_warnings <<- c(numerical_warnings, conditionMessage(warning))
      invokeRestart("muffleWarning")
    }
  )
  result$numerical_warning <- paste(unique(numerical_warnings), collapse = "; ")
  if (length(numerical_warnings)) {
    result$check_status <- "point_estimate_reproduced_covariance_requires_review"
  }
  result
})
results <- do.call(rbind, results)
stopifnot(nrow(results) == 10L, !anyDuplicated(results$paper_id))
stopifnot(all(round(results$iv_coefficient, 4) == results$source_iv_coefficient))
write.csv(results, "data/pilot/iv_verification.csv", row.names = FALSE)

# Independent matrix calculation of the seven-restriction AR test for the factor instrument.
alt <- readRDS("data/pilot/sources/iv_raw/jop_Alt_etal_2015.rds")
reference <- lm(gov ~ treatment + urate_now, alt)
columns <- grep("^treatment", names(coef(reference)))
b <- coef(reference)[columns]
v <- sandwich::vcovHC(reference, type = "HC1")[columns, columns]
statistic <- drop(t(b) %*% solve(v, b)) / length(columns)
p_value <- pf(statistic, length(columns), df.residual(reference), lower.tail = FALSE)
stopifnot(length(columns) == 7L)
stopifnot(abs(p_value - results$ar_p[results$paper_id == "iv_Alt2015"]) < 1e-10)
alt$treatment_code <- as.numeric(alt$treatment)
numeric_fit <- lm(gov ~ treatment_code + urate_now, alt)
numeric_t <- coef(numeric_fit)["treatment_code"] /
  sqrt(sandwich::vcovHC(numeric_fit, type = "HC1")["treatment_code", "treatment_code"])
numeric_p <- pf(numeric_t^2, 1, df.residual(numeric_fit), lower.tail = FALSE)
write.csv(data.frame(
  specification = c("seven_factor_indicators", "numeric_category_code"),
  ar_df1 = c(length(columns), 1L), ar_p = c(p_value, unname(numeric_p)),
  source_ar_p = published$AR_p[published$name == "Alt2015"]
), "data/pilot/iv_encoding_check.csv", row.names = FALSE)
cat("Ten IV point estimates independently reproduced; factor-instrument AR test verified.\n")
cat("Covariance warnings requiring review:", sum(nzchar(results$numerical_warning)), "papers.\n")
