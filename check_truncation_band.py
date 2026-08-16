"""
check_truncation_band.py -- DIAGNOSTIC. No network, no cost.

Scopes the COLLECT_MAX_POSTS / PROBE_MAX_POSTS inconsistency.

A query is flagged `saturated` only when posts_found >= PROBE_MAX_POSTS (100), but
an unblocked query collects at most COLLECT_MAX_POSTS (60). Any query with
posts_found in [60, 99] is therefore collected UNBLOCKED and TRUNCATED: production
takes the 60 newest of what the probe found, because searchSort = "new".

This script counts how many queries sit in that band, per tier, and reports whether
each has already been collected -- which determines whether fixing it costs money.

Run:  (.venv active)  python check_truncation_band.py
"""

from __future__ import annotations
import pandas as pd
import config as cfg

CPP = 9.4   # observed mean stored comments per collected post


def main() -> None:
    if not cfg.PROBE_REPORT.exists():
        raise SystemExit(f"[stop] no probe report at {cfg.PROBE_REPORT}")

    df = pd.read_csv(cfg.PROBE_REPORT)
    lo, hi = cfg.COLLECT_MAX_POSTS, cfg.PROBE_MAX_POSTS

    print(f"[settings] COLLECT_MAX_POSTS={lo}  PROBE_MAX_POSTS={hi}  "
          f"MAX_POSTS_PER_BLOCK={cfg.MAX_POSTS_PER_BLOCK}  "
          f"blocks={len(cfg.build_windows())}")
    if lo >= hi:
        print("[settings] truncation band is EMPTY because "
              "COLLECT_MAX_POSTS >= PROBE_MAX_POSTS\n")
        print(f"AFFECTED QUERIES: 0 of {len(df)}")
        print("No query can satisfy posts_found >= COLLECT_MAX_POSTS "
              "and posts_found < PROBE_MAX_POSTS.")
        return

    print(f"[settings] truncation band = posts_found in [{lo}, {hi - 1}]\n")

    df["band"] = pd.cut(
        df["posts_found"], [-1, lo - 1, hi - 1, 10 ** 9],
        labels=[f"under {lo} (census, fine)",
                f"{lo}-{hi - 1} (TRUNCATED)",
                f"{hi}+ (saturated, blocked)"])

    print("QUERIES BY BAND, PER TIER")
    print(pd.crosstab(df["tier"], df["band"]).to_string())

    band = df[(df["posts_found"] >= lo) & (df["posts_found"] < hi)].copy()
    print(f"\nAFFECTED QUERIES: {len(band)} of {len(df)}")
    if band.empty:
        print("None. The inconsistency is latent, not active -- no change required now,")
        print("though it should still be closed so a future re-probe cannot trip on it.")
        return

    band["dropped"] = band["posts_found"] - lo
    band = band.sort_values("posts_found", ascending=False)

    # already collected? unblocked queries are single full-window jobs
    def collected(row) -> bool:
        job = {"subreddit": row.subreddit, "term": row.term,
               "start": cfg.STUDY_START, "end": cfg.STUDY_END}
        return cfg.job_path(job, "collect").exists()

    band["already_collected"] = [collected(r) for r in band.itertuples()]

    cols = ["tier", "subreddit", "term", "posts_found", "dropped",
            "earliest_post", "latest_post", "already_collected"]
    print("\n" + band[cols].to_string(index=False))

    print(f"\nposts dropped in total: {int(band['dropped'].sum())}")
    print(f"already collected (fixing these means RE-collecting): "
          f"{int(band['already_collected'].sum())}")
    print(f"not yet collected (fixing these is free of rework): "
          f"{int((~band['already_collected']).sum())}")

    # cost of each remedy for the affected queries only
    n_blocks = len(cfg.build_windows())
    cur = sum(cfg.estimate_cost(min(n, lo) * (1 + CPP), 1) for n in band["posts_found"])
    opt_a = sum(cfg.estimate_cost(min(n, hi) * (1 + CPP), 1) for n in band["posts_found"])
    opt_b = len(band) * cfg.estimate_cost(cfg.MAX_POSTS_PER_BLOCK * n_blocks * (1 + CPP),
                                          n_blocks)

    print("\nCOST FOR THE AFFECTED QUERIES ONLY (excludes re-collection of any already done)")
    print(f"{'current  (unblocked, cap 60, truncated)':<48} "
          f"{int(band['posts_found'].clip(upper=lo).sum()):>5} posts  USD {cur:6.2f}")
    print(f"{'option A (unblocked, cap 100, census)':<48} "
          f"{int(band['posts_found'].clip(upper=hi).sum()):>5} posts  USD {opt_a:6.2f}")
    print(f"{'option B (blocked, 3/block)':<48} "
          f"{len(band) * cfg.MAX_POSTS_PER_BLOCK * n_blocks:>5} posts  USD {opt_b:6.2f}")


if __name__ == "__main__":
    main()
