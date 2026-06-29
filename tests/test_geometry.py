import pytest
from qec.geometry import (
    d_idx,
    manhattan,
    ANC_POS,
    code_sizes,
    generate_stabilizer_layout,
    generate_plaquettes,
    generate_ancilla_positions,
    code_boundaries,
    validate_distance,
)


# =========================
# CGeometry indexing
# =========================

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


# =========================
# Code parameters
# =========================

def test_code_sizes_d3():
    n_data, n_x, n_z = code_sizes(3)

    assert n_data == 9
    assert n_x == 4
    assert n_z == 4


def test_code_sizes_d5():
    n_data, n_x, n_z = code_sizes(5)

    assert n_data == 25
    assert n_x == 16
    assert n_z == 16


def test_code_boundaries_d3():
    bounds = code_boundaries(3)

    assert bounds["top"] == -0.5
    assert bounds["bottom"] == 2.5
    assert bounds["left"] == -0.5
    assert bounds["right"] == 2.5
    assert bounds["span"] == 3.0


def test_code_boundaries_d5():
    bounds = code_boundaries(5)

    assert bounds["top"] == -0.5
    assert bounds["bottom"] == 4.5
    assert bounds["left"] == -0.5
    assert bounds["right"] == 4.5
    assert bounds["span"] == 5.0
    

def test_validate_distance_rejects_invalid():
    with pytest.raises(ValueError):
        validate_distance(2)

    with pytest.raises(ValueError):
        validate_distance(4)

    with pytest.raises(ValueError):
        validate_distance(0)    


# =========================
# Stabilizer geometry
# =========================

def test_checkerboard_layout_d3():
    layout = generate_stabilizer_layout(3)

    types = [
        s.stabilizer_type
        for s in layout
    ]

    assert types == [
        "X",
        "Z",
        "Z",
        "X",
    ]


def test_stabilizer_has_data_qubits():

    layout = generate_stabilizer_layout(3)

    assert layout[0].data_qubits == (
        0,
        1,
        3,
        4,
    )


def test_stabilizer_has_data_coordinates():

    layout = generate_stabilizer_layout(3)

    assert (
        layout[0].data_coordinates
        ==
        (
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
        )
    )


def test_stabilizer_has_ancilla_position():

    layout = generate_stabilizer_layout(3)

    assert (
        layout[0].ancilla_position
        ==
        (0.5, 0.5)
    )


def test_stabilizer_not_boundary():

    layout = generate_stabilizer_layout(3)

    assert layout[0].boundary is False


def test_stabilizer_geometry_consistency():

    layout = generate_stabilizer_layout(5)

    for stabilizer in layout:

        assert len(stabilizer.data_qubits) == 4
        assert len(stabilizer.data_coordinates) == 4

        assert (
            len(set(stabilizer.data_qubits))
            == 4
        )

        assert (
            len(set(stabilizer.data_coordinates))
            == 4
        )


# =========================
# Legacy compatibility
# =========================

def test_generate_plaquettes_d3():
    assert len(generate_plaquettes(3)) == 4


def test_generate_plaquettes_d5():
    assert len(generate_plaquettes(5)) == 16


def test_generate_ancilla_positions_d3():
    assert len(generate_ancilla_positions(3)) == 4


def test_generate_ancilla_positions_d5():
    assert len(generate_ancilla_positions(5)) == 16