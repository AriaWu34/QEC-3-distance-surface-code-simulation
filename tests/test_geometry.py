from qec.geometry import (
    d_idx,
    manhattan,
    ANC_POS,
    N_DATA,
    N_X,
    N_Z,
)


def test_d_idx():
    assert d_idx(0, 0) == 0
    assert d_idx(0, 2) == 2
    assert d_idx(1, 0) == 3
    assert d_idx(2, 2) == 8


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