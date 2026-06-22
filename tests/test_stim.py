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

    assert circuit.num_qubits == 17


def test_build_circuit_d5():
    backend = SurfaceCodeStimBackend(
        distance=5,
        rounds=1,
    )

    circuit = backend.build_circuit()

    assert circuit.num_qubits == 57


def test_multiple_rounds_build():
    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=2,
    )

    circuit = backend.build_circuit()

    assert circuit.num_qubits == 17


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

    info = backend.get_stabilizer_info(
        len(backend.plaquettes)
    )

    assert info.stabilizer_type == "Z"
    assert info.plaquette_idx == 0


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