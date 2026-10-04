"""Tranche 2: where the gate's bar comes from.

Deviation 10 lets the draw go ahead only if the allocation rule's expected smallest
final class count is at least 200. This script shows what that figure looks like when
the pre-filter is useless: every tranche 1 item is given a RANDOM predicted label,
unrelated to its tranche 1 label, and the rule in tranche2_03_allocate.py is applied.

It uses the tranche 1 labels and weights only. No pre-filter output is involved, so it
can be run, and was run, before any comment was scored.

    python tranche2_gate_null_simulation.py
"""
from __future__ import annotations

import numpy as np

import tranche2_common as c
from tranche2_03_allocate import leximin

REPLICATES = 400
SEED = [c.SEED, c.TRANCHE, 99]


def main() -> None:
    c.setup_console()
    key, _, labels = c.load_tranche1(verbose=False)
    gold = labels.to_numpy()
    w = key["weight"].to_numpy()
    T = np.array([(gold == k).sum() for k in c.CLASSES], dtype=float)
    G = np.stack([(gold == k) for k in c.CLASSES], axis=1).astype(float)
    pool = np.array([3000, 3000, 3000])            # pools are not binding in this exercise
    allowed = np.array([True, True, True])
    rng = np.random.default_rng(SEED)
    scenarios = [
        ("40% predicted not relevant, classes equal", [0.40, 0.20, 0.20, 0.20]),
        ("25% predicted not relevant, classes equal", [0.25, 0.25, 0.25, 0.25]),
        ("30% predicted not relevant, OTHER rare", [0.30, 0.30, 0.30, 0.10]),
        ("30% predicted not relevant, OTHER very rare", [0.30, 0.33, 0.33, 0.04]),
    ]
    print(f"tranche 1 counts {dict(zip(c.CLASSES, (int(x) for x in T)))}; a second natural tranche would be expected "
          f"to leave the smallest class near {int(2 * T.min())}; the gate's bar is {c.GATE_MIN_EXPECTED_SMALLEST}\n")
    print(f"{'random predicted labels':46s} {'mean':>6s} {'95th pct':>9s} {'share at or above the bar':>26s}")
    for name, probs in scenarios:
        out = []
        for _ in range(REPLICATES):
            pred = rng.choice(4, size=len(gold), p=probs)          # 0 = not relevant, 1..3 = the classes
            H = np.zeros((3, 3))
            usable = True
            for p in range(3):
                m = pred == p + 1
                if not m.any():
                    usable = False
                    break
                H[p] = (w[m, None] * G[m]).sum(axis=0) / w[m].sum()
            if not usable:
                continue
            a, _ = leximin(T, H, pool, allowed, c.TRANCHE2_N)
            out.append(float((T + a @ H).min()))
        v = np.array(out)
        print(f"{name:46s} {v.mean():6.1f} {np.percentile(v, 95):9.1f} "
              f"{100 * (v >= c.GATE_MIN_EXPECTED_SMALLEST).mean():25.1f}%")


if __name__ == "__main__":
    main()
