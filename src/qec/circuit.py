"""
Circuit construction utilities for surface-code simulations.
"""

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qec.geometry import (
    d_idx,
    code_sizes,
    ancilla_offsets,
    generate_plaquettes,
)

def one_round_surface_code(distance: int = 3):
    """
    Construct a single-round planar surface-code syndrome extraction circuit.

    Parameters
    ----------
    distance : int, optional
        Surface-code distance. Defaults to 3.
    """

    n_data, n_x, n_z = code_sizes(distance)
    x_start, z_start = ancilla_offsets(distance)
    plaqs = generate_plaquettes(distance)

    qreg = QuantumRegister(n_data + n_x + n_z, "q")
    creg = ClassicalRegister(n_x + n_z, "syn")
    qc = QuantumCircuit(qreg, creg)

    # --- X stabilizers (measure XXXX) ---
    for s, plaq in enumerate(plaqs):
        a = x_start + s  # ancilla index
        qc.h(a)          # prepare |+>
        for (r,c) in plaq:
            qc.cx(a, d_idx(r, c, distance))      # CNOT ancilla -> data (parity of X)
        qc.h(a)                       # return to Z basis
        qc.measure(a, s)              # measure into syn[0..3]

    # --- Z stabilizers (measure ZZZZ) ---
    for s, plaq in enumerate(plaqs):
        a = z_start + s
        for (r,c) in plaq:
            qc.cx(d_idx(r, c, distance), a)     # parity of Z
        qc.measure(a, n_x + s)        # measure into syn[4..7]

    return qc


def k_rounds_surface_code(distance: int = 3, k: int = 1) -> QuantumCircuit:
    """
    Construct a planar surface-code circuit with multiple rounds of
    syndrome extraction.

    Parameters
    ----------
    distance : int, optional
        Surface-code distance. Defaults to 3.

    k : int, optional
        Number of syndrome-extraction rounds.
    """

    n_data, n_x, n_z = code_sizes(distance)
    x_start, z_start = ancilla_offsets(distance)
    plaqs = generate_plaquettes(distance)

    qreg = QuantumRegister(n_data + n_x + n_z, "q")
    qc = QuantumCircuit(qreg)

    for r in range(k):
        # simple memory error opportunity on data (lets 'id' pick up depolarizing)
        for q in range(n_data): 
            qc.id(q)
        syn = ClassicalRegister(n_x + n_z, f"syn_{r}")
        qc.add_register(syn)

        # --- X stabilizers: ancilla -> data (H, CNOTs, H, measure), reset ancilla
        for s, plaq in enumerate(plaqs):
            a = x_start + s
            qc.reset(qreg[a])
            qc.h(qreg[a])
            for (row, col) in plaq:
                qc.cx(qreg[a], qreg[d_idx(row, col, distance)])
            qc.h(qreg[a])
            qc.measure(qreg[a], syn[s])  # X syndrome bit s
            # (reset done above; no reset after measure needed)

        # --- Z stabilizers: data -> ancilla (CNOTs), measure, reset ancilla
        for s, plaq in enumerate(plaqs):
            a = z_start + s
            qc.reset(qreg[a])
            for (row, col) in plaq:
                qc.cx(qreg[d_idx(row, col, distance)], qreg[a])
            qc.measure(qreg[a], syn[n_x + s])  # Z syndrome bit s

    return qc