"""
Geometry and indexing utilities for planar surface codes.
"""

from dataclasses import dataclass

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


@dataclass(frozen=True)
class StabilizerGeometry:
    """
    Geometry describing a stabilizer in the
    checkerboard surface-code layout.
    """

    stabilizer_idx: int

    stabilizer_type: str

    ancilla_position: tuple[float, float]

    data_coordinates: tuple[
        tuple[int, int],
        ...
    ]

    data_qubits: tuple[int, ...]

    boundary: bool = False

    @property
    def weight(self):
        """
        Number of data qubits acted on by the stabilizer.
        """
        return len(self.data_qubits)


def generate_stabilizer_layout(
    distance: int,
) -> list[StabilizerGeometry]:
    """
    Generate the checkerboard stabilizer
    layout for a planar surface code.
    """

    stabilizers: list[
        StabilizerGeometry
    ] = []

    idx = 0

    for r in range(distance - 1):

        for c in range(distance - 1):

            coordinates = (
                (r, c),
                (r, c + 1),
                (r + 1, c),
                (r + 1, c + 1),
            )

            stabilizers.append(
                StabilizerGeometry(
                    stabilizer_idx=idx,

                    stabilizer_type=(
                        "X"
                        if (r + c) % 2 == 0
                        else "Z"
                    ),

                    ancilla_position=(
                        r + 0.5,
                        c + 0.5,
                    ),

                    data_coordinates=coordinates,

                    data_qubits=tuple(
                        d_idx(
                            rr,
                            cc,
                            distance,
                        )
                        for rr, cc in coordinates
                    ),

                    boundary=False,
                )
            )

            idx += 1

    return stabilizers


def generate_plaquettes(distance: int):
    """
    Generate all 2×2 plaquettes for the legacy
    Qiskit surface-code implementation.

    Notes
    -----
    This helper is retained for compatibility with
    the legacy circuit construction pipeline. The
    Stim backend uses `generate_stabilizer_layout()`
    instead.
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