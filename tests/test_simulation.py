from qec.simulation import logical_failure_rate_stim


def test_logical_failure_rate_stim_runs():
    rate = logical_failure_rate_stim(
        distance=3,
        rounds=3,
        shots=10,
        depolarizing_error=0.01,
    )

    assert 0.0 <= rate <= 1.0