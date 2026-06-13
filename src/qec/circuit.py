"""
Circuit construction utilities for surface-code simulations.
"""

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qec.geometry import d_idx, PLAQS, N_DATA, N_X, N_Z, X_START, Z_START

def one_round_surface_d3():
    """
    Returns a circuit with:
      - 9 data qubits
      - 4 X-ancillas (indices 9..12), 4 Z-ancillas (indices 13..16)
      - 8 classical bits storing [X syndromes | Z syndromes]
    """

    qreg = QuantumRegister(N_DATA + N_X + N_Z, "q")
    creg = ClassicalRegister(N_X + N_Z, "syn")  # [X | Z]
    qc = QuantumCircuit(qreg, creg)

    # --- X stabilizers (measure XXXX) ---
    for s, plaq in enumerate(PLAQS):
        a = X_START + s  # ancilla index
        qc.h(a)          # prepare |+>
        for (r,c) in plaq:
            qc.cx(a, d_idx(r,c))      # CNOT ancilla -> data (parity of X)
        qc.h(a)                       # return to Z basis
        qc.measure(a, s)              # measure into syn[0..3]

    # --- Z stabilizers (measure ZZZZ) ---
    for s, plaq in enumerate(PLAQS):
        a = Z_START + s
        for (r,c) in plaq:
            qc.cx(d_idx(r,c), a)      # parity of Z
        qc.measure(a, N_X + s)        # measure into syn[4..7]

    return qc


def k_rounds_surface_d3(k: int) -> QuantumCircuit:
    """
    Build d=3 planar surface-code circuit with k rounds of syndrome extraction.
    """
    qreg = QuantumRegister(N_DATA + N_X + N_Z, "q")
    qc = QuantumCircuit(qreg)

    for r in range(k):
        # simple memory error opportunity on data (lets 'id' pick up depolarizing)
        for q in range(9): 
            qc.id(q)
        syn = ClassicalRegister(N_X + N_Z, f"syn_{r}")  # 8 bits for this round
        qc.add_register(syn)

        # --- X stabilizers: ancilla -> data (H, CNOTs, H, measure), reset ancilla
        for s, plaq in enumerate(PLAQS):
            a = X_START + s
            qc.reset(qreg[a])
            qc.h(qreg[a])
            for (row, col) in plaq:
                qc.cx(qreg[a], qreg[d_idx(row, col)])
            qc.h(qreg[a])
            qc.measure(qreg[a], syn[s])  # X syndrome bit s
            # (reset done above; no reset after measure needed)

        # --- Z stabilizers: data -> ancilla (CNOTs), measure, reset ancilla
        for s, plaq in enumerate(PLAQS):
            a = Z_START + s
            qc.reset(qreg[a])
            for (row, col) in plaq:
                qc.cx(qreg[d_idx(row, col)], qreg[a])
            qc.measure(qreg[a], syn[N_X + s])  # Z syndrome bit s

    return qc