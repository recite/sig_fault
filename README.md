## Significant Error: Citations to Research With Publicized Statistical Errors

Gelman et al.(2006) discuss a common statistical error where researchers treat differences between significant and non-significant results as significant. They describe a scenario where results from two independent studies report parameter estimates and standard errors of 25 $\pm$ 10 and 10 $\pm$ 10, respectively. The first result is significant at the 1\% level, while the second is non-significant. The finding is interpreted by many as evidence of a significant difference, but a basic calculation of the difference in the effects and its standard error tells a different story, $15 \pm \sqrt{10^{2} + 10^{2}}$, which is not significant at the conventional 95\% level.

Nieuwenhuis et al. (2011) analyzed 157 behavioral, systems, and cognitive neuroscience articles that relied on such analysis and were published in journals like *Nature*, *Science*, *Neuron*, and *Journal of Neuroscience* between 2009 and 2010. They found that roughly half (79) of the articles made this error. Further, they found that the error had serious consequences for the results for approximately two-thirds of the studies that made the error. To date, none of the studies that Nieuwenhuis et al. (2011) identified as problematic have been retracted. We assess whether the citation rate changes after the publication of Nieuwenhuis et al. (2011).

### Data

* [Original data + Citations to articles](data/01_nieuwenhuis/)
* [Are new citations approving?](data/02_are_nw_citations_approving/)

### Script, Manuscript, Figures, and Tables

* [Script](01_nieuwenhuis.R) produces:
    * [tables](tabs/)
    * [figures](figs/)
* [Manuscript](ms/)

### Authors

Ken Cor and Gaurav Sood

## 🔗 Adjacent Repositories

- [recite/propagation_of_error](https://github.com/recite/propagation_of_error) — Retracted articles continue to get cited after being retracted.
- [recite/re-cite.org](https://github.com/recite/re-cite.org) — Code for a web application to highlight citations to retracted articles.
- [recite/miscitations](https://github.com/recite/miscitations) — Estimating the Frequency of Miscitations in Review Articles
- [recite/i4replication](https://github.com/recite/i4replication) — How replicable and robust are the papers in select social science journals? We analyze replication attempts by https://i4replication.org
- [recite/autosum](https://github.com/recite/autosum) — Summarize Publications Automatically
