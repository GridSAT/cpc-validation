from __future__ import annotations

import pytest

from src.ccir_lower_parity import (
    lower_parity_instance_to_ccir,
)
from src.compiler import (
    DEFAULT_XOR_INSTANCE,
)
from src.tri_backend_validation import (
    validate_tri_backend,
)


@pytest.mark.parametrize(
    (
        "x0",
        "x3",
        "expected",
    ),
    (
        (0, 0, 0),
        (0, 1, 1),
        (1, 0, 1),
        (1, 1, 0),
    ),
)
def test_default_xor_passes_tri_backend_validation(
    x0: int,
    x3: int,
    expected: int,
) -> None:
    program = lower_parity_instance_to_ccir(
        DEFAULT_XOR_INSTANCE
    )

    result = validate_tri_backend(
        program,
        {
            0: x0,
            3: x3,
        },
    )

    assert result.rc_decoded == expected
    assert result.digital_decoded == expected
    assert result.fpga_decoded == expected
    assert result.reference == expected

    assert result.backend_agreement
    assert result.rc_semantic_match
    assert result.digital_semantic_match
    assert result.fpga_semantic_match
    assert result.overall_pass


def test_tri_backend_result_records_separate_conditions() -> None:
    program = lower_parity_instance_to_ccir(
        DEFAULT_XOR_INSTANCE
    )

    result = validate_tri_backend(
        program,
        {
            0: 0,
            3: 1,
        },
    )

    assert isinstance(
        result.backend_agreement,
        bool,
    )

    assert isinstance(
        result.rc_semantic_match,
        bool,
    )

    assert isinstance(
        result.digital_semantic_match,
        bool,
    )

    assert isinstance(
        result.fpga_semantic_match,
        bool,
    )

    assert isinstance(
        result.overall_pass,
        bool,
    )


def test_tri_backend_result_retains_execution_records() -> None:
    program = lower_parity_instance_to_ccir(
        DEFAULT_XOR_INSTANCE
    )

    result = validate_tri_backend(
        program,
        {
            0: 0,
            3: 1,
        },
    )

    assert result.rc.prepared.backend_id == "rc"
    assert result.digital.prepared.backend_id == "digital"
    assert result.fpga.prepared.backend_id == "fpga"

    assert result.rc.observable.backend_id == "rc"
    assert result.digital.observable.backend_id == "digital"
    assert result.fpga.observable.backend_id == "fpga"

    assert result.rc.decoded == 1
    assert result.digital.decoded == 1
    assert result.fpga.decoded == 1


def test_tri_backend_execution_metadata_identifies_actual_engines() -> None:
    program = lower_parity_instance_to_ccir(
        DEFAULT_XOR_INSTANCE
    )

    result = validate_tri_backend(
        program,
        {
            0: 0,
            3: 1,
        },
    )

    rc_metadata = dict(
        result.rc.observable.metadata
    )

    digital_metadata = dict(
        result.digital.observable.metadata
    )

    fpga_metadata = dict(
        result.fpga.observable.metadata
    )

    assert rc_metadata["execution_engine"] == "ngspice"

    assert (
        digital_metadata["execution_engine"]
        == "python-digital-interpreter"
    )

    assert (
        fpga_metadata["execution_engine"]
        == "iverilog/vvp"
    )

    assert rc_metadata["execution_engine_version"]
    assert digital_metadata["execution_engine_version"]
    assert fpga_metadata["execution_engine_version"]
