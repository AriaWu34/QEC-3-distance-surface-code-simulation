"""
Plotting utilities for QEC experiments.
"""

from pathlib import Path
import matplotlib.pyplot as plt


def save_figure(save_path: str | None = None):
    """
    Save current matplotlib figure if a path is provided.
    """
    if save_path is None:
        return

    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(path, dpi=300, bbox_inches="tight")
    print(f"Saved figure to {path}")


def plot_decoder_comparison(
    ps,
    pLX_1,
    pLZ_1,
    pLX_ST,
    pLZ_ST,
    save_path: str | None = None,
):
    """
    Plot single-round vs space-time decoder performance.
    """
    plt.figure(figsize=(7.5, 5.2))

    plt.plot(ps, pLX_1, "o-", label="Logical-X (single round)")
    plt.plot(ps, pLZ_1, "s--", label="Logical-Z (single round)")

    plt.plot(
        ps,
        pLX_ST,
        "o-",
        linewidth=2.5,
        label="Logical-X (space-time, k=3)",
    )

    plt.plot(
        ps,
        pLZ_ST,
        "s--",
        linewidth=2.5,
        label="Logical-Z (space-time, k=3)",
    )

    plt.xlabel("Physical 1q depolarising probability $p_1$")
    plt.ylabel("Estimated logical failure rate")
    plt.title("Single-round vs Space-time Decoding")

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    save_figure(save_path)

    plt.show()