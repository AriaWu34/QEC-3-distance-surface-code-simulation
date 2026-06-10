"""
Geometry and indexing utilities for the distance-3 surface code.
"""

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


def d_idx(r: int, c: int) -> int:
    """
    Convert a 2D data-qubit coordinate into a linear index.
    """
    return 3 * r + c


# Plaquette definitions for the distance-3 code
PLAQS = [
    [(0, 0), (0, 1), (1, 0), (1, 1)],
    [(0, 1), (0, 2), (1, 1), (1, 2)],
    [(1, 0), (1, 1), (2, 0), (2, 1)],
    [(1, 1), (1, 2), (2, 1), (2, 2)],
]


# Ancilla positions for the 4 plaquettes (both X and Z stabilizers share geometry on d=3)
# Centers at (row+0.5, col+0.5) for the four 2x2 blocks:
ANC_POS = {
    0: (0.5, 0.5),
    1: (0.5, 1.5),
    2: (1.5, 0.5),
    3: (1.5, 1.5),
}


# Logical boundaries used by the decoder
TOP_Y, BOT_Y = -0.5, 2.5          # rough (Z-syndrome → correct X errors → logical X)
LEFT_X, RIGHT_X = -0.5, 2.5       # smooth (X-syndrome → correct Z errors → logical Z)
GRID_SPAN = 3.0                   # distance across the code (rows or cols 0..2 → span ~3)


def manhattan(p, q):
    """
    Manhattan distance between two coordinates.
    """
    return abs(p[0] - q[0]) + abs(p[1] - q[1])