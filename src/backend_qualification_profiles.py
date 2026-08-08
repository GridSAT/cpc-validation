from __future__ import annotations

from typing import Mapping

from src.backend_qualification import (
    BackendConformance,
    BackendExecutionProfile,
    BackendQualificationManifest,
    manifest_from_summary,
)
from src.backends.digital_ccir import (
    DIGITAL_SPECIFICATION,
)
from src.backends.digital_execute import (
    DIGITAL_EXECUTION_ID,
)
from src.backends.digital_prepare import (
    DIGITAL_PREPARATION_ID,
)
from src.backends.fpga_ccir import (
    FPGA_SPECIFICATION,
)
from src.backends.fpga_execute import (
    FPGA_EXECUTION_ID,
)
from src.backends.fpga_prepare import (
    FPGA_PREPARATION_ID,
)
from src.backends.rc_ccir import (
    RC_SPECIFICATION,
)
from src.backends.rc_execute import (
    RC_EXECUTION_ID,
)


RC_PREPARATION_ID = "rc.ngspice-netlist.v1"

DIGITAL_EXECUTION_ENGINE = (
    "python-digital-interpreter"
)

DIGITAL_EXECUTION_ENGINE_VERSION = "1"

RC_EXECUTION_ENGINE = "ngspice"

FPGA_EXECUTION_ENGINE = "iverilog/vvp"


REFERENCE_BACKEND_CONFORMANCE = BackendConformance(
    rfc0003=True,
    rfc0004=True,
    rfc0005_eligible=True,
    rfc0006_qualified=True,
    answer_independence=True,
    provenance_support=True,
)


def build_rc_qualification_manifest(
    *,
    execution_engine_version: str,
    summary: Mapping[str, object] | None = None,
) -> BackendQualificationManifest:
    """
    Construct the qualification manifest for the RC reference backend.

    The ngspice version is supplied from the actual execution environment
    rather than fixed by the backend specification.
    """

    execution = BackendExecutionProfile(
        preparation_id=RC_PREPARATION_ID,
        execution_id=RC_EXECUTION_ID,
        execution_engine=RC_EXECUTION_ENGINE,
        execution_engine_version=(
            execution_engine_version
        ),
    )

    return manifest_from_summary(
        specification=RC_SPECIFICATION,
        execution=execution,
        conformance=REFERENCE_BACKEND_CONFORMANCE,
        summary=summary,
    )


def build_digital_qualification_manifest(
    *,
    summary: Mapping[str, object] | None = None,
) -> BackendQualificationManifest:
    """
    Construct the qualification manifest for the deterministic digital
    reference backend.
    """

    execution = BackendExecutionProfile(
        preparation_id=DIGITAL_PREPARATION_ID,
        execution_id=DIGITAL_EXECUTION_ID,
        execution_engine=(
            DIGITAL_EXECUTION_ENGINE
        ),
        execution_engine_version=(
            DIGITAL_EXECUTION_ENGINE_VERSION
        ),
    )

    return manifest_from_summary(
        specification=DIGITAL_SPECIFICATION,
        execution=execution,
        conformance=REFERENCE_BACKEND_CONFORMANCE,
        summary=summary,
    )

def build_fpga_qualification_manifest(
    *,
    execution_engine_version: str,
    summary: Mapping[str, object] | None = None,
) -> BackendQualificationManifest:
    """
    Construct the qualification manifest for the FPGA reference backend.

    The Icarus Verilog execution-engine version is supplied from the actual
    execution environment rather than fixed by the backend specification.
    """

    execution = BackendExecutionProfile(
        preparation_id=FPGA_PREPARATION_ID,
        execution_id=FPGA_EXECUTION_ID,
        execution_engine=FPGA_EXECUTION_ENGINE,
        execution_engine_version=(
            execution_engine_version
        ),
    )

    return manifest_from_summary(
        specification=FPGA_SPECIFICATION,
        execution=execution,
        conformance=REFERENCE_BACKEND_CONFORMANCE,
        summary=summary,
    )
