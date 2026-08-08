from __future__ import annotations

from itertools import product

from src.observable_execution import ObservableExecution
from src.prepared_execution import PreparedExecution


DIGITAL_EXECUTION_ID = "digital.deterministic-enumeration.v1"


def execute_digital(
    prepared: PreparedExecution,
) -> ObservableExecution:
    """
    Execute one RFC-0005 prepared deterministic digital computation.

    Execution consumes only PreparedExecution.

    No CCIR program, ExecutionArtifact, source representation,
    reference evaluator, or expected semantic result participates
    in this stage.
    """

    if prepared.backend_id != "digital":
        raise ValueError(
            "digital execution requires a digital prepared execution"
        )

    if not isinstance(
        prepared.payload,
        tuple,
    ):
        raise ValueError(
            "digital prepared execution payload must be immutable tuple data"
        )

    payload = dict(
        prepared.payload
    )

    if "boundary_values" not in payload:
        raise ValueError(
            "digital prepared execution requires boundary_values"
        )

    if "program" not in payload:
        raise ValueError(
            "digital prepared execution requires compiled program"
        )

    boundary_values = dict(
        payload["boundary_values"]
    )

    program = tuple(
        payload["program"]
    )

    result = _execute_instruction_program(
        program,
        boundary_values,
    )

    return ObservableExecution(
        backend_id=prepared.backend_id,
        backend_version=prepared.backend_version,
        observations=(
            (
                "result_bit",
                result,
            ),
        ),
        provenance=prepared.provenance,
        metadata=(
            (
                "execution_engine",
                "python-digital-interpreter",
            ),
            (
                "execution_engine_version",
                "1",
            ),
            (
                "execution_id",
                DIGITAL_EXECUTION_ID,
            ),
        ),
    )


def _execute_instruction_program(
    program: tuple[tuple[str, object], ...],
    boundary_values: dict[int, int],
) -> int:
    parity_instructions: list[
        tuple[
            tuple[int, ...],
            int,
        ]
    ] = []

    variables: set[int] = set()

    for _, element in program:
        if not isinstance(
            element,
            tuple,
        ) or not element:
            continue

        element_type = element[0]

        if element_type == "variable-register":
            if len(element) != 2:
                raise ValueError(
                    "digital variable register topology is malformed"
                )
            variable = element[1]

            if not isinstance(
                variable,
                int,
            ):
                raise ValueError(
                    "digital variable register requires integer index"
                )

            variables.add(
                variable
            )

        elif element_type == "parity-instruction":
            continue

        elif element_type in {
            "boundary-port",
            "existential-reduction",
            "result-register",
            "readout",
        }:
            continue

    for _, element in program:
        if not isinstance(
            element,
            tuple,
        ) or not element:
            continue

        if element[0] != "parity-instruction":
            continue

        if len(element) != 3:
            raise ValueError(
                "digital parity instruction must contain "
                "variables and parity"
            )

        instruction_variables = element[1]
        parity = element[2]

        if not isinstance(
            instruction_variables,
            tuple,
        ):
            raise ValueError(
                "digital parity instruction variables must be a tuple"
            )

        if any(
            not isinstance(variable, int)
            for variable in instruction_variables
        ):
            raise ValueError(
                "digital parity instruction variables must be integers"
            )

        if isinstance(
            parity,
            bool,
        ) or parity not in (
            0,
            1,
        ):
            raise ValueError(
                "digital parity instruction parity must be 0 or 1"
            )

        parity_instructions.append(
            (
                instruction_variables,
                parity,
            )
        )

        variables.update(
            instruction_variables
        )

    internal_variables = tuple(
        variable
        for variable in sorted(
            variables
        )
        if variable not in boundary_values
    )

    for values in product(
        (0, 1),
        repeat=len(internal_variables),
    ):
        assignment = {
            **boundary_values,
            **dict(
                zip(
                    internal_variables,
                    values,
                    strict=True,
                )
            ),
        }

        satisfied = True

        for (
            instruction_variables,
            parity,
        ) in parity_instructions:
            value = 0

            for variable in instruction_variables:
                if variable not in assignment:
                    raise ValueError(
                        "digital instruction references "
                        f"unassigned variable {variable}"
                    )

                value ^= assignment[
                    variable
                ]

            if value != parity:
                satisfied = False
                break

        if satisfied:
            return 1

    return 0
