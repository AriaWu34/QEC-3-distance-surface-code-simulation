from qec.syndrome import (
    split_into_rounds,
    parse_round_bits,
    defects_from_bits,
    spacetime_defects,
)


def test_parse_round_bits():
    xs, zs = parse_round_bits("10100110")
    assert xs == "1010"
    assert zs == "0110"


def test_defects_from_bits_empty():
    assert defects_from_bits("0000") == []


def test_defects_from_bits_nonempty():
    assert defects_from_bits("1010") == [0, 2]


def test_split_into_rounds_single():
    rounds = split_into_rounds("00001111", k=1)
    assert len(rounds) == 1
    assert rounds[0] == "11110000"  # reversed because of Qiskit bit ordering


def test_spacetime_defects_no_changes():
    defects_z, defects_x = spacetime_defects(
        "00000000 00000000",
        k=2,
    )

    assert defects_z == []
    assert defects_x == []