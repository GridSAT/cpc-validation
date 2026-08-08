from __future__ import annotations

from pathlib import Path

import pytest

from src.backends.rc_execute import (
    RC_EXECUTION_ID,
    execute_rc,
)
from src.observable_execution import ObservableExecution
from src.prepared_execution import PreparedExecution


def _prepared() -> PreparedExecution:
    return PreparedExecution(
        backend_id="rc",
        backend_version="1",
        payload="* test netlist\n.end\n",
        interface=(
            ("readout_node", "vout"),
            ("threshold_voltage", 2.5),
        ),
        decoder_specification=(
            ("threshold_voltage", 2.5),
        ),
        metadata=(
            ("preparation_id", "rc.ngspice-netlist.v1"),
        ),
    )


def test_execute_rc_consumes_prepared_execution_only(
    monkeypatch,
) -> None:
    import src.spice_model

    seen_netlist = {}

    def fake_run(
        netlist_path: Path,
        log_path: Path,
    ) -> None:
        seen_netlist["text"] = (
            netlist_path.read_text(
                encoding="utf-8"
            )
        )

        log_path.write_text(
            "fake",
            encoding="utf-8",
        )

    def fake_read(
        log_path: Path,
    ) -> float:
        assert log_path.read_text(
            encoding="utf-8"
        ) == "fake"

        return 4.75

    monkeypatch.setattr(
        src.spice_model,
        "_run_ngspice",
        fake_run,
    )

    monkeypatch.setattr(
        src.spice_model,
        "_read_measured_voltage",
        fake_read,
    )

    monkeypatch.setattr(
        src.spice_model,
        "_ngspice_version",
        lambda: "ngspice-42",
    )

    result = execute_rc(
        _prepared()
    )

    assert isinstance(
        result,
        ObservableExecution,
    )

    assert seen_netlist["text"] == (
        "* test netlist\n.end\n"
    )

    assert dict(
        result.observations
    ) == {
        "vout": 4.75,
    }

    assert dict(
        result.metadata
    ) == {
        "execution_engine": "ngspice",
        "execution_engine_version": "ngspice-42",
        "execution_id": RC_EXECUTION_ID,
    }


def test_execute_rc_rejects_wrong_backend() -> None:
    prepared = PreparedExecution(
        backend_id="other",
        backend_version="1",
        payload="netlist",
        interface=(
            ("readout_node", "vout"),
        ),
        decoder_specification=(),
    )

    with pytest.raises(
        ValueError,
        match="requires an RC prepared execution",
    ):
        execute_rc(
            prepared
        )


def test_execute_rc_rejects_non_string_payload() -> None:
    prepared = PreparedExecution(
        backend_id="rc",
        backend_version="1",
        payload=object(),
        interface=(
            ("readout_node", "vout"),
        ),
        decoder_specification=(),
    )

    with pytest.raises(
        ValueError,
        match="payload must be an ngspice netlist string",
    ):
        execute_rc(
            prepared
        )


def test_execute_rc_enforces_admitted_readout() -> None:
    prepared = PreparedExecution(
        backend_id="rc",
        backend_version="1",
        payload="netlist",
        interface=(
            ("readout_node", "hidden_node"),
        ),
        decoder_specification=(),
    )

    with pytest.raises(
        ValueError,
        match="admitted readout node 'vout'",
    ):
        execute_rc(
            prepared
        )
