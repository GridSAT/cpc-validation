from __future__ import annotations

import pytest

from src.observable_execution import ObservableExecution


def test_observable_execution_preserves_observations() -> None:
    result = ObservableExecution(
        backend_id="rc",
        backend_version="1",
        observations=(
            ("vout", 4.9),
        ),
        metadata=(
            ("execution_id", "rc.ngspice-transient.v1"),
        ),
    )

    assert result.backend_id == "rc"
    assert result.backend_version == "1"

    assert dict(
        result.observations
    ) == {
        "vout": 4.9,
    }


def test_observable_execution_requires_backend_identity() -> None:
    with pytest.raises(ValueError):
        ObservableExecution(
            backend_id="",
            backend_version="1",
            observations=(),
        )


def test_observable_execution_rejects_duplicate_observations() -> None:
    with pytest.raises(
        ValueError,
        match="observation keys must be unique",
    ):
        ObservableExecution(
            backend_id="rc",
            backend_version="1",
            observations=(
                ("vout", 1.0),
                ("vout", 2.0),
            ),
        )


def test_observable_execution_requires_sorted_observations() -> None:
    with pytest.raises(
        ValueError,
        match="observation keys must be sorted",
    ):
        ObservableExecution(
            backend_id="rc",
            backend_version="1",
            observations=(
                ("z", 1),
                ("a", 2),
            ),
        )


def test_observable_execution_preserves_provenance() -> None:
    provenance = (
        ("element:0", object()),
    )

    observable = ObservableExecution(
        backend_id="rc",
        backend_version="1",
        observations=(),
        provenance=provenance,
    )

    assert observable.provenance is provenance
