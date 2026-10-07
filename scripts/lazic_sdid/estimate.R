source("R/synthetic_did.R")
base <- "data/lazic/sdid"
read <- function(name) read.csv(file.path(base, name), stringsAsFactors = FALSE)
write <- function(x, name) write.csv(x, file.path(base, name), row.names = FALSE, na = "")
stopifnot(packageDescription("synthdid")$RemoteSha == "70c1ce3eac58e28c30b67435ca377bb48baa9b8a")
panel <- read("panel.csv")
specs <- read("specifications.csv")
models <- estimates <- placebos <- paths <- list()
papers <- times <- balances <- draws <- indices <- list()
for (i in seq_len(nrow(specs))) {
  spec <- specs[i, ]
  name <- spec$specification
  x <- panel[panel$specification == name, ]
  roster <- unique(x[c("article_id", "flag", "publication_year", "journal", "split_unit")])
  setup <- sdid_matrix(x, roster, spec$pre_start:spec$pre_end, spec$post_start:spec$post_end)
  placebo_setup <- sdid_matrix(x, roster, spec$pre_start:2015, 2016L)
  placebo <- sdid_fit(placebo_setup)
  placebos[[name]] <- data.frame(
    specification = name, sdid = as.numeric(placebo$fit), did = sdid_did(placebo_setup)$estimate,
    actual = tail(placebo$paths$flagged_mean, 1),
    predicted = tail(placebo$paths$synthetic_adjusted, 1),
    donor_effective_n = placebo$diagnostics$donor_effective_n,
    pre_rmse = placebo$diagnostics$pre_rmse
  )
  result <- sdid_fit(setup)
  seed <- 20261008L + i
  bootstrap <- sdid_bootstrap(result$fit, 1999L, seed)
  estimate <- as.numeric(result$fit)
  did <- sdid_did(setup)
  estimates[[name]] <- data.frame(
    specification = name, n_flagged = nrow(setup$y) - setup$n0, n_comparison = setup$n0,
    pre = paste(spec$pre_start:spec$pre_end, collapse = ";"),
    post = paste(spec$post_start:spec$post_end, collapse = ";"),
    estimate = estimate, se = bootstrap$se,
    lower = estimate - qnorm(.975) * bootstrap$se, upper = estimate + qnorm(.975) * bootstrap$se,
    did = did$estimate, did_se = did$se, did_lower = did$lower, did_upper = did$upper,
    result$diagnostics, seed = seed, bootstrap_repetitions = 1999L,
    bootstrap_rejected = bootstrap$rejected
  )
  weights <- attr(result$fit, "weights")
  paper <- setup$roster
  paper$weight <- c(weights$omega, rep(1 / sum(paper$flag), sum(paper$flag)))
  papers[[name]] <- cbind(specification = name, paper)
  times[[name]] <- data.frame(
    specification = name, year = setup$years,
    period = c(rep("pre", setup$t0), rep("post", ncol(setup$y) - setup$t0)),
    weight = c(weights$lambda, rep(1 / (ncol(setup$y) - setup$t0), ncol(setup$y) - setup$t0))
  )
  balance <- list()
  for (variable in c("publication_year", "split_unit")) {
    for (value in sort(unique(as.character(paper[[variable]])))) {
      z <- as.numeric(as.character(paper[[variable]]) == value)
      balance[[length(balance) + 1L]] <- data.frame(
        specification = name, variable = variable, value = value,
        flagged = mean(z[paper$flag == 1L]), comparison = mean(z[paper$flag == 0L]),
        weighted_comparison = weighted.mean(z[paper$flag == 0L], weights$omega)
      )
    }
  }
  balances[[name]] <- do.call(rbind, balance)
  paths[[name]] <- cbind(specification = name, result$paths)
  draws[[name]] <- cbind(specification = name, bootstrap$draws)
  indices[[name]] <- cbind(specification = name, bootstrap$indices)
  models[[name]] <- list(fit = result$fit, placebo = placebo$fit, article_order = rownames(setup$y))
  message(name, ": finished ", nrow(bootstrap$draws), " article bootstrap draws")
}
estimates <- do.call(rbind, estimates)
placebos <- do.call(rbind, placebos)
paths <- do.call(rbind, paths)
for (name in c("estimates", "placebos", "paths")) write(get(name), paste0(name, ".csv"))
for (name in c("papers", "times", "balances", "draws", "indices")) {
  filename <- switch(name,
    papers = "paper_weights",
    times = "time_weights",
    balances = "balance",
    draws = "bootstrap",
    indices = "bootstrap_indices"
  )
  write(do.call(rbind, get(name)), paste0(filename, ".csv"))
}
saveRDS(models, file.path(base, "models.rds"))
writeLines(trimws(capture.output(sessionInfo()), which = "right"), file.path(base, "R-session.txt"))
status <- list(
  models = nrow(estimates), bootstrap_draws = sum(estimates$bootstrap_repetitions),
  max_identity_error = max(estimates$identity_error),
  bootstrap_rejected = sum(estimates$bootstrap_rejected),
  package_version = as.character(packageVersion("synthdid")),
  package_commit = packageDescription("synthdid")$RemoteSha
)
jsonlite::write_json(status, file.path(base, "estimation_status.json"),
  pretty = TRUE, auto_unbox = TRUE
)
