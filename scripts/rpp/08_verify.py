"""Verify every ancestor's code, sources, outputs, and successful execution."""

from scripts.research_pipeline import Run


def main():
    with Run("rpp", "08_verify", __file__, True) as run:
        run.require("07_analyze")
        run.check(
            "complete_provenance_chain",
            True,
            "All seven stages and transitive ancestors verified",
        )
        run.record["metrics"] = dict(verified_stages=7)
        print("Seven RPP stages verified, including transitive source and code hashes.")


if __name__ == "__main__":
    main()
