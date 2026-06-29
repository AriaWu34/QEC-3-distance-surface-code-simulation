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
    generate_stabilizer_layout,
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

@dataclass(frozen=True)
class StabilizerInfo:
    """
    Metadata describing a stabilizer.
    """

    stabilizer_idx: int
    stabilizer_type: str
    plaquette_idx: int

class SurfaceCodeStimBackend:
    """
    Stim implementation of the planar surface code.
    """

    def __init__(
        self,
        distance: int = 3,
        rounds: int = 1,
        depolarizing_error: float = 0.0,
        readout_error: float = 0.0,
        memory_basis: str = "Z",
    ):
        validate_distance(distance)

        if rounds < 1:
            raise ValueError(
                "Rounds must be >= 1."
            )
        
        if memory_basis not in {"X", "Z"}:
            raise ValueError(
                "memory_basis must be 'X' or 'Z'."
            )

        self.memory_basis = memory_basis
        
        for p in (
            depolarizing_error,
            readout_error,
        ):
            if not 0.0 <= p <= 1.0:
                raise ValueError(
                    "Error probabilities must be in [0,1]."
                )

        self.distance = distance
        self.rounds = rounds
        self.depolarizing_error = depolarizing_error
        self.readout_error = readout_error

        self.stabilizers = generate_stabilizer_layout(distance)

        self.plaquettes = generate_plaquettes(distance)

        self.n_data, self.n_x, self.n_z = code_sizes(distance)

        self.measurements: dict[
            tuple[int, int],
            StabilizerMeasurement,
        ] = {}

        self.data_measurement_records: dict[
            int,
            int,
        ] = {}

    @property
    def n_qubits(self) -> int:
        return self.n_data + self.n_stabilizers

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
    def n_stabilizers(self):
        return len(self.stabilizers)
    
    @property
    def stabilizer_ancilla_start(self) -> int:
        return self.n_data
    

    def get_stabilizer_info(
        self,
        stabilizer_idx: int,
    ) -> StabilizerInfo:
        """
        Return metadata for a stabilizer in the
        checkerboard layout.

        Provides the stabilizer type (X or Z)
        and the associated plaquette index.
        """

        if not (
            0 <= stabilizer_idx
            < len(self.stabilizers)
        ):
            raise ValueError(
                f"Invalid stabilizer index: "
                f"{stabilizer_idx}"
            )

        stabilizer = self.stabilizers[
            stabilizer_idx
        ]

        return StabilizerInfo(
            stabilizer_idx=stabilizer.stabilizer_idx,
            stabilizer_type=stabilizer.stabilizer_type,
            plaquette_idx=stabilizer.plaquette_idx,
        )

    def reset_measurements(self) -> None:
        """
        Clear measurement bookkeeping.
        """

        self.measurements.clear()
        self.data_measurement_records.clear()
    
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
    
    def rec_offset_from_record(
        self,
        record_idx: int,
        current_record_idx: int,
    ) -> int:
        """
        Convert a raw measurement record index
        into a Stim REC offset.
        """

        return (
            record_idx
            - current_record_idx
            - 1
        )

    def add_x_stabilizer(
        self,
        circuit: stim.Circuit,
        ancilla: int,
        coordinates: tuple[
            tuple[int, int],
            ...
        ],
    ) -> None:
        """
        Add an X-stabilizer measurement.
        """

        circuit.append("H", [ancilla])

        for row, col in coordinates:
            circuit.append(
                "CX",
                [
                    ancilla,
                    self.data_idx(row, col),
                ],
            )

        circuit.append("H", [ancilla])

        self.add_readout_error(
            circuit,
            ancilla,
        )

        circuit.append(
            "M",
            [ancilla],
        )

    def add_z_stabilizer(
        self,
        circuit: stim.Circuit,
        ancilla: int,
        coordinates: tuple[
            tuple[int, int],
            ...
        ],
    ) -> None:
        """
        Add a Z-stabilizer measurement.
        """

        for row, col in coordinates:
            circuit.append(
                "CX",
                [
                    self.data_idx(row, col),
                    ancilla,
                ],
            )

        self.add_readout_error(
            circuit,
            ancilla,
        )

        circuit.append(
            "M",
            [ancilla],
        )

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

        for stabilizer in self.stabilizers:

            ancilla = (
                self.stabilizer_ancilla_start
                + stabilizer.stabilizer_idx
            )

            coordinates = (
                stabilizer.data_coordinates
            )

            if stabilizer.stabilizer_type == "X":

                self.add_x_stabilizer(
                    circuit,
                    ancilla,
                    coordinates,
                )

            else:

                self.add_z_stabilizer(
                    circuit,
                    ancilla,
                    coordinates,
                )

            self.record_measurement(
                round_idx=round_idx,
                stabilizer_idx=(
                    stabilizer.stabilizer_idx
                ),
                record_idx=record_idx,
            )

            record_idx += 1

        self.add_depolarizing_noise(
            circuit,
            self.data_indices,
        )

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

            stabilizer = self.stabilizers[
                stabilizer_idx
            ]

            x, y = (
                stabilizer.ancilla_position
            )

            basis = (
                0.0
                if stabilizer.stabilizer_type == "X"
                else 1.0
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
                [
                    x,
                    y,
                    float(round_idx),
                    basis,
                ],
            )

    def add_final_detectors(
        self,
        circuit: stim.Circuit,
        current_record_idx: int,
    ) -> None:
        """
        Add the final detector layer for a logical
        memory experiment.
        """

        last_round = self.rounds - 1

        stabilizer_type = self.memory_basis

        basis_coord = (
            0.0
            if stabilizer_type == "X"
            else 1.0
        )

        for stabilizer_idx in range(
            self.n_stabilizers
        ):

            stabilizer = self.stabilizers[
                stabilizer_idx
            ]

            if (
                stabilizer.stabilizer_type
                != stabilizer_type
            ):
                continue

            coordinates = (
                stabilizer.data_coordinates
            )

            syndrome_record = self.get_measurement(
                last_round,
                stabilizer_idx,
            )

            targets = [
                stim.target_rec(
                    self.rec_offset(
                        syndrome_record,
                        current_record_idx,
                    )
                )
            ]

            for r, c in coordinates:

                data_qubit = self.data_idx(
                    r,
                    c,
                )

                data_record = (
                    self.data_measurement_records[
                        data_qubit
                    ]
                )

                targets.append(
                    stim.target_rec(
                        self.rec_offset_from_record(
                            data_record,
                            current_record_idx,
                        )
                    )
                )

            x, y = (
                stabilizer.ancilla_position
            )

            circuit.append(
                "DETECTOR",
                targets,
                [
                    x,
                    y,
                    float(self.rounds),
                    basis_coord,
                ],
            )

    def prepare_logical_state(
        self,
        circuit,
    ):
        """
        Prepare the logical memory state.
        """

        if self.memory_basis == "Z":
            return

        if self.memory_basis == "X":
            circuit.append(
                "H",
                self.data_indices,
            )

    def build_circuit(self) -> stim.Circuit:
        """
        Build a Stim surface-code circuit for a
        logical memory experiment.
        """

        self.reset_measurements()

        record_idx = 0

        circuit = stim.Circuit()

        circuit.append(
            "R",
            range(self.n_qubits),
        )

        self.prepare_logical_state(
            circuit
        )

        for round_idx in range(
            self.rounds
        ):

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

        record_idx = (
            self.add_final_data_measurements(
                circuit,
                record_idx,
            )
        )

        self.add_final_detectors(
            circuit,
            record_idx - 1,
        )

        if self.memory_basis == "Z":

            self.add_logical_z_observable(
                circuit,
                record_idx - 1,
            )

        elif self.memory_basis == "X":

            self.add_logical_x_observable(
                circuit,
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
    
    def logical_z_chain(self) -> list[int]:
        """
        Data qubits forming the logical Z operator.
        """

        return [
            self.data_idx(r, 0)
            for r in range(self.distance)
        ]
    
    def logical_x_chain(self) -> list[int]:
        """
        Data qubits forming the logical X operator.
        """

        return [
            self.data_idx(0, c)
            for c in range(self.distance)
        ]
        
    def measure_data_qubits(
        self,
        circuit,
    ):
        """
        Measure data qubits in the
        memory basis.
        """

        if self.memory_basis == "Z":

            circuit.append(
                "M",
                self.data_indices,
            )

        elif self.memory_basis == "X":

            circuit.append(
                "H",
                self.data_indices,
            )

            circuit.append(
                "M",
                self.data_indices,
            )

    def add_final_data_measurements(
        self,
        circuit: stim.Circuit,
        record_idx: int,
    ) -> int:

        if self.readout_error > 0:
            circuit.append(
                "X_ERROR",
                self.data_indices,
                self.readout_error,
            )

        self.measure_data_qubits(
            circuit
        )

        for q in self.data_indices:
            self.data_measurement_records[q] = record_idx
            record_idx += 1

        return record_idx
    
    def add_logical_z_observable(
        self,
        circuit: stim.Circuit,
        current_record_idx: int,
    ) -> None:
        
        targets: list[stim.GateTarget] = []

        for q in self.logical_z_chain():

            record_idx = (
                self.data_measurement_records[q]
            )

            targets.append(
                stim.target_rec(
                    self.rec_offset_from_record(
                        record_idx,
                        current_record_idx,
                    )
                )
            )

        circuit.append(
            "OBSERVABLE_INCLUDE",
            targets,
            0,
        )

    def add_logical_x_observable(
        self,
        circuit: stim.Circuit,
        current_record_idx: int,
    ) -> None:

        targets: list[stim.GateTarget] = []

        for q in self.logical_x_chain():

            record_idx = (
                self.data_measurement_records[q]
            )

            targets.append(
                stim.target_rec(
                    self.rec_offset_from_record(
                        record_idx,
                        current_record_idx,
                    )
                )
            )

        circuit.append(
            "OBSERVABLE_INCLUDE",
            targets,
            0,
        )

    def add_depolarizing_noise(
        self,
        circuit: stim.Circuit,
        qubits,
    ) -> None:
        if self.depolarizing_error == 0:
            return

        circuit.append(
            "DEPOLARIZE1",
            qubits,
            self.depolarizing_error,
        )

    def add_readout_error(
        self,
        circuit: stim.Circuit,
        qubit: int,
    ) -> None:
        """
        Apply measurement error before
        a measurement operation.
        """

        if self.readout_error == 0:
            return

        circuit.append(
            "X_ERROR",
            [qubit],
            self.readout_error,
        )


    def compile_detector_sampler(
        self,
    ) -> stim.CompiledDetectorSampler:
        """
        Compile a detector sampler for the circuit.
        """

        return (
            self.build_circuit()
            .compile_detector_sampler()
        )

    def sample_detectors(
        self,
        shots: int,
    ):
        """
        Sample detector outcomes.
        """

        sampler = (
            self.compile_detector_sampler()
        )

        return sampler.sample(shots)
    
    def sample_detectors_and_observables(
        self,
        shots: int,
    ):
        """
        Sample detector outcomes and
        logical observables.
        """

        sampler = (
            self.build_circuit()
            .compile_detector_sampler()
        )

        return sampler.sample(
            shots,
            separate_observables=True,
        )