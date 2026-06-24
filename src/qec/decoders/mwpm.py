"""
MWPM decoder implementations for surface-code simulations.

This module provides Minimum Weight Perfect Matching (MWPM)
decoding utilities for both single-round and space-time
syndrome decoding.

The decoder supports multiple backends:
- NetworkX-based MWPM for reference decoding
- PyMatching-based MWPM for Stim detector error models

All decoder implementations conform to the common
decoder interface defined in qec.decoders.base.
"""

import pymatching
import networkx as nx
from qec.geometry import (
    manhattan,
    generate_ancilla_positions,
    code_boundaries,
    code_sizes,
)
from qec.decoders.base import Decoder


class MWPMDecoder(Decoder):
    """
    Reference MWPM decoder implementation.

    Supports both NetworkX and PyMatching backends.
    """

    def __init__(
        self,
        backend: str = "networkx",
        dem=None,
    ):
        self.backend = backend

        self.matching = None

        if backend == "pymatching":

            if dem is None:
                raise ValueError(
                    "DEM required for "
                    "PyMatching backend."
                )

            self.matching = (
                pymatching.Matching
                .from_detector_error_model(
                    dem
                )
            )

        elif backend != "networkx":
            raise ValueError(
                f"Unknown backend: "
                f"{backend}"
            )


    def decode(
        self,
        bitstr: str,
        distance: int,
        k: int = 1,
    ) -> tuple[int, int]:
        return decode_one_shot(
            bitstr=bitstr,
            distance=distance,
            k=k,
        )

    def decode_spacetime(
        self,
        bitstr: str,
        distance: int,
        k: int,
    ) -> tuple[int, int]:
        return decode_spacetime_one_shot(
            bitstr=bitstr,
            distance=distance,
            k=k,
        )
    
    def decode_detection_events(
        self,
        detection_events,
    ):
        """
        Decode detector events using
        the PyMatching backend.
        """

        if self.backend != "pymatching":
            raise ValueError(
                "PyMatching backend required."
            )

        return self.matching.decode(
            detection_events
        )
    

# Boundary utilities
def distance_to_vertical_boundary(pos, distance):
    """
    Distance to the nearest top or bottom boundary.
    """
    bounds = code_boundaries(distance)

    return min(
        abs(pos[0] - bounds["top"]),
        abs(pos[0] - bounds["bottom"]),
    )


def distance_to_horizontal_boundary(pos, distance):
    """
    Distance to the nearest left or right boundary.
    """
    bounds = code_boundaries(distance)

    return min(
        abs(pos[1] - bounds["left"]),
        abs(pos[1] - bounds["right"]),
    )


# MWPM
def mwpm_pairs(
    defect_idxs: list[int],
    boundary_mode: str,
    distance: int,
):
    """
    Match syndrome defects using MWPM.
    """
    if not defect_idxs:
        return []

    anc_pos = generate_ancilla_positions(distance)

    G = nx.Graph()
    nodes = [f"a{i}" for i in defect_idxs]

    for u in nodes:
        G.add_node(u)

    add_B = (len(nodes) % 2 == 1)

    if add_B:
        G.add_node("B")

    # pairwise defect distances
    for i, u in enumerate(nodes):
        for j, v in enumerate(nodes):
            if j <= i:
                continue

            w = manhattan(
                anc_pos[int(u[1:])],
                anc_pos[int(v[1:])]
            )

            G.add_edge(u, v, weight=w)

    # connect defects to virtual boundary
    if add_B:
        for u in nodes:
            pos = anc_pos[int(u[1:])]

            if boundary_mode == "vertical":
                w = distance_to_vertical_boundary(pos, distance)
            else:
                w = distance_to_horizontal_boundary(pos, distance)

            G.add_edge(u, "B", weight=w)

    matching = nx.algorithms.matching.min_weight_matching(
        G,
        weight="weight"
    )

    if not matching:
        return []

    pairs = []

    for e in matching:
        u, v = tuple(e)
        pairs.append((u, v))

    return pairs


# Space-time utilities
def ancilla_pos_3d(
    idx: int,
    t: int,
    distance: int,
):
    """
    Return the space-time coordinates of an ancilla defect.
    """
    anc_pos = generate_ancilla_positions(distance)

    r, c = anc_pos[idx]

    return (r, c, t)


