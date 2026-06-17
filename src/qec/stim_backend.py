"""
Stim backend for surface-code simulations.

Provides utilities for constructing Stim-compatible
surface-code circuits and detector error models.
"""

import stim

from qec.geometry import (
    code_sizes,
    generate_plaquettes,
    validate_distance,
)


class SurfaceCodeStimBackend:
    """
    Stim implementation of the planar surface code.
    """

    def __init__(
        self,
        distance: int = 3,
        rounds: int = 1,
    ):

        validate_distance(distance)

        if rounds < 1:
            raise ValueError(
                "Rounds must be >= 1."
            )

        self.distance = distance
        self.rounds = rounds
        self.plaquettes = generate_plaquettes(distance)
        self.n_data, self.n_x, self.n_z = code_sizes(distance)

    @property
    def n_qubits(self) -> int:
        return self.n_data + self.n_x + self.n_z
    
    @property
    def x_ancilla_start(self) -> int:
        return self.n_data

    @property
    def z_ancilla_start(self) -> int:
        return self.n_data + self.n_x
    
    @property
    def ancilla_indices(self):
        return range(
            self.n_data,
            self.n_qubits,
        )
    
    @property
    def data_indices(self):
        return range(self.n_data)
    

    def build_circuit(self) -> stim.Circuit:
        """
        Build a Stim surface-code circuit.
        """

        circuit = stim.Circuit()
        circuit.append(
            "R",
            range(self.n_qubits),
        )

        return circuit

    def detector_error_model(self) -> stim.DetectorErrorModel:
        """
        Generate the detector error model.
        """

        return self.build_circuit().detector_error_model()