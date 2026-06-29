from qec.legacy.simulation import logical_failure_rates_single 

def test_single_round_simulation_runs():
    fx, fz = logical_failure_rates_single(
        distance=3,
        shots=10,
    )

    assert 0.0 <= fx <= 1.0
    assert 0.0 <= fz <= 1.0