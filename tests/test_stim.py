import pytest

from qec.stim_backend import SurfaceCodeStimBackend


# =========================
# Construction tests
# =========================

def test_build_circuit_d3():
    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=1,
    )

    circuit = backend.build_circuit()

    assert circuit.num_qubits == 13


def test_build_circuit_d5():
    backend = SurfaceCodeStimBackend(
        distance=5,
        rounds=1,
    )

    circuit = backend.build_circuit()

    assert circuit.num_qubits == 41


def test_multiple_rounds_build():
    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=2,
    )

    circuit = backend.build_circuit()

    assert circuit.num_qubits == 13


# =========================
# Validation tests
# =========================

def test_invalid_distance():
    with pytest.raises(ValueError):
        SurfaceCodeStimBackend(distance=4)


def test_invalid_rounds():
    with pytest.raises(ValueError):
        SurfaceCodeStimBackend(
            distance=3,
            rounds=0,
        )


# =========================
# Detector tests
# =========================

def test_detector_count_d3_rounds_2():
    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=2,
    )

    circuit = backend.build_circuit()

    detector_count = str(circuit).count(
        "DETECTOR"
    )

    assert detector_count == backend.n_stabilizers


def test_detector_count_d3_rounds_3():
    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=3,
    )

    circuit = backend.build_circuit()

    detector_count = str(circuit).count(
        "DETECTOR"
    )

    assert detector_count == (
        backend.n_stabilizers * 2
    )


def test_detectors_present():
    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=2,
    )

    circuit = backend.build_circuit()

    assert "DETECTOR" in str(circuit)


# =========================
# Stabilizer metadata tests
# =========================

def test_get_stabilizer_info_x():
    backend = SurfaceCodeStimBackend(
        distance=3
    )

    info = backend.get_stabilizer_info(0)

    assert info.stabilizer_type == "X"
    assert info.plaquette_idx == 0


def test_get_stabilizer_info_z():
    backend = SurfaceCodeStimBackend(
        distance=3
    )

    info = backend.get_stabilizer_info(1)

    assert info.stabilizer_type == "Z"
    assert info.plaquette_idx == 1


def test_get_stabilizer_info_invalid():
    backend = SurfaceCodeStimBackend(
        distance=3
    )

    with pytest.raises(ValueError):
        backend.get_stabilizer_info(
            backend.n_stabilizers
        )


def test_stabilizer_metadata_mapping():
    backend = SurfaceCodeStimBackend(
        distance=3
    )

    for idx in range(
        backend.n_stabilizers
    ):
        info = backend.get_stabilizer_info(
            idx
        )

        assert (
            0
            <= info.plaquette_idx
            < len(backend.plaquettes)
        )

        assert info.stabilizer_type in {
            "X",
            "Z",
        }


def test_checkerboard_stabilizer_types_d3():
    backend = SurfaceCodeStimBackend(
        distance=3
    )

    types = [
        backend.get_stabilizer_info(i)
        .stabilizer_type
        for i in range(
            backend.n_stabilizers
        )
    ]

    assert types == [
        "X",
        "Z",
        "Z",
        "X",
    ]


def test_d3_stabilizer_count():
    backend = SurfaceCodeStimBackend(
        distance=3
    )

    assert backend.n_stabilizers == 4


def test_d5_stabilizer_count():
    backend = SurfaceCodeStimBackend(
        distance=5
    )

    assert backend.n_stabilizers == 16


# =========================
# Logical operator tests
# =========================

def test_logical_z_chain_length():
    backend = SurfaceCodeStimBackend(
        distance=3
    )

    chain = backend.logical_z_chain()

    assert len(chain) == backend.distance


def test_logical_x_chain_length():
    backend = SurfaceCodeStimBackend(
        distance=5
    )

    chain = backend.logical_x_chain()

    assert len(chain) == backend.distance


def test_final_data_measurements_recorded():
    backend = SurfaceCodeStimBackend(
        distance=3
    )

    backend.build_circuit()

    assert (
        len(
            backend.data_measurement_records
        )
        == backend.n_data
    )


def test_logical_chains_use_valid_data_qubits():
    backend = SurfaceCodeStimBackend(
        distance=3
    )

    for q in (
        backend.logical_z_chain()
        + backend.logical_x_chain()
    ):
        assert q in backend.data_indices


# ========================
# Logical observable tests
# ========================

def test_observables_present():
    backend = SurfaceCodeStimBackend(
        distance=3
    )

    circuit = backend.build_circuit()

    observable_count = str(circuit).count(
        "OBSERVABLE_INCLUDE"
    )

    assert observable_count == 2


def test_data_measurements_recorded():
    backend = SurfaceCodeStimBackend(
        distance=3
    )

    backend.build_circuit()

    assert (
        len(
            backend.data_measurement_records
        )
        == backend.n_data
    )


# =================
# Noise model tests
# =================

def test_invalid_depolarizing_error():
    with pytest.raises(ValueError):
        SurfaceCodeStimBackend(
            distance=3,
            depolarizing_error=-0.1,
        )


def test_depolarizing_error_present():
    backend = SurfaceCodeStimBackend(
        distance=3,
        depolarizing_error=0.01,
    )

    circuit = backend.build_circuit()

    assert "DEPOLARIZE1" in str(circuit)
    

def test_invalid_readout_error():
    with pytest.raises(ValueError):
        SurfaceCodeStimBackend(
            distance=3,
            readout_error=-0.1,
        )


def test_readout_error_present():
    backend = SurfaceCodeStimBackend(
        distance=3,
        readout_error=0.01,
    )

    circuit = backend.build_circuit()

    assert "X_ERROR" in str(circuit)