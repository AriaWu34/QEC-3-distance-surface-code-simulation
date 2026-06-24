import pytest

from qec.decoders.mwpm import MWPMDecoder
from qec.stim_backend import SurfaceCodeStimBackend


def expected_detector_count(
    backend: SurfaceCodeStimBackend,
) -> int:

    num_memory_stabilizers = sum(
        s.stabilizer_type
        == backend.memory_basis
        for s in backend.stabilizers
    )

    return (
        backend.n_stabilizers
        * (backend.rounds - 1)
        + num_memory_stabilizers
    )


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
# Memory basis tests
# =========================

def test_invalid_memory_basis():

    with pytest.raises(ValueError):
        SurfaceCodeStimBackend(
            memory_basis="bad"
        )


def test_z_memory_has_one_observable():

    backend = SurfaceCodeStimBackend(
        distance=3,
        memory_basis="Z",
    )

    circuit = backend.build_circuit()

    observable_count = str(circuit).count(
        "OBSERVABLE_INCLUDE"
    )

    assert observable_count == 1


def test_x_memory_has_one_observable():

    backend = SurfaceCodeStimBackend(
        distance=3,
        memory_basis="X",
    )

    circuit = backend.build_circuit()

    observable_count = str(circuit).count(
        "OBSERVABLE_INCLUDE"
    )

    assert observable_count == 1


def test_x_memory_sampling_shape():

    backend = SurfaceCodeStimBackend(
        distance=3,
        memory_basis="X",
    )

    _, obs = (
        backend.sample_detectors_and_observables(
            shots=5
        )
    )

    assert obs.shape == (
        5,
        1,
    )


def test_x_memory_adds_final_detectors():

    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=5,
        memory_basis="X",
    )

    circuit = backend.build_circuit()

    detector_count = str(circuit).count(
        "DETECTOR"
    )

    num_x_stabilizers = sum(
        s.stabilizer_type == "X"
        for s in backend.stabilizers
    )

    expected = (
        backend.n_stabilizers
        * (backend.rounds - 1)
        + num_x_stabilizers
    )

    assert detector_count == expected


def test_x_memory_dem_builds():

    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=5,
        memory_basis="X",
    )

    dem = backend.detector_error_model()

    assert dem is not None


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

    assert detector_count == (
        expected_detector_count(
            backend
        )
    )


def test_final_detector_layer_present():

    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=5,
    )

    circuit = backend.build_circuit()

    detector_count = str(circuit).count(
        "DETECTOR"
    )

    assert detector_count == (
        expected_detector_count(
            backend
        )
    )


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


# =====================
# Sampling tests
# =====================

def test_detector_sampling_shape():
    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=5,
        depolarizing_error=0.01,
    )

    samples = backend.sample_detectors(
        shots=10
    )

    assert samples.shape == (
        10,
        expected_detector_count(
            backend
        ),
    )


def test_detector_and_observable_sampling_shapes():
    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=5,
        depolarizing_error=0.01,
    )

    dets, obs = (
        backend
        .sample_detectors_and_observables(
            shots=10
        )
    )

    assert dets.shape == (
        10,
        expected_detector_count(
            backend
        ),
    )

    assert obs.shape == (
        10,
        1,
    )


# =================
# PyMatching tests
# =================

def test_pymatching_decoder_builds():
    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=5,
        depolarizing_error=0.01,
    )

    decoder = MWPMDecoder(
        backend="pymatching",
        dem=backend.detector_error_model(),
    )

    assert decoder.matching is not None


def test_pymatching_decode_runs():
    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=5,
        depolarizing_error=0.01,
    )

    decoder = MWPMDecoder(
        backend="pymatching",
        dem=backend.detector_error_model(),
    )

    dets = backend.sample_detectors(
        shots=1
    )

    result = (
        decoder.decode_detection_events(
            dets[0]
        )
    )

    assert len(result) == 1