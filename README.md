# Quantum Error Correction Surface Code Simulator

A modular quantum error correction (QEC) simulator for studying planar surface codes using Stim and PyMatching. The project provides tools for constructing surface-code circuits, generating detector error models (DEMs), performing Minimum Weight Perfect Matching (MWPM) decoding, and evaluating logical failure rates through Monte Carlo simulation.

The simulator is designed as a modular research platform that can be extended with alternative decoders, noise models, and future threshold studies.

---

## Features

- Configurable odd code distances (`d = 3, 5, 7, ...`)
- Multi-round syndrome extraction
- Stim-based circuit generation
- Detector Error Model (DEM) generation
- PyMatching MWPM decoder
- Depolarising and readout noise models
- X- and Z-memory experiments
- Logical failure-rate simulations
- Distance-scaling experiments
- Modular package structure with unit tests

---

## Repository Structure

```text
src/qec/
├── geometry.py
├── circuit.py
├── syndrome.py
├── noise.py
├── simulation.py
├── visualization.py
├── stim_backend.py
└── decoders/
    ├── base.py
    └── mwpm.py

experiments/
├── compare_decoders.py
└── logical_failure_stim.py

results/
├── comparison/
└── logical_failure/
    ├── X/
    └── Z/

tests/
├── test_geometry.py
├── test_circuit.py
├── test_syndrome.py
├── test_decoder.py
├── test_simulation.py
└── test_stim_pymatching.py

notebooks/
├── demo.ipynb
├── repetition-code-simulation.ipynb
└── 3-distance-surface-code.ipynb
```

---

## Example Experiment

### Decoder Comparison

```bash
python experiments/compare_decoders.py
```

Generates:

```text
results/comparison/decoder_comparison.png
```

### Logical Failure-Rate Experiment

```bash
python experiments/logical_failure_stim.py
```

Runs logical memory experiments for both **X** and **Z** memory bases across multiple code distances and produces logical failure-rate and distance-scaling plots.

---

## Example Result

### Decoder Comparison

![Decoder Comparison](results/comparison/decoder_comparison.png)

### Logical Failure Rate (Z Memory)

![Logical Failure](results/logical_failure/Z/distance_scaling.png)

---

## Current Limitation

The current implementation uses a simplified checkerboard stabilizer layout. While the complete **Stim → DEM → PyMatching** pipeline is operational, the geometry does not yet implement the boundary structure of a full planar surface code. Consequently, the expected reduction in logical error rate with increasing code distance has not yet been achieved.

The next development milestone is implementing proper planar surface-code geometry with boundary stabilizers and validating distance scaling.

---

## Future Work

- Planar surface-code geometry
- Boundary stabilizers
- Threshold analysis
- Decoder benchmarking
- GitHub Actions CI

---

## Testing

Run the complete test suite:

```bash
pytest
```

---

## Requirements

- Python 3.10+
- Stim
- PyMatching
- NumPy
- Matplotlib
- Pytest

Install dependencies:

```bash
pip install qiskit stim pymatching numpy networkx matplotlib pytest
```
