from __future__ import annotations

import pytest

from src.dimacs import (
    load_dimacs,
    parse_dimacs,
)


def test_parse_dimacs() -> None:
    instance = parse_dimacs(
        """
        c Example
        p cnf 3 2
        1 -2 3 0
        2 0
        """
    )

    assert instance.variable_count == 3
    assert len(instance.clauses) == 2
    assert instance.clauses[0].literals[1].variable == 2
    assert instance.clauses[0].literals[1].negated is True


def test_comments_blank_lines_and_split_clause() -> None:
    instance = parse_dimacs(
        """
        c first comment

        p cnf 3 1
        1
        c embedded comment
        -2 3 0
        """
    )

    assert len(instance.clauses) == 1
    assert len(instance.clauses[0].literals) == 3


def test_multiple_clauses_on_one_line() -> None:
    instance = parse_dimacs(
        "p cnf 2 2\n1 0 -2 0\n"
    )

    assert len(instance.clauses) == 2


def test_empty_formula() -> None:
    instance = parse_dimacs(
        "p cnf 0 0\n"
    )

    assert instance.variable_count == 0
    assert instance.clauses == ()


def test_empty_clause() -> None:
    instance = parse_dimacs(
        "p cnf 0 1\n0\n"
    )

    assert len(instance.clauses) == 1
    assert instance.clauses[0].literals == ()


def test_load_dimacs(tmp_path) -> None:
    path = tmp_path / "example.cnf"
    path.write_text(
        "p cnf 1 1\n1 0\n",
        encoding="utf-8",
    )

    instance = load_dimacs(path)

    assert instance.variable_count == 1


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("", "missing"),
        ("1 0", "precedes header"),
        ("p sat 1 1\n1 0", "invalid DIMACS header"),
        ("p cnf -1 0", "must be non-negative"),
        ("p cnf 1 1\nx 0", "invalid DIMACS integer"),
        ("p cnf 1 1\n2 0", "exceeds"),
        ("p cnf 1 1\n1", "missing terminating zero"),
        ("p cnf 1 2\n1 0", "clause count mismatch"),
        ("p cnf 1 0\np cnf 1 0", "multiple headers"),
    ],
)
def test_invalid_dimacs_rejected(
    text: str,
    message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=message,
    ):
        parse_dimacs(text)


def test_missing_file_rejected(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        load_dimacs(
            tmp_path / "missing.cnf"
        )
