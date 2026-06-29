"""
Simulation utilities for Stim-based surface-code experiments.

Provides Monte Carlo routines for estimating logical failure
rates using Stim detector sampling and PyMatching decoding.
"""

from qec.decoders import MWPMDecoder
from qec.stim_backend import SurfaceCodeStimBackend


def logical_failure_rate_stim(
    distance: int = 3,
    rounds: int = 5,
    shots: int = 1000,
    depolarizing_error: float = 0.01,
    readout_error: float = 0.01,
    memory_basis: str = "Z",
) -> float:
    """
    Estimate logical failure rate using
    Stim detector sampling and PyMatching.
    """

    backend = SurfaceCodeStimBackend(
        distance=distance,
        rounds=rounds,
        depolarizing_error=depolarizing_error,
        readout_error=readout_error,
        memory_basis=memory_basis,
    )

    decoder = MWPMDecoder(
        backend="pymatching",
        dem=backend.detector_error_model(),
    )

    dets, obs = (
        backend
        .sample_detectors_and_observables(
            shots=shots,
        )
    )

    failures = 0

    for det, actual in zip(
        dets,
        obs,
    ):
        predicted = (
            decoder
            .decode_detection_events(det)
        )

        if not (
            predicted == actual
        ).all():
            failures += 1

    return failures / shots