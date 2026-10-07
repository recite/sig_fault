library(ggplot2)
annual <- read.csv("data/nieuwenhuis/paths/annual_summary.csv")
annual$group <- ifelse(annual$flag == 1L, "Flagged (76 papers)", "Comparison (77 papers)")
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
  geom_point(size = 1.6) +
  facet_wrap(~statistic, nrow = 1) +
  scale_color_manual(values = c(
    "Comparison (77 papers)" = "#555555", "Flagged (76 papers)" = "#156082"
  )) +
  scale_linetype_manual(values = c(
    "Comparison (77 papers)" = "dashed", "Flagged (76 papers)" = "solid"
  )) +
  scale_x_continuous(breaks = seq(min(annual$year), max(annual$year), by = 2)) +
  scale_y_continuous(limits = c(0, NA), labels = scales::label_comma()) +
  labs(
    title = "Citations to flagged and comparison papers, 2009-2025",
    subtitle = "OpenAlex articles and reviews; the same 153 papers in every year",
    x = "Citing publication year", y = NULL, color = NULL, linetype = NULL,
    caption = paste(
      "Vertical line: publication of the critique in August 2011. Raw annual means and medians.",
      "Duplicate records and citations dated before the original paper are excluded.",
      "Papers appeared in 2009-2010, so early counts include partial publication years.",
      "Descriptive citation paths; differences between the lines are not treatment effects.",
      sep = "\n"
    )
  ) +
  theme_minimal(base_size = 11) +
  theme(
    panel.grid.minor = element_blank(), panel.grid.major.x = element_blank(),
    axis.title = element_text(color = "black"), axis.text = element_text(color = "black"),
    strip.text = element_text(hjust = 0, face = "bold"), legend.position = "top",
    plot.title.position = "plot", plot.caption.position = "plot",
    plot.caption = element_text(hjust = 0, size = 9, margin = margin(t = 12)),
    plot.margin = margin(10, 16, 10, 10)
  )
ggsave("figs/citation_paths_openalex.pdf", p, width = 8.5, height = 4.8, device = cairo_pdf)
