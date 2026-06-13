"""
MWPM decoding utilities for surface-code simulations.

Provides 2D and space-time matching decoders based on
Minimum Weight Perfect Matching (MWPM).
"""

import networkx as nx
from qec.geometry import (
    d_idx,
    ANC_POS,
    TOP_Y,
    BOT_Y,
    LEFT_X,
    RIGHT_X,
    GRID_SPAN,
    manhattan,
)
from qec.syndrome import(
    split_into_rounds,
    parse_round_bits,
    defects_from_bits,
    spacetime_defects
)

# Boundary utilities
def distance_to_vertical_boundary(pos):
    """Distance to nearest TOP/BOTTOM boundary (use y)."""
    return min(abs(pos[0]-TOP_Y), abs(pos[0]-BOT_Y))

def distance_to_horizontal_boundary(pos):
    """Distance to nearest LEFT/RIGHT boundary (use x)."""
    return min(abs(pos[1]-LEFT_X), abs(pos[1]-RIGHT_X))

# MWPM
def mwpm_pairs(defect_idxs, boundary_mode):
    """
    defect_idxs: list of ancilla indices 0..3
    boundary_mode: 'vertical' (TOP/BOTTOM) or 'horizontal' (LEFT/RIGHT)
    returns list of pairs, nodes are 'a{i}' or 'B' (virtual boundary)
    """
    
    if not defect_idxs:
        return [] 

    G = nx.Graph()
    nodes = [f"a{i}" for i in defect_idxs]
    for u in nodes: G.add_node(u)

    # add boundary node for odd count
    add_B = (len(nodes) % 2 == 1)
    if add_B:
        G.add_node('B')

    # complete graph among defects
    for i,u in enumerate(nodes):
        for j,v in enumerate(nodes):
            if j <= i: continue
            w = manhattan(ANC_POS[int(u[1:])], ANC_POS[int(v[1:])])
            G.add_edge(u, v, weight=w)

    # complete graph among defects
    for i,u in enumerate(nodes):
        for j,v in enumerate(nodes):
            if j <= i: continue
            w = manhattan(ANC_POS[int(u[1:])], ANC_POS[int(v[1:])])
            G.add_edge(u, v, weight=w)

    # connect defects to boundary with appropriate distance
    if add_B:
        for u in nodes:
            pos = ANC_POS[int(u[1:])]
            w = (distance_to_vertical_boundary(pos) if boundary_mode == 'vertical' 
                 else distance_to_horizontal_boundary(pos))
            G.add_edge(u, 'B', weight=w)

    matching = nx.algorithms.matching.min_weight_matching(G, weight="weight")
    if not matching:
        return []

    # matching is a set of 2-tuples or frozensets; normalize to list of tuples
    pairs = []
    for e in matching:
        if len(e) != 2:    # just in case
            continue
        u, v = tuple(e)    # works for tuple or frozenset
        pairs.append((u, v))
    return pairs

# Space-time encoding
def ancilla_pos_3d(idx: int, t: int):
    r, c = ANC_POS[idx]
    return (r, c, t)

def mwpm_3d(defects: list[tuple[int,int]], boundary_mode: str, k: int):
    """
    defects: [(anc_idx, t)] with anc_idx in {0..3}, t in {0..k-2}
    boundary_mode: 'vertical' (for Z-syndrome → X errors) or 'horizontal' (for X-syndrome → Z errors)
    returns list of matched pairs; nodes are 'a{idx}_t{t}' or 'B' (boundary)
    """
    G = nx.Graph()
    nodes = [f"a{a}_t{t}" for (a, t) in defects]
    for u in nodes: G.add_node(u)

    # add virtual boundary if odd number of nodes
    if len(nodes) % 2 == 1:
        G.add_node('B')

    # complete graph among defects with L1 distance in space-time
    for i, u in enumerate(nodes):
        for j, v in enumerate(nodes):
            if j <= i: continue
            ai, ti = map(int, (u.split('_')[0][1:], u.split('_')[1][1:]))
            aj, tj = map(int, (v.split('_')[0][1:], v.split('_')[1][1:]))
            (ri, ci, ti), (rj, cj, tj) = ancilla_pos_3d(ai, ti), ancilla_pos_3d(aj, tj)
            w = abs(ri - rj) + abs(ci - cj) + abs(ti - tj)
            G.add_edge(u, v, weight=w)

    # connect to spatial boundary (not temporal; shots are fixed-length)
    if 'B' in G.nodes:
        for u in nodes:
            ai, ti = map(int, (u.split('_')[0][1:], u.split('_')[1][1:]))
            r, c = ANC_POS[ai]
            if boundary_mode == 'vertical':
                w = min(abs(r - TOP_Y), abs(r - BOT_Y))
            else:
                w = min(abs(c - LEFT_X), abs(c - RIGHT_X))
            G.add_edge(u, 'B', weight=w)

    matching = nx.algorithms.matching.min_weight_matching(G, weight="weight")
    return list(matching) if matching is not None else []

# Decoding pipeline
def decode_one_shot(bitstr, k=1):
    """
    Returns (logical_X_fail, logical_Z_fail) using the LAST round only.
    """
    rounds = split_into_rounds(bitstr, k)
    Xs, Zs = parse_round_bits(rounds[-1])  # last round
    # Z-syndrome -> correct X errors -> logical-X test (vertical boundaries)
    z_def = defects_from_bits(Zs)
    pairs_xcorr = mwpm_pairs(z_def, boundary_mode='vertical')
    logX = correction_spans_code(pairs_xcorr, boundary_mode='vertical')

    # X-syndrome -> correct Z errors -> logical-Z test (horizontal boundaries)
    x_def = defects_from_bits(Xs)
    pairs_zcorr = mwpm_pairs(x_def, boundary_mode='horizontal')
    logZ = correction_spans_code(pairs_zcorr, boundary_mode='horizontal')

    return int(logX), int(logZ)

def decode_spacetime_one_shot(bitstr: str, k: int) -> tuple[int, int]:
    """
    Returns (logX, logZ): 1 if logical-X/Z failure is detected, else 0.
    """
    defects_Z, defects_X = spacetime_defects(bitstr, k)
    pairs_Z = mwpm_3d(defects_Z, boundary_mode='vertical',   k=k)   # logical-X risk
    pairs_X = mwpm_3d(defects_X, boundary_mode='horizontal', k=k)   # logical-Z risk
    logX = correction_spans_code(pairs_Z, 'vertical')
    logZ = correction_spans_code(pairs_X, 'horizontal')
    return int(logX), int(logZ)

# Logical checks
def correction_spans_code(pairs, boundary_mode: str) -> bool:
    """
    crude homology test for d=3:
    return True if any correction pair likely spans across the code in the relevant direction.
    """
    for u, v in pairs:
        def axis(node):
            if node == 'B':
                return TOP_Y if boundary_mode == 'vertical' else LEFT_X
            idx = int(node.split('_')[0][1:])
            pos = ANC_POS[idx]
            return pos[0] if boundary_mode == 'vertical' else pos[1]

        a, b = axis(u), axis(v)
        if abs(a - b) >= (GRID_SPAN - 1.0):
            return True
    return False