"""
Logical failure-rate experiment using
Stim and PyMatching.

Usage:
    python experiments/logical_failure.py
"""

from pathlib import Path

import numpy as np

from qec.simulation import (
    logical_failure_rate_stim,
)
from qec.visualization import (
    plot_logical_failure_rate,
)


OUTPUT_DIR = Path(
    "results/logical_failure"
)


def main():

    p_vals = np.linspace(
        0.001,
        0.05,
        10,
    )

    rates = []

    for p in p_vals:

        rate = logical_failure_rate_stim(
            distance=3,
            rounds=5,
            shots=1000,
            depolarizing_error=p,
            readout_error=0.01,
        )

        rates.append(rate)

        print(
            f"p={p:.4f} "
            f"logical={rate:.4f}"
        )

    plot_logical_failure_rate(
        physical_error_rates=p_vals,
        logical_error_rates=rates,
        distance=3,
        save_path=(
            OUTPUT_DIR
            / "d3.png"
        ),
    )


if __name__ == "__main__":
    main()