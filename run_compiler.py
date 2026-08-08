from __future__ import annotations

from pathlib import Path

from src.compiler import (
    DEFAULT_XOR_INSTANCE,
    compile_parity_instance,
)


def main() -> None:
    output_directory = Path("netlists/compiler")
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("CPC generic parity compiler")
    print()

    for x0 in (0, 1):
        for x3 in (0, 1):
            compiled = compile_parity_instance(
                DEFAULT_XOR_INSTANCE,
                {
                    0: x0,
                    3: x3,
                },
            )

            output_path = (
                output_directory
                / f"default_xor_{x0}_{x3}.cir"
            )

            output_path.write_text(
                compiled.netlist,
                encoding="utf-8",
            )

            statistics = compiled.statistics

            print(
                f"x0={x0} "
                f"x3={x3} "
                f"constraints={statistics.constraint_count} "
                f"variables={statistics.variable_count} "
                f"internal={statistics.internal_variable_count} "
                f"candidates={statistics.candidate_count} "
                f"sources={statistics.behavioral_source_count} "
                f"netlist={output_path}"
            )

    print()
    print("Generic parity compilation: PASS")


if __name__ == "__main__":
    main()
