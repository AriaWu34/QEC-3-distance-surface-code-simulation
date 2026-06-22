from qec.stim_backend import SurfaceCodeStimBackend


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


def test_invalid_distance():
    import pytest

    with pytest.raises(ValueError):
        SurfaceCodeStimBackend(distance=4)


def test_invalid_rounds():
    import pytest

    with pytest.raises(ValueError):
        SurfaceCodeStimBackend(
            distance=3,
            rounds=0,
        )

def test_detectors_added():
    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=2,
    )

    circuit = backend.build_circuit()

    assert "DETECTOR" in str(circuit)