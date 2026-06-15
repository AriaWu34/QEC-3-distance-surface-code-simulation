from qec.decoder import (
    mwpm_pairs,
    correction_spans_code,
)


def test_empty_matching_vertical():
    assert mwpm_pairs([], "vertical", distance=3) == []


def test_empty_matching_horizontal():
    assert mwpm_pairs([], "horizontal", distance=3) == []


def test_no_span_empty_vertical():
    assert correction_spans_code(
        [],
        boundary_mode="vertical",
        distance=3,
    ) is False


def test_no_span_empty_horizontal():
    assert correction_spans_code(
        [],
        boundary_mode="horizontal",
        distance=3,
    ) is False


def test_single_defect_matches_boundary():
    pairs = mwpm_pairs(
        [0],
        "vertical",
        distance=3,
    )

    assert len(pairs) == 1

    u, v = pairs[0]

    assert "B" in (u, v)


def test_two_defects_match_together():
    pairs = mwpm_pairs(
        [0, 1],
        "vertical",
        distance=3,
    )

    assert len(pairs) == 1

    u, v = pairs[0]

    assert "B" not in (u, v)


def test_span_detection_vertical():
    pairs = [("a0", "a2")]

    assert correction_spans_code(
        pairs,
        boundary_mode="vertical",
        distance=3,
    ) is False


def test_mwpm_pairs_distance_5():
    pairs = mwpm_pairs(
        [0],
        "vertical",
        distance=5,
    )

    assert len(pairs) == 1

    u, v = pairs[0]

    assert "B" in (u, v)