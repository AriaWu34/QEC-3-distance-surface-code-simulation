"""
Simulation and benchmarking utilities for surface-code experiments.

Provides Monte Carlo routines for estimating logical failure rates
under different noise models and decoding strategies.
"""

import numpy as np

from qiskit import transpile
from qiskit_aer import AerSimulator

from qec.circuit import k_rounds_surface_code
from qec.noise import depol_noise_model
from qec.decoders.mwpm import (
    decode_one_shot,
    decode_spacetime_one_shot,
    MWPMDecoder,
)
from qec.stim_backend import (
    SurfaceCodeStimBackend,
)

def logical_failure_rates_single(
    distance: int = 3,
    k: int = 1,
    shots: int = 4000,
    p1: float = 0.01,
    ro: float = 0.0,
) -> tuple[float, float]:
    """
    Estimate logical failure rates for a planar surface code
    using last-round-only decoding.
    """
        
    sim = AerSimulator()
    qc = k_rounds_surface_code(distance=distance, k=k)
    tc = transpile(qc, basis_gates=['id','rz','sx','x','h','cx','measure'],
                   optimization_level=1)
    nm = depol_noise_model(p1=p1, ro=ro)

    res = sim.run(tc, shots=shots, noise_model=nm).result()
    counts = res.get_counts()

    failX = failZ = total = 0
    for bitstr, n in counts.items():
        lx, lz = decode_one_shot(bitstr, distance=distance, k=k)
        failX += lx * n
        failZ += lz * n
        total += n
    return failX/max(1,total), failZ/max(1,total)


def logical_failure_rates_spacetime(
    distance: int = 3,
    k: int = 3,
    shots: int = 4000,
    p1: float = 0.01,
    ro: float = 0.01,
) -> tuple[float, float]:
    """
    Estimate logical failure rates for a planar surface code
    using space-time MWPM decoding.
    """
    sim = AerSimulator()
    qc = k_rounds_surface_code(distance=distance, k=k)
    tc = transpile(qc, basis_gates=['id','rz','sx','x','h','cx','measure'], optimization_level=1)
    nm = depol_noise_model(p1=p1, ro=ro)

    res = sim.run(tc, shots=shots, noise_model=nm).result()
    counts = res.get_counts()

    failX = failZ = total = 0
    for bitstr, n in counts.items():
        lx, lz = decode_spacetime_one_shot(bitstr, distance=distance, k=k)
        failX += lx * n
        failZ += lz * n
        total += n

    return failX/max(1,total), failZ/max(1,total)


def compare_single_vs_spacetime(
    p_vals,
    k_space_time: int = 3,
    k_single: int = 1,
    shots: int = 6000,
    ro: float = 0.01,
    distance: int = 3,
):
    """
    Compare logical failure rates for single-round and space-time decoding
    across a range of physical error rates.
    """
    pLX_1, pLZ_1, pLX_ST, pLZ_ST = [], [], [], []
    for p in p_vals:

        # single-round baseline
        fx1, fz1 = logical_failure_rates_single(
            distance=distance,
            k=k_single,
            shots=shots,
            p1=p,
            ro=ro,
        )
        pLX_1.append(fx1); pLZ_1.append(fz1)

        # space–time decoidng
        fxst, fzst = logical_failure_rates_spacetime(
            distance=distance,
            k=k_space_time,
            shots=shots,
            p1=p,
            ro=ro,
        )
        pLX_ST.append(fxst); pLZ_ST.append(fzst)
    return (np.array(p_vals),
            np.array(pLX_1), np.array(pLZ_1),
            np.array(pLX_ST), np.array(pLZ_ST))


def logical_failure_rate_stim(
    distance: int = 3,
    rounds: int = 5,
    shots: int = 1000,
    depolarizing_error: float = 0.01,
    readout_error: float = 0.01,
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