def mwpm_3d(
    defects,
    boundary_mode,
    distance,
):
    """
    Match space-time syndrome defects using MWPM.

    Defects are connected using Manhattan distance in
    space-time and may be paired to a virtual boundary.
    """
    anc_pos = generate_ancilla_positions(distance)
    bounds = code_boundaries(distance)

    G = nx.Graph()

    nodes = [f"a{a}_t{t}" for (a, t) in defects]

    for u in nodes:
        G.add_node(u)

    if len(nodes) % 2 == 1:
        G.add_node("B")

    # Complete graph among defects
    for i, u in enumerate(nodes):
        for j, v in enumerate(nodes):

            if j <= i:
                continue

            ai, ti = map(
                int,
                (u.split("_")[0][1:], u.split("_")[1][1:]),
            )

            aj, tj = map(
                int,
                (v.split("_")[0][1:], v.split("_")[1][1:]),
            )

            (ri, ci, ti), (rj, cj, tj) = (
                ancilla_pos_3d(ai, ti, distance),
                ancilla_pos_3d(aj, tj, distance),
            )

            w = (
                abs(ri - rj)
                + abs(ci - cj)
                + abs(ti - tj)
            )

            G.add_edge(u, v, weight=w)

    # Connect defects to virtual boundary
    if "B" in G.nodes:

        for u in nodes:

            ai, ti = map(
                int,
                (u.split("_")[0][1:], u.split("_")[1][1:]),
            )

            r, c = anc_pos[ai]

            if boundary_mode == "vertical":
                w = min(
                    abs(r - bounds["top"]),
                    abs(r - bounds["bottom"]),
                )
            else:
                w = min(
                    abs(c - bounds["left"]),
                    abs(c - bounds["right"]),
                )

            G.add_edge(u, "B", weight=w)

    matching = nx.algorithms.matching.min_weight_matching(
        G,
        weight="weight",
    )

    return list(matching) if matching is not None else []


from qec.syndrome import(
    split_into_rounds,
    parse_round_bits,
    defects_from_bits,
    spacetime_defects
)

# Decoding pipeline
def decode_one_shot(
    bitstr: str,
    distance: int,
    k: int = 1,
):
    """
    Decode the final syndrome round using MWPM.
    """
    _, n_x, n_z = code_sizes(distance)

    rounds = split_into_rounds(
        bitstr,
        k,
        n_x + n_z,
    )

    Xs, Zs = parse_round_bits(
        rounds[-1],
        n_x,
    )

    # Z-syndrome -> correct X errors -> logical-X test
    z_def = defects_from_bits(Zs)

    pairs_xcorr = mwpm_pairs(
        z_def,
        boundary_mode="vertical",
        distance=distance,
    )

    logX = correction_spans_code(
        pairs_xcorr,
        boundary_mode="vertical",
        distance=distance,
    )

    # X-syndrome -> correct Z errors -> logical-Z test
    x_def = defects_from_bits(Xs)

    pairs_zcorr = mwpm_pairs(
        x_def,
        boundary_mode="horizontal",
        distance=distance,
    )

    logZ = correction_spans_code(
        pairs_zcorr,
        boundary_mode="horizontal",
        distance=distance,
    )

    return int(logX), int(logZ)


def decode_spacetime_one_shot(
    bitstr: str,
    distance: int,
    k: int,
) -> tuple[int, int]:
    """
    Decode space-time syndrome defects using MWPM.
    """
    defects_Z, defects_X = spacetime_defects(
        bitstr,
        distance,
        k,
    )

    pairs_Z = mwpm_3d(
        defects_Z,
        boundary_mode="vertical",
        distance=distance,
    )

    pairs_X = mwpm_3d(
        defects_X,
        boundary_mode="horizontal",
        distance=distance,
    )

    logX = correction_spans_code(
        pairs_Z,
        boundary_mode="vertical",
        distance=distance,
    )

    logZ = correction_spans_code(
        pairs_X,
        boundary_mode="horizontal",
        distance=distance,
    )

    return int(logX), int(logZ)


# Logical checks
def correction_spans_code(
    pairs,
    boundary_mode: str,
    distance: int,
) -> bool:
    """
    Determine whether a matched correction chain spans the code.

    Used as a simple logical-failure heuristic.
    """

    bounds = code_boundaries(distance)
    anc_pos = generate_ancilla_positions(distance)

    for u, v in pairs:
        def axis(node):
            if node == "B":
                return (
                    bounds["top"]
                    if boundary_mode == "vertical"
                    else bounds["left"]
                )
            idx = int(node.split("_")[0][1:])
            pos = anc_pos[idx]
            return pos[0] if boundary_mode == "vertical" else pos[1]

        a, b = axis(u), axis(v)
        if abs(a - b) >= (bounds["span"] - 1.0):
            return True
    return False