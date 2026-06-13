from qec.geometry import (
    d_idx,
    manhattan,
    ANC_POS,
    N_DATA,
    N_X,
    N_Z,
    generate_plaquettes,
    generate_ancilla_positions,
)


def test_d_idx_distance_3():
    assert d_idx(0, 0, 3) == 0
    assert d_idx(0, 2, 3) == 2
    assert d_idx(1, 0, 3) == 3
    assert d_idx(2, 2, 3) == 8


def test_d_idx_distance_5():
    assert d_idx(0, 0, 5) == 0
    assert d_idx(0, 4, 5) == 4
    assert d_idx(1, 0, 5) == 5
    assert d_idx(4, 4, 5) == 24


def test_manhattan_distance():
    assert manhattan((0, 0), (0, 0)) == 0
    assert manhattan((0, 0), (1, 1)) == 2
    assert manhattan((0.5, 0.5), (1.5, 1.5)) == 2.0


def test_ancilla_positions():
    assert len(ANC_POS) == 4
    assert ANC_POS[0] == (0.5, 0.5)
    assert ANC_POS[3] == (1.5, 1.5)


def test_code_constants():
    assert N_DATA == 9
    assert N_X == 4
    assert N_Z == 4


def test_generate_plaquettes_d3():
    assert len(generate_plaquettes(3)) == 4


def test_generate_plaquettes_d5():
    assert len(generate_plaquettes(5)) == 16


def test_generate_ancilla_positions_d3():
    assert len(generate_ancilla_positions(3)) == 4


def test_generate_ancilla_positions_d5():
    assert len(generate_ancilla_positions(5)) == 16