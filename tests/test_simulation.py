from qec.simulation import logical_failure_rates_single, logical_failure_rate_stim


def test_single_round_simulation_runs():
    fx, fz = logical_failure_rates_single(
        distance=3,
        shots=10,
    )

    assert 0.0 <= fx <= 1.0
    assert 0.0 <= fz <= 1.0


def test_logical_failure_rate_stim_runs():
    rate = logical_failure_rate_stim(
        distance=3,
        rounds=3,
        shots=10,
        depolarizing_error=0.01,
    )

    assert 0.0 <= rate <= 1.0