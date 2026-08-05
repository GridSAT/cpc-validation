from __future__ import annotations

import argparse
from pathlib import Path

from src.ir import (
    IRConstraint,
    IRInterface,
    IRProgram,
    enumerate_ir_candidates,
)


def build_default_program(
    x0: int,
    x3: int,
) -> IRProgram:
    for name, value in (
        ("x0", x0),
        ("x3", x3),
    ):
        if value not in (0, 1):
            raise ValueError(
                f"{name} must be 0 or 1"
            )

    return IRProgram(
        name=f"default-xor-boundary-{x0}-{x3}",
        constraints=(
            IRConstraint(
                variables=(0, 1, 2),
                parity=0,
            ),
            IRConstraint(
                variables=(1, 2, 3),
                parity=1,
            ),
        ),
        boundary_variables=(0, 3),
        internal_variables=(1, 2),
        boundary_assignment=(
            (0, x0),
            (3, x3),
        ),
        candidates=enumerate_ir_candidates(
            (1, 2)
        ),
        interface=IRInterface(),
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect the backend-independent CPC "
            "intermediate representation."
        )
    )

    parser.add_argument(
        "--x0",
        type=int,
        choices=(0, 1),
        default=0,
    )

    parser.add_argument(
        "--x3",
        type=int,
        choices=(0, 1),
        default=1,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional JSON output path.",
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    program = build_default_program(
        arguments.x0,
        arguments.x3,
    )

    print("CPC backend-independent IR")
    print()
    print(program.pretty())

    if arguments.output is not None:
        program.write_json(
            arguments.output
        )

        print()
        print(
            f"IR JSON: {arguments.output}"
        )

    print()
    print(
        "Intermediate representation: PASS"
    )


if __name__ == "__main__":
    main()
