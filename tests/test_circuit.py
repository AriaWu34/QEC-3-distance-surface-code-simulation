from qec.circuit import (
    one_round_surface_d3,
    k_rounds_surface_d3,
)

from qec.geometry import (
    N_DATA,
    N_X,
    N_Z,
)


def test_one_round_qubit_count():
    qc = one_round_surface_d3()

    assert qc.num_qubits == N_DATA + N_X + N_Z


def test_one_round_classical_bits():
    qc = one_round_surface_d3()

    assert qc.num_clbits == N_X + N_Z


def test_k_round_qubit_count():
    qc = k_rounds_surface_d3(3)

    assert qc.num_qubits == N_DATA + N_X + N_Z


def test_k_round_classical_bits():
    k = 3

    qc = k_rounds_surface_d3(k)

    assert qc.num_clbits == k * (N_X + N_Z)


def test_k_round_has_measurements():
    qc = k_rounds_surface_d3(2)

    measure_ops = qc.count_ops().get("measure", 0)

    assert measure_ops > 0


def test_k_round_has_resets():
    qc = k_rounds_surface_d3(2)

    reset_ops = qc.count_ops().get("reset", 0)

    assert reset_ops > 0