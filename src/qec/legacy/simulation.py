"""
Legacy simulation utilities based on the original
Qiskit implementation.

This module provides Monte Carlo routines for
estimating logical failure rates using the
reference Qiskit circuit simulator together with
the NetworkX-based Minimum Weight Perfect Matching
(MWPM) decoder.

The implementation is retained for historical
reference and comparison with the current
Stim + PyMatching simulation pipeline.
"""

import numpy as np

from qiskit import transpile
from qiskit_aer import AerSimulator

from qec.legacy.circuit import k_rounds_surface_code
from qec.legacy.noise import depol_noise_model

from qec.decoders.networkx import (
    decode_one_shot,
    decode_spacetime_one_shot,
)

def logical_failure_rates_single(
    distance: int = 3,
    k: int = 1,
    shots: int = 4000,
    p1: float = 0.01,
    ro: float = 0.0,
) -> tuple[float, float]:
    """
    Estimate logical X- and Z-failure rates using the
    legacy Qiskit simulation pipeline with single-round
    MWPM decoding.

    This routine performs Monte Carlo simulation using
    AerSimulator and the reference NetworkX decoder.
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
    Estimate logical X- and Z-failure rates using the
    legacy Qiskit simulation pipeline with space-time
    MWPM decoding.

    Multiple rounds of syndrome extraction are decoded
    using the reference NetworkX implementation.
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
    Compare single-round and space-time decoding for
    the legacy Qiskit simulation pipeline across a
    range of physical error rates.

    Returns logical failure rates for both decoding
    strategies to enable benchmarking.
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