# Where the uncertainty comes from

This check reconstructs the four article-clustered standard errors directly
from paired citation counts. It does not assume the publicity comparisons are causal.

| Audit | Flagged / comparison | Log-scale SE | Weight, % | Variance from top article, % | Variance from top five, % |
| --- | ---: | ---: | ---: | ---: | ---: |
| Nieuwenhuis | 76 / 77 | 0.124 | 33.6 | 12.5 | 40.1 |
| Lal | 8 / 59 | 0.145 | 24.5 | 43.6 | 71.0 |
| Lazic | 82 / 45 | 0.138 | 27.0 | 10.8 | 31.2 |
| HMX | 13 / 7 | 0.186 | 14.9 | 37.3 | 83.8 |

The independent calculation gives a pooled contrast of -12.9% [-24.3, 0.2]%, with log-scale SE 0.0717.
The fixed-effect interval uses a normal critical value. It is not wide because
a four-study t critical value was applied or because random-effects heterogeneity
was added. Most uncertainty comes from variation in article-level citation changes.

For article i in group g, the normalized change is its share of the group's
post citations minus its share of the group's pre citations. The squared
normalized changes sum to the unadjusted variance of the log ratio contrast.
Multiplying by G/(G−1) × (2G−1)/(2G−3) reproduces the fitted model's
article-clustered finite-sample adjustment, where G counts contributing articles.
All-zero pairs do not identify that coefficient. Variance shares diagnose
concentration; they are not a reason to delete influential papers.

These intervals condition on the model and comparison. They do not include
uncertainty from unobserved earlier disclosure, confounding trends, or treating
different diagnostic labels as a common exposure. Reproducible calculation is
separate from identification of a publicity effect.
