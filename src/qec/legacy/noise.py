"""
Noise model definitions for QEC simulations.
"""

from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import ReadoutError, depolarizing_error


def depol_noise_model(
    p1: float = 0.005,
    p2: float | None = None,
    ro: float = 0.02,
) -> NoiseModel:
    """
    Create a depolarizing noise model with readout errors.
    """
    if p2 is None:
        p2 = 2.5 * p1

    noise_model = NoiseModel()

    # Single-qubit depolarizing errors
    noise_model.add_all_qubit_quantum_error(
        depolarizing_error(p1, 1),
        ["id", "h", "x", "sx"],
    )

    # Two-qubit depolarizing errors
    noise_model.add_all_qubit_quantum_error(
        depolarizing_error(p2, 2),
        ["cx"],
    )

    # Ancilla readout errors
    readout_error = ReadoutError(
        [
            [1 - ro, ro],
            [ro, 1 - ro],
        ]
    )

    ancillas = range(9, 17)

    for qubit in ancillas:
        noise_model.add_readout_error(readout_error, [qubit])

    return noise_model