from __future__ import annotations

import pytest

from src.backends.rc_ccir import (
    RCBackend,
    RC_SPECIFICATION,
)
from src.backends.rc_prepare import (
    prepare_rc_netlist,
)
from src.ccir import (
    CCIRConstraint,
    CCIRProgram,
)
from src.ccir_parity import (
    CCIRParityPayload,
)
from src.compile_backend import (
    compile_backend,
)


def _programs() -> tuple[CCIRProgram, ...]:
    return (
        CCIRProgram(
            name="single-parity",
            variable_count=3,
            boundary_variables=(0, 2),
            constraints=(
                CCIRConstraint(
                    family="parity",
                    payload=CCIRParityPayload(
                        variables=(0, 1, 2),
                        parity=0,
                    ),
                ),
            ),
        ),
        CCIRProgram(
            name="double-parity",
            variable_count=4,
            boundary_variables=(0, 3),
            constraints=(
                CCIRConstraint(
                    family="parity",
                    payload=CCIRParityPayload(
                        variables=(0, 1, 2),
                        parity=0,
                    ),
                ),
                CCIRConstraint(
                    family="parity",
                    payload=CCIRParityPayload(
                        variables=(1, 2, 3),
                        parity=1,
                    ),
                ),
            ),
        ),
        CCIRProgram(
            name="parity-chain",
            variable_count=5,
            boundary_variables=(0, 4),
            constraints=(
                CCIRConstraint(
                    family="parity",
                    payload=CCIRParityPayload(
                        variables=(0, 1),
                        parity=1,
                    ),
                ),
                CCIRConstraint(
                    family="parity",
                    payload=CCIRParityPayload(
                        variables=(1, 2, 3),
                        parity=0,
                    ),
                ),
                CCIRConstraint(
                    family="parity",
                    payload=CCIRParityPayload(
                        variables=(3, 4),
                        parity=1,
                    ),
                ),
            ),
        ),
    )


def _boundary_assignments(
    program: CCIRProgram,
) -> tuple[dict[int, int], ...]:
    if len(program.boundary_variables) != 2:
        raise AssertionError(
            "audit fixture expects exactly two boundary variables"
        )

    first, second = program.boundary_variables

    return (
        {
            first: 0,
            second: 0,
        },
        {
            first: 0,
            second: 1,
        },
        {
            first: 1,
            second: 0,
        },
        {
            first: 1,
            second: 1,
        },
    )


@pytest.mark.parametrize(
    "program",
    _programs(),
    ids=lambda program: program.name,
)
def test_generated_netlists_contain_no_semantic_oracle_fields(
    program: CCIRProgram,
) -> None:
    artifact = compile_backend(
        program,
        RCBackend(),
    )

    forbidden = (
        "expected=",
        "expected_continuation",
        "continuation_value",
        "completion_count",
        "completion_table",
        "satisfying_assignments",
        "reference_answer",
        "decoded=",
    )

    for boundary_values in _boundary_assignments(
        program
    ):
        netlist, _ = prepare_rc_netlist(
            program,
            artifact,
            boundary_values,
            RC_SPECIFICATION,
        )

        lowered = netlist.lower()

        for term in forbidden:
            assert term not in lowered


@pytest.mark.parametrize(
    "program",
    _programs(),
    ids=lambda program: program.name,
)
def test_external_reference_output_cannot_change_generated_netlist(
    program: CCIRProgram,
) -> None:
    artifact = compile_backend(
        program,
        RCBackend(),
    )

    boundary_values = _boundary_assignments(
        program
    )[0]

    baseline, _ = prepare_rc_netlist(
        program,
        artifact,
        boundary_values,
        RC_SPECIFICATION,
    )

    for external_reference in (
        None,
        0,
        1,
        "corrupted",
    ):
        reference_output = external_reference

        repeated, _ = prepare_rc_netlist(
            program,
            artifact,
            boundary_values,
            RC_SPECIFICATION,
        )

        assert reference_output is external_reference
        assert repeated == baseline


@pytest.mark.parametrize(
    "program",
    _programs(),
    ids=lambda program: program.name,
)
def test_generated_netlist_is_reproducible(
    program: CCIRProgram,
) -> None:
    first_artifact = compile_backend(
        program,
        RCBackend(),
    )

    second_artifact = compile_backend(
        program,
        RCBackend(),
    )

    assert first_artifact == second_artifact

    for boundary_values in _boundary_assignments(
        program
    ):
        first_netlist, first_statistics = prepare_rc_netlist(
            program,
            first_artifact,
            boundary_values,
            RC_SPECIFICATION,
        )

        second_netlist, second_statistics = prepare_rc_netlist(
            program,
            second_artifact,
            boundary_values,
            RC_SPECIFICATION,
        )

        assert first_netlist == second_netlist
        assert first_statistics == second_statistics


@pytest.mark.parametrize(
    "program",
    _programs(),
    ids=lambda program: program.name,
)
def test_boundary_preparation_does_not_mutate_compiled_artifact(
    program: CCIRProgram,
) -> None:
    artifact = compile_backend(
        program,
        RCBackend(),
    )

    baseline = artifact

    for boundary_values in _boundary_assignments(
        program
    ):
        prepare_rc_netlist(
            program,
            artifact,
            boundary_values,
            RC_SPECIFICATION,
        )

        assert artifact == baseline
