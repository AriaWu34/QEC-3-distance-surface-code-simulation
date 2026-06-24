"""
Logical failure-rate experiment using
Stim and PyMatching.

Usage:
    python experiments/logical_failure_stim.py
"""

from pathlib import Path
import numpy as np

from qec.simulation import (
    logical_failure_rate_stim,
)
from qec.visualization import (
    plot_logical_failure_rate,
    plot_distance_scaling,
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

    distances = [3, 5, 7]
    results = {}

    for distance in distances:

        rates = []

        print(
            f"\nRunning d={distance}"
        )

        for p in p_vals:

            rate = logical_failure_rate_stim(
                distance=distance,
                rounds=5,
                shots=1000,
                depolarizing_error=p,
                readout_error=0.01,
            )

            rates.append(rate)

            print(
                f"d={distance} "
                f"p={p:.4f} "
                f"logical={rate:.4f}"
            )

        results[distance] = rates

        plot_logical_failure_rate(
            physical_error_rates=p_vals,
            logical_error_rates=rates,
            distance=distance,
            save_path=(
                OUTPUT_DIR
                / f"logical_failure_rate_d{distance}.png"
            ),
        )

    plot_distance_scaling(
        physical_error_rates=p_vals,
        logical_error_rates_by_distance=results,
        save_path=(
            OUTPUT_DIR
            / "distance_scaling.png"
        ),
    )


if __name__ == "__main__":
    main()