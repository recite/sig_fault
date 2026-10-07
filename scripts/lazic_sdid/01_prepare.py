"""Construct complete, post-publication panels for the Lazic synthetic DiD design."""

from scripts.research_pipeline import ROOT, Run, read_csv, unique, write_csv, write_json

SPECS = [
    ("main", 2013, 2014, 2020),
    ("older_longer", 2012, 2013, 2020),
    ("older_same", 2012, 2014, 2020),
    ("shorter_post", 2013, 2014, 2019),
]


def main():
    with Run(
        "lazic_sdid", "01_prepare", __file__, True, data_dir=ROOT / "data/lazic/sdid"
    ) as run:
        articles = read_csv(run.input(ROOT / "data/lazic/articles.csv"))
        panel = read_csv(run.input(ROOT / "data/lazic/opencitations/panel.csv"))
        prior = read_csv(run.input(ROOT / "data/lazic/prior_warnings.csv"))
        run.input(ROOT / "docs/lazic/synthetic-did-design.md")
        unique(articles, ["article_id"])
        unique(panel, ["article_id", "year"])
        index = {(r["article_id"], int(r["year"])): r for r in panel}
        prior_ids = {r["pmid"] for r in prior}
        dispositions, selected, specifications = [], [], []
        for name, cutoff, start, end in SPECS:
            years = list(range(start, 2017)) + list(range(2018, end + 1))
            counts = {"0": 0, "1": 0}
            for article in articles:
                reason = "included"
                if article["flagged"] not in ("0", "1"):
                    reason = "classification_unknown"
                elif article["pmid"] in prior_ids:
                    reason = "prior_warning"
                elif int(article["publication_year"]) > cutoff:
                    reason = "published_after_cutoff"
                dispositions.append(
                    dict(specification=name, **article, disposition=reason)
                )
                if reason != "included":
                    continue
                counts[article["flagged"]] += 1
                for year in years:
                    row = index[(article["article_id"], year)]
                    assert row["status"] == "complete"
                    assert row["flagged"] == article["flagged"]
                    assert int(row["citations"]) >= 0
                    selected.append(
                        dict(
                            specification=name,
                            article_id=article["article_id"],
                            year=year,
                            flag=int(article["flagged"]),
                            citations=int(row["citations"]),
                            status=row["status"],
                            publication_year=int(article["publication_year"]),
                            journal=article["journal"],
                            split_unit=article["split_unit"],
                        )
                    )
            expected = (50, 26) if cutoff == 2013 else (30, 14)
            run.check(
                name + "_population", (counts["1"], counts["0"]) == expected, counts
            )
            specifications.append(
                dict(
                    specification=name,
                    cutoff=cutoff,
                    pre_start=start,
                    pre_end=2016,
                    post_start=2018,
                    post_end=end,
                    n_flagged=counts["1"],
                    n_comparison=counts["0"],
                )
            )
        for name, rows in [
            ("panel.csv", selected),
            ("dispositions.csv", dispositions),
            ("specifications.csv", specifications),
        ]:
            write_csv(run.data / name, rows, list(rows[0]))
            run.output(run.data / name)
        unique(selected, ["specification", "article_id", "year"])
        status = dict(
            specifications=len(specifications),
            panel_rows=len(selected),
            dispositions=len(dispositions),
            complete=True,
        )
        write_json(run.data / "preparation_status.json", status)
        run.output(run.data / "preparation_status.json")
        run.record["metrics"] = status


if __name__ == "__main__":
    main()
