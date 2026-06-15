from qec.circuit import (
    one_round_surface_d3,
    k_rounds_surface_d3,
    one_round_surface_code,
    k_rounds_surface_code,
)

from qec.geometry import code_sizes


def test_one_round_surface_code_d3():
    qc = one_round_surface_code(distance=3)

    assert qc.num_qubits == 17
    assert qc.num_clbits == 8


def test_one_round_surface_code_d5():
    qc = one_round_surface_code(distance=5)

    assert qc.num_qubits == 57
    assert qc.num_clbits == 32


def test_k_rounds_surface_code_d5():
    qc = k_rounds_surface_code(distance=5, k=3)

    assert qc.num_qubits == 57
    assert qc.num_clbits == 96


def test_one_round_qubit_count():
    n_data, n_x, n_z = code_sizes(3)

    qc = one_round_surface_d3()

    assert qc.num_qubits == n_data + n_x + n_z


def test_one_round_classical_bits():
    _, n_x, n_z = code_sizes(3)

    qc = one_round_surface_d3()

    assert qc.num_clbits == n_x + n_z


def test_k_round_qubit_count():
    n_data, n_x, n_z = code_sizes(3)

    qc = k_rounds_surface_d3(3)

    assert qc.num_qubits == n_data + n_x + n_z


def test_k_round_classical_bits():
    _, n_x, n_z = code_sizes(3)

    k = 3
    qc = k_rounds_surface_d3(k)

    assert qc.num_clbits == k * (n_x + n_z)


def test_k_round_has_measurements():
    qc = k_rounds_surface_d3(2)

    assert qc.count_ops().get("measure", 0) > 0


def test_k_round_has_resets():
    qc = k_rounds_surface_d3(2)

    assert qc.count_ops().get("reset", 0) > 0