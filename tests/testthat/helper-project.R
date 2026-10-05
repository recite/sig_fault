root <- normalizePath(file.path("..", ".."))
source(file.path(root, "R/data.R"))
source(file.path(root, "R/analysis.R"))
read_derived <- function(name) read.csv(file.path(root, "data/derived", paste0(name, ".csv")))
