"""
Syndrome extraction and defect processing utilities.

Converts stabilizer measurement outcomes into syndrome defects for decoding.
"""

import numpy as np

from qec.geometry import code_sizes


def split_into_rounds(
    bitstr: str,
    k: int,
    n_stabilizers: int,
) -> list[str]:
    """
    Split a measurement string into k syndrome rounds.
    """
    s = bitstr.replace(" ", "")[::-1]

    return [
        s[i * n_stabilizers:(i + 1) * n_stabilizers]
        for i in range(k)
    ]


def parse_round_bits(
    round_bits: str,
    n_x: int,
) -> tuple[str, str]:
    """
    Return (X_bits, Z_bits) for a single syndrome round.
    """
    return round_bits[:n_x], round_bits[n_x:]


def defects_from_bits(bits: str) -> list[int]:
    """
    Return indices of stabilizers reporting syndrome 1.
    """
    return [i for i, b in enumerate(bits) if b == "1"]


def spacetime_defects(
    full_bitstr: str,
    distance: int,
    k: int,
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """
    Construct space-time defects for MWPM decoding.

    Consecutive syndrome rounds are compared, and changes in
    stabilizer outcomes are recorded as space-time defect events.
    """
    
    _, n_x, n_z = code_sizes(distance)

    n_stabilizers = n_x + n_z

    rounds = split_into_rounds(
        full_bitstr,
        k,
        n_stabilizers,
    )

    syn = np.array(
        [
            [int(b) for b in rb]
            for rb in rounds
        ]
    )

    defects_z = []
    defects_x = []

    for t in range(k - 1):

        # Z stabilizer changes
        diff_z = syn[t, n_x:] != syn[t + 1, n_x:]

        for i, changed in enumerate(diff_z):
            if changed:
                defects_z.append((i, t))

        # X stabilizer changes
        diff_x = syn[t, :n_x] != syn[t + 1, :n_x]

        for i, changed in enumerate(diff_x):
            if changed:
                defects_x.append((i, t))

    return defects_z, defects_x