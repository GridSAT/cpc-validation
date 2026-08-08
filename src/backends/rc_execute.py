from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from src.observable_execution import ObservableExecution
from src.prepared_execution import PreparedExecution
import src.spice_model as spice_model


RC_EXECUTION_ID = "rc.ngspice-transient.v1"


def execute_rc(
    prepared: PreparedExecution,
) -> ObservableExecution:
    """
    Execute one RFC-0004 prepared RC computation.

    Execution consumes only PreparedExecution.

    No CCIR program, ExecutionArtifact, boundary assignment, reference
    evaluator, or semantic expected result participates in this stage.
    """

    if prepared.backend_id != "rc":
        raise ValueError(
            "RC execution requires an RC prepared execution"
        )

    if not isinstance(
        prepared.payload,
        str,
    ):
        raise ValueError(
            "RC prepared execution payload must be an ngspice netlist string"
        )

    interface = dict(
        prepared.interface
    )

    readout_node = interface.get(
        "readout_node"
    )

    if readout_node != "vout":
        raise ValueError(
            "RC execution requires admitted readout node 'vout'"
        )

    with TemporaryDirectory(
        prefix="cpc-rc-execution-"
    ) as directory:
        root = Path(directory)

        netlist_path = (
            root / "execution.cir"
        )

        log_path = (
            root / "execution.log"
        )

        netlist_path.write_text(
            prepared.payload,
            encoding="utf-8",
        )

        spice_model._run_ngspice(
            netlist_path,
            log_path,
        )

        output_voltage = (
            spice_model._read_measured_voltage(
                log_path
            )
        )

    return ObservableExecution(
        backend_id=prepared.backend_id,
        backend_version=prepared.backend_version,
        observations=(
            (
                "vout",
                output_voltage,
            ),
        ),
        provenance=prepared.provenance,
        metadata=(
            (
                "execution_id",
                RC_EXECUTION_ID,
            ),
        ),
    )
