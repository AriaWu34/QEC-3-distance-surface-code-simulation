"""
Geometry and indexing utilities for planar surface codes.
"""

DEFAULT_DISTANCE = 3


def code_sizes(distance: int):
    """
    Return the number of data, X-ancilla, and Z-ancilla qubits.
    """
    n_data = distance**2
    n_x = (distance - 1) ** 2
    n_z = (distance - 1) ** 2

    return n_data, n_x, n_z


def ancilla_offsets(distance: int):
    """
    Return the starting indices of X and Z ancillas.
    """
    n_data, n_x, _ = code_sizes(distance)

    x_start = n_data
    z_start = n_data + n_x

    return x_start, z_start


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


def generate_plaquettes(distance: int):
    """
    Generate all 2x2 plaquettes for a distance-d planar code.
    """
    plaqs = []

    for r in range(distance - 1):
        for c in range(distance - 1):
            plaqs.append(
                [
                    (r, c),
                    (r, c + 1),
                    (r + 1, c),
                    (r + 1, c + 1),
                ]
            )

    return plaqs


# Backward compatibility for d=3
PLAQS = generate_plaquettes(DEFAULT_DISTANCE)


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


# Backward compatibility for d=3
ANC_POS = generate_ancilla_positions(DEFAULT_DISTANCE)


# Logical boundaries used by the decoder
# (still fixed to d=3 for now; will be generalized later)
TOP_Y, BOT_Y = -0.5, 2.5
LEFT_X, RIGHT_X = -0.5, 2.5
GRID_SPAN = 3.0


def manhattan(p: tuple, q: tuple) -> float:
    """
    Manhattan distance between two coordinates.
    """
    return abs(p[0] - q[0]) + abs(p[1] - q[1])


def code_boundaries(distance: int):
    """
    Return decoder boundary coordinates.
    """
    low = -0.5
    high = distance - 0.5

    return {
        "top": low,
        "bottom": high,
        "left": low,
        "right": high,
        "span": float(distance),
    }


def validate_distance(distance: int):
    if distance < 3 or distance % 2 == 0:
        raise ValueError(
            "Distance must be an odd integer >= 3."
        )