"""
Geometry and indexing utilities for the distance-3 surface code.
"""

DEFAULT_DISTANCE = 3

# Distance-3 code layout constants
N_DATA = 9
N_X = 4
N_Z = 4

# Ancilla qubit indices in the circuit register
X_START = N_DATA
Z_START = N_DATA + N_X


# Data qubit indexing:
#
# (0,0) (0,1) (0,2)
# (1,0) (1,1) (1,2)
# (2,0) (2,1) (2,2)
#
# ->
#
# 0 1 2
# 3 4 5
# 6 7 8

def d_idx(r: int, c: int, distance: int) -> int:
    """
    Convert a 2D data-qubit coordinate into a linear index.
    """
    return distance * r + c


# Plaquette definitions for the distance-3 code
PLAQS = [
    [(0, 0), (0, 1), (1, 0), (1, 1)],
    [(0, 1), (0, 2), (1, 1), (1, 2)],
    [(1, 0), (1, 1), (2, 0), (2, 1)],
    [(1, 1), (1, 2), (2, 1), (2, 2)],
]

def generate_plaquettes(distance: int):
    """
    Generate all 2x2 plaquettes for a distance-d planar code.
    """
    plaqs = []

    for r in range(distance - 1):
        for c in range(distance - 1):
            plaqs.append([
                (r, c),
                (r, c + 1),
                (r + 1, c),
                (r + 1, c + 1),
            ])

    return plaqs


# Ancilla positions for the 4 plaquettes
ANC_POS = {
    0: (0.5, 0.5),
    1: (0.5, 1.5),
    2: (1.5, 0.5),
    3: (1.5, 1.5),
}

def generate_ancilla_positions(distance: int):
    """
    Generate ancilla coordinates for all plaquettes.
    """
    pos = {}

    idx = 0

    for r in range(distance - 1):
        for c in range(distance - 1):
            pos[idx] = (r + 0.5, c + 0.5)
            idx += 1

    return pos


# Logical boundaries used by the decoder
TOP_Y, BOT_Y = -0.5, 2.5          # rough (Z-syndrome → correct X errors → logical X)
LEFT_X, RIGHT_X = -0.5, 2.5       # smooth (X-syndrome → correct Z errors → logical Z)
GRID_SPAN = 3.0                   # distance across the code (rows or cols 0..2 → span ~3)


def manhattan(p: tuple, q: tuple) -> float:
    """
    Manhattan distance between two coordinates.
    """
    return abs(p[0] - q[0]) + abs(p[1] - q[1])