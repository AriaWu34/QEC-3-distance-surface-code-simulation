from qec.stim_backend import SurfaceCodeStimBackend

def test_stim_backend_builds_circuit():
    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=2,
    )

    circuit = backend.build_circuit()

    assert circuit.num_qubits == 17