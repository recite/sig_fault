library(ggplot2)
results <- readRDS("data/derived/results.rds")
dir.create("figs", showWarnings = FALSE)
paper_theme <- theme_minimal(base_size = 11) + theme(
  panel.grid.minor = element_blank(), panel.grid.major.x = element_blank(),
  axis.title = element_text(color = "black"), axis.text = element_text(color = "black"),
  strip.text = element_text(hjust = 0, face = "bold"), legend.position = "top",
  plot.margin = margin(8, 18, 8, 8)
)
annual <- results$annual
annual$group <- ifelse(annual$flag == 1L, "Flagged", "Comparison")
plot_data <- rbind(
  transform(annual, value = mean, statistic = "Mean citations per paper"),
  transform(annual, value = median, statistic = "Median citations per paper")
)
plot_data$statistic <- factor(plot_data$statistic,
  levels = c("Median citations per paper", "Mean citations per paper")
)
p <- ggplot(plot_data, aes(year, value, color = group, linetype = group)) +
  geom_vline(xintercept = 2011.65, color = "grey55", linewidth = .4) +
  geom_line(linewidth = .7) +
  geom_point(size = 1.8) +
  facet_wrap(~statistic, nrow = 1) +
  scale_color_manual(values = c(Comparison = "#555555", Flagged = "#156082")) +
  scale_linetype_manual(values = c(Comparison = "dashed", Flagged = "solid")) +
  scale_x_continuous(breaks = 2009:2015) +
  scale_y_continuous(limits = c(0, NA)) +
  labs(x = "Citing publication year", y = NULL, color = NULL, linetype = NULL) +
  paper_theme
ggsave("figs/citation_paths.pdf", p, width = 6.5, height = 3.1, device = cairo_pdf)
y <- results$proportional_years
p <- ggplot(y, aes(year, percent)) +
  geom_hline(yintercept = 0, color = "grey55", linewidth = .4) +
  geom_linerange(aes(ymin = lower_simultaneous, ymax = upper_simultaneous),
    linewidth = .65, color = "#156082"
  ) +
  geom_point(size = 2, color = "#156082") +
  scale_x_continuous(breaks = 2011:2015) +
  labs(
    x = "Citing publication year",
    y = "Relative post/pre citation change (%)"
  ) +
  paper_theme
ggsave("figs/year_contrasts.pdf", p, width = 6.5, height = 3.4, device = cairo_pdf)
