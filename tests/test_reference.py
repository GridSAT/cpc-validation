# python test_reference.py

from src.reference import build_initial_system


def test_initial_continuation_table() -> None:
    system = build_initial_system()

    expected = {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 1,
        (1, 1): 0,
    }

    for boundary_values, expected_value in expected.items():
        boundary = {
            0: boundary_values[0],
            3: boundary_values[1],
        }

        assert system.evaluate(boundary) == expected_value


def test_satisfying_boundaries_have_two_internal_completions() -> None:
    system = build_initial_system()

    assert len(system.completions({0: 0, 3: 1})) == 2
    assert len(system.completions({0: 1, 3: 0})) == 2


def test_obstructed_boundaries_have_no_completion() -> None:
    system = build_initial_system()

    assert system.completions({0: 0, 3: 0}) == []
    assert system.completions({0: 1, 3: 1}) == []