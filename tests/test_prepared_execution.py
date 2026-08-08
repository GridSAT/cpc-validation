from __future__ import annotations

import pytest

from src.prepared_execution import PreparedExecution


def test_prepared_execution_preserves_fields() -> None:
    prepared = PreparedExecution(
        backend_id="rc",
        backend_version="1",
        payload="netlist",
        interface=(
            ("readout_node", "vout"),
        ),
        decoder_specification=(
            ("threshold_voltage", 2.5),
        ),
        metadata=(
            ("preparation_id", "rc.ngspice-netlist.v1"),
        ),
    )

    assert prepared.backend_id == "rc"
    assert prepared.backend_version == "1"
    assert prepared.payload == "netlist"
    assert prepared.interface == (
        ("readout_node", "vout"),
    )
    assert prepared.decoder_specification == (
        ("threshold_voltage", 2.5),
    )
    assert prepared.metadata == (
        ("preparation_id", "rc.ngspice-netlist.v1"),
    )


@pytest.mark.parametrize(
    ("backend_id", "backend_version"),
    (
        ("", "1"),
        ("rc", ""),
    ),
)
def test_prepared_execution_requires_backend_identity(
    backend_id: str,
    backend_version: str,
) -> None:
    with pytest.raises(ValueError):
        PreparedExecution(
            backend_id=backend_id,
            backend_version=backend_version,
            payload="netlist",
            interface=(),
            decoder_specification=(),
        )


def test_prepared_execution_rejects_duplicate_metadata_keys() -> None:
    with pytest.raises(
        ValueError,
        match="metadata keys must be unique",
    ):
        PreparedExecution(
            backend_id="rc",
            backend_version="1",
            payload="netlist",
            interface=(),
            decoder_specification=(),
            metadata=(
                ("key", 1),
                ("key", 2),
            ),
        )


def test_prepared_execution_requires_sorted_metadata() -> None:
    with pytest.raises(
        ValueError,
        match="metadata keys must be sorted",
    ):
        PreparedExecution(
            backend_id="rc",
            backend_version="1",
            payload="netlist",
            interface=(),
            decoder_specification=(),
            metadata=(
                ("z", 1),
                ("a", 2),
            ),
        )


def test_prepared_execution_preserves_provenance() -> None:
    provenance = (
        ("element:0", object()),
    )

    prepared = PreparedExecution(
        backend_id="rc",
        backend_version="1",
        payload="netlist",
        interface=(),
        decoder_specification=(),
        provenance=provenance,
    )

    assert prepared.provenance is provenance
