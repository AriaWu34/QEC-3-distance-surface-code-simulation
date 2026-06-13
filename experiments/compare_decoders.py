"""
Compare single-round and space-time decoding.

Usage:
    python experiments/compare_decoders.py
"""

from qec.simulation import compare_single_vs_spacetime
from qec.visualization import plot_decoder_comparison

import numpy as np


def main():
    p_vals = np.linspace(0.0, 0.08, 9)

    results = compare_single_vs_spacetime(
        p_vals,
        k_space_time=3,
        k_single=1,
        shots=8000,
        ro=0.01,
    )

    plot_decoder_comparison(
        *results,
        save_path="results/comparison/decoder_comparison.png",
    )


if __name__ == "__main__":
    main()