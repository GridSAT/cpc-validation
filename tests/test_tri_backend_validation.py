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
