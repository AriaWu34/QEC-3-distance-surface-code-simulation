from qec.syndrome import (
    split_into_rounds,
    parse_round_bits,
    defects_from_bits,
    spacetime_defects,
)


def test_parse_round_bits():
    xs, zs = parse_round_bits("10100110", n_x=4)

    assert xs == "1010"
    assert zs == "0110"


def test_defects_from_bits_empty():
    assert defects_from_bits("0000") == []


def test_defects_from_bits_nonempty():
    assert defects_from_bits("1010") == [0, 2]


def test_split_into_rounds_single():
    rounds = split_into_rounds(
        "00001111",
        k=1,
        n_stabilizers=8,
    )

    assert len(rounds) == 1
    assert rounds[0] == "11110000"


def test_split_into_rounds_d5():
    rounds = split_into_rounds(
        "0" * 64,
        k=2,
        n_stabilizers=32,
    )

    assert len(rounds) == 2
    assert all(len(r) == 32 for r in rounds)


def test_spacetime_defects_no_changes():
    defects_z, defects_x = spacetime_defects(
        "00000000 00000000",
        distance=3,
        k=2,
    )

    assert defects_z == []
    assert defects_x == []

def test_spacetime_defects_detect_change():
    defects_z, defects_x = spacetime_defects(
        "00000000 00010000",
        distance=3,
        k=2,
    )

    assert len(defects_z) > 0 or len(defects_x) > 0