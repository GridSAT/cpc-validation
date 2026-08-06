from __future__ import annotations

from pathlib import Path

from src.cnf import (
    CNFInstance,
    Clause,
    Literal,
)


def load_dimacs(
    path: str | Path,
) -> CNFInstance:
    """Load one DIMACS CNF file."""
    source_path = Path(path)

    if not source_path.is_file():
        raise FileNotFoundError(
            f"DIMACS file does not exist: {source_path}"
        )

    return parse_dimacs(
        source_path.read_text(encoding="utf-8")
    )


def parse_dimacs(
    text: str,
) -> CNFInstance:
    """Parse strict DIMACS CNF text into a CNFInstance."""
    header_seen = False
    variable_count = 0
    declared_clause_count = 0
    tokens: list[tuple[str, int]] = []

    for line_number, raw_line in enumerate(
        text.splitlines(),
        start=1,
    ):
        line = raw_line.strip()

        if not line or line.startswith("c"):
            continue

        if line.startswith("p"):
            if header_seen:
                raise ValueError(
                    "DIMACS input contains multiple headers"
                )

            parts = line.split()

            if len(parts) != 4 or parts[:2] != ["p", "cnf"]:
                raise ValueError(
                    f"invalid DIMACS header on line {line_number}"
                )

            variable_count = _nonnegative_integer(
                parts[2],
                "variable count",
            )
            declared_clause_count = _nonnegative_integer(
                parts[3],
                "clause count",
            )
            header_seen = True
            continue

        if not header_seen:
            raise ValueError(
                f"DIMACS content precedes header on line {line_number}"
            )

        tokens.extend(
            (token, line_number)
            for token in line.split()
        )

    if not header_seen:
        raise ValueError(
            "DIMACS input is missing a 'p cnf' header"
        )

    clauses: list[Clause] = []
    current_literals: list[Literal] = []

    for token, line_number in tokens:
        try:
            signed_literal = int(token)
        except ValueError as error:
            raise ValueError(
                f"invalid DIMACS integer {token!r} "
                f"on line {line_number}"
            ) from error

        if signed_literal == 0:
            clauses.append(
                Clause(
                    literals=tuple(current_literals)
                )
            )
            current_literals = []
            continue

        variable = abs(signed_literal)

        if variable > variable_count:
            raise ValueError(
                f"DIMACS literal {signed_literal} exceeds "
                f"declared variable count {variable_count}"
            )

        current_literals.append(
            Literal(
                variable=variable,
                negated=signed_literal < 0,
            )
        )

    if current_literals:
        raise ValueError(
            "DIMACS clause is missing terminating zero"
        )

    if len(clauses) != declared_clause_count:
        raise ValueError(
            "DIMACS clause count mismatch: "
            f"declared {declared_clause_count}, "
            f"parsed {len(clauses)}"
        )

    return CNFInstance(
        variable_count=variable_count,
        clauses=tuple(clauses),
    )


def _nonnegative_integer(
    token: str,
    description: str,
) -> int:
    try:
        value = int(token)
    except ValueError as error:
        raise ValueError(
            f"DIMACS {description} must be an integer"
        ) from error

    if value < 0:
        raise ValueError(
            f"DIMACS {description} must be non-negative"
        )

    return value
