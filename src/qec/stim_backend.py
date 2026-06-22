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

        self.measurements: dict[
            tuple[int, int],
            StabilizerMeasurement,
        ] = {}

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
    
    def record_measurement(
        self,
        round_idx: int,
        stabilizer_idx: int,
        record_idx: int,
    ) -> None:
        """
        Store stabilizer measurement metadata.
        """

        self.measurements[
            (round_idx, stabilizer_idx)
        ] = StabilizerMeasurement(
            round_idx=round_idx,
            stabilizer_idx=stabilizer_idx,
            record_idx=record_idx,
        )

    def get_measurement(
        self,
        round_idx: int,
        stabilizer_idx: int,
    ) -> StabilizerMeasurement:
        """
        Retrieve a recorded stabilizer measurement.
        """

        return self.measurements[
            (round_idx, stabilizer_idx)
        ]

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
    
    def rec_offset(
        self,
        measurement: StabilizerMeasurement,
        current_record_idx: int,
    ) -> int:
        """
        Convert an absolute record index into
        a Stim REC offset.
        """

        return (
            measurement.record_idx
            - current_record_idx
            - 1
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
        round_idx: int,
        record_idx: int,
    ) -> int:
        """
        Add one round of syndrome extraction.
        """

        circuit.append(
            "R",
            self.ancilla_indices,
        )

        # X stabilizers
        for s, plaquette in enumerate(self.plaquettes):

            ancilla = self.x_ancilla_start + s

            self.add_x_stabilizer(
                circuit,
                ancilla,
                plaquette,
            )

            self.record_measurement(
                round_idx=round_idx,
                stabilizer_idx=s,
                record_idx=record_idx,
            )

            record_idx += 1

        # Z stabilizers
        for s, plaquette in enumerate(self.plaquettes):

            ancilla = self.z_ancilla_start + s

            self.add_z_stabilizer(
                circuit,
                ancilla,
                plaquette,
            )

            stabilizer_idx = len(self.plaquettes) + s

            self.record_measurement(
                round_idx=round_idx,
                stabilizer_idx=stabilizer_idx,
                record_idx=record_idx,
            )

            record_idx += 1

        return record_idx
        
    def add_round_detectors(
        self,
        circuit: stim.Circuit,
        round_idx: int,
        current_record_idx: int,
    ) -> None:

        if round_idx == 0:
            return

        for stabilizer_idx in range(
            self.n_stabilizers
        ):

            prev = self.get_measurement(
                round_idx - 1,
                stabilizer_idx,
            )

            curr = self.get_measurement(
                round_idx,
                stabilizer_idx,
            )

            circuit.append(
                "DETECTOR",
                [
                    stim.target_rec(
                        self.rec_offset(
                            prev,
                            current_record_idx,
                        )
                    ),
                    stim.target_rec(
                        self.rec_offset(
                            curr,
                            current_record_idx,
                        )
                    ),
                ],
            )

    def build_circuit(self) -> stim.Circuit:
        """
        Build a Stim surface-code circuit.
        """

        self.reset_measurements()
        record_idx = 0

        circuit = stim.Circuit()

        circuit.append(
            "R",
            range(self.n_qubits),
        )

        for round_idx in range(self.rounds):

            record_idx = self.add_syndrome_round(
                circuit,
                round_idx,
                record_idx,
            )

            self.add_round_detectors(
                circuit,
                round_idx,
                record_idx - 1,
            )

        return circuit

    def detector_error_model(
        self,
    ) -> stim.DetectorErrorModel:
        """
        Generate the detector error model.
        """

        return self.build_circuit().detector_error_model()