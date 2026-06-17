"""
Stim backend for surface-code simulations.

Provides utilities for constructing Stim-compatible
surface-code circuits and detector error models.
"""

from dataclasses import dataclass

import stim

from qec.geometry import (
    d_idx,
    code_sizes,
    generate_plaquettes,
    validate_distance,
)


@dataclass(frozen=True)
class StabilizerMeasurement:
    """
    Metadata describing a stabilizer measurement.
    """

    round_idx: int
    stabilizer_idx: int
    record_idx: int


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

        self.measurements: list[StabilizerMeasurement] = []

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
    def ancilla_indices(self) -> range:
        return range(
            self.n_data,
            self.n_qubits,
        )

    @property
    def data_indices(self) -> range:
        return range(self.n_data)

    @property
    def n_stabilizers(self) -> int:
        return len(self.plaquettes) * 2

    def reset_measurements(self) -> None:
        """
        Clear measurement bookkeeping.
        """

        self.measurements.clear()

    def data_idx(
        self,
        row: int,
        col: int,
    ) -> int:
        """
        Return the linear index of a data qubit.
        """

        return d_idx(
            row,
            col,
            self.distance,
        )

    def add_x_stabilizer(
        self,
        circuit: stim.Circuit,
        ancilla: int,
        plaquette,
    ) -> None:
        """
        Add an X-stabilizer measurement.
        """

        circuit.append("H", [ancilla])

        for row, col in plaquette:
            circuit.append(
                "CX",
                [
                    ancilla,
                    self.data_idx(row, col),
                ],
            )

        circuit.append("H", [ancilla])

        circuit.append("M", [ancilla])

    def add_z_stabilizer(
        self,
        circuit: stim.Circuit,
        ancilla: int,
        plaquette,
    ) -> None:
        """
        Add a Z-stabilizer measurement.
        """

        for row, col in plaquette:
            circuit.append(
                "CX",
                [
                    self.data_idx(row, col),
                    ancilla,
                ],
            )

        circuit.append("M", [ancilla])

    def add_syndrome_round(
        self,
        circuit: stim.Circuit,
    ) -> None:
        """
        Add one round of syndrome extraction.
        """

        # X stabilizers
        for s, plaquette in enumerate(self.plaquettes):

            ancilla = self.x_ancilla_start + s

            self.add_x_stabilizer(
                circuit,
                ancilla,
                plaquette,
            )

        # Z stabilizers
        for s, plaquette in enumerate(self.plaquettes):

            ancilla = self.z_ancilla_start + s

            self.add_z_stabilizer(
                circuit,
                ancilla,
                plaquette,
            )

    def build_circuit(self) -> stim.Circuit:
        """
        Build a Stim surface-code circuit.
        """

        self.reset_measurements()

        circuit = stim.Circuit()

        circuit.append(
            "R",
            range(self.n_qubits),
        )

        for _ in range(self.rounds):
            self.add_syndrome_round(circuit)

        return circuit

    def detector_error_model(
        self,
    ) -> stim.DetectorErrorModel:
        """
        Generate the detector error model.
        """

        return self.build_circuit().detector_error_model()