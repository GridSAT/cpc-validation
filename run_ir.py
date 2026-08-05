from __future__ import annotations

import argparse
from pathlib import Path

from src.compiler import DEFAULT_XOR_INSTANCE
from src.ir_compiler import (
    compile_parity_instance_to_ir,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compile and inspect the backend-independent "
            "CPC intermediate representation."
        )
    )

    parser.add_argument(
        "--x0",
        type=int,
        choices=(
            0,
            1,
        ),
        default=0,
    )

    parser.add_argument(
        "--x3",
        type=int,
        choices=(
            0,
            1,
        ),
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

    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        {
            0: arguments.x0,
            3: arguments.x3,
        },
        name=(
            "default-xor-"
            f"boundary-{arguments.x0}-{arguments.x3}"
        ),
    )

    print("CPC compiler-to-IR inspection")
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
        "Compiler-to-IR translation: PASS"
    )


if __name__ == "__main__":
    main()
