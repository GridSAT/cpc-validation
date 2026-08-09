from __future__ import annotations

import ast
from pathlib import Path

import pytest

from src.backends.fpga_execute import (
    FPGA_EXECUTION_ID,
    _extract_result_bit,
    execute_fpga,
)
from src.observable_execution import ObservableExecution
from src.prepared_execution import PreparedExecution


def _prepared(
    result: int = 1,
) -> PreparedExecution:
    source = f"""
module cpc_fpga_execution(
    output wire result
);
    assign result = 1'b{result};

    initial begin
        #1;
        $display("CPC_RESULT=%b", result);
        $finish;
    end
endmodule
"""

    return PreparedExecution(
        backend_id="fpga",
        backend_version="1",
        payload=source,
        interface=(
            (
                "readout_signal",
                "result",
            ),
        ),
        decoder_specification=(
            (
                "readout_signal",
                "result",
            ),
        ),
        metadata=(
            (
                "preparation_id",
                "fpga.verilog.v1",
            ),
        ),
    )


@pytest.mark.parametrize(
    (
        "value",
        "expected",
    ),
    (
        (0, 0),
        (1, 1),
    ),
)
def test_execute_fpga_runs_icarus_verilog(
    value: int,
    expected: int,
) -> None:
    observable = execute_fpga(
        _prepared(value)
    )

    assert isinstance(
        observable,
        ObservableExecution,
    )

    assert observable.observations == (
        (
            "result_bit",
            expected,
        ),
    )

    metadata = dict(
        observable.metadata
    )

    assert metadata[
        "execution_engine"
    ] == "iverilog/vvp"

    assert metadata[
        "execution_engine_version"
    ]

    assert metadata[
        "execution_id"
    ] == FPGA_EXECUTION_ID


def test_execute_fpga_preserves_identity_and_provenance() -> None:
    prepared = PreparedExecution(
        backend_id="fpga",
        backend_version="1",
        payload="""
module cpc_fpga_execution(output wire result);
assign result = 1'b1;
initial begin
#1;
$display("CPC_RESULT=%b", result);
$finish;
end
endmodule
""",
        interface=(
            ("readout_signal", "result"),
        ),
        decoder_specification=(
            ("readout_signal", "result"),
        ),
        provenance=(
            ("fpga.test", "origin"),
        ),
    )

    observable = execute_fpga(
        prepared
    )

    assert observable.backend_id == "fpga"
    assert observable.backend_version == "1"
    assert observable.provenance == prepared.provenance


def test_execute_fpga_rejects_wrong_backend() -> None:
    prepared = PreparedExecution(
        backend_id="digital",
        backend_version="1",
        payload="",
        interface=(),
        decoder_specification=(),
    )

    with pytest.raises(
        ValueError,
        match="requires an FPGA prepared execution",
    ):
        execute_fpga(
            prepared
        )


def test_execute_fpga_rejects_non_string_payload() -> None:
    prepared = PreparedExecution(
        backend_id="fpga",
        backend_version="1",
        payload=(),
        interface=(
            ("readout_signal", "result"),
        ),
        decoder_specification=(),
    )

    with pytest.raises(
        ValueError,
        match="payload must be Verilog source",
    ):
        execute_fpga(
            prepared
        )


def test_execute_fpga_enforces_admitted_readout() -> None:
    prepared = PreparedExecution(
        backend_id="fpga",
        backend_version="1",
        payload="",
        interface=(
            ("readout_signal", "hidden"),
        ),
        decoder_specification=(),
    )

    with pytest.raises(
        ValueError,
        match="admitted readout signal 'result'",
    ):
        execute_fpga(
            prepared
        )


@pytest.mark.parametrize(
    "text",
    (
        "",
        "ordinary output\n",
    ),
)
def test_extract_result_requires_observation(
    text: str,
) -> None:
    with pytest.raises(
        RuntimeError,
        match="no CPC_RESULT",
    ):
        _extract_result_bit(
            text
        )


@pytest.mark.parametrize(
    "text",
    (
        "CPC_RESULT=x\n",
        "CPC_RESULT=z\n",
        "CPC_RESULT=2\n",
        "CPC_RESULT=\n",
    ),
)
def test_extract_result_rejects_malformed_observation(
    text: str,
) -> None:
    with pytest.raises(
        RuntimeError,
        match="malformed CPC_RESULT",
    ):
        _extract_result_bit(
            text
        )


def test_extract_result_rejects_multiple_observations() -> None:
    with pytest.raises(
        RuntimeError,
        match="multiple CPC_RESULT",
    ):
        _extract_result_bit(
            "CPC_RESULT=1\nCPC_RESULT=1\n"
        )


def test_fpga_execution_module_has_no_semantic_reference_dependency() -> None:
    path = Path(
        "src/backends/fpga_execute.py"
    )

    tree = ast.parse(
        path.read_text(
            encoding="utf-8"
        )
    )

    forbidden_modules = {
        "src.ccir",
        "src.ccir_reference",
        "src.generic_reference",
        "src.physical_validation",
    }

    imports = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            imports.update(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if node.module is not None:
                imports.add(
                    node.module
                )

    assert forbidden_modules.isdisjoint(
        imports
    )